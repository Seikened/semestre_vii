"""Contrato entre precarga e inferencia: la galería de embeddings guardada en disco."""

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Self

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .embedding import TOLERANCIA_NORMA
from .pan import ClasePan

ARCHIVO_VECTORES = "galeria.npz"
ARCHIVO_MANIFIESTO = "manifiesto.json"


class ManifiestoGaleria(BaseModel):
    """Cómo se construyó la galería; la inferencia lo usa para no mezclar espacios de vectores."""

    model_config = ConfigDict(frozen=True)

    encoder: str
    dimension: int = Field(gt=0)
    k: int = Field(gt=0)
    umbral: float = Field(ge=-1, le=1)
    dataset: str
    instancias_por_clase: dict[ClasePan, int]
    omitidas: int = Field(ge=0)
    gris: bool  # Si los recortes se vectorizaron en escala de grises.
    exactitud_validacion: float = Field(ge=0, le=1)
    creada: datetime

    @property
    def clases(self) -> tuple[ClasePan, ...]:
        return tuple(self.instancias_por_clase)

    @property
    def total(self) -> int:
        return sum(self.instancias_por_clase.values())


class Galeria(BaseModel):
    """Una fila por pan anotado: su vector, su clase y la imagen de la que salió."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    manifiesto: ManifiestoGaleria
    vectores: np.ndarray
    clases: np.ndarray
    origenes: np.ndarray

    @model_validator(mode="after")
    def exigir_consistencia(self) -> Self:
        filas = self.manifiesto.total
        if self.manifiesto.k > filas:
            raise ValueError(f"Galería de {filas} vectores: no alcanza para k={self.manifiesto.k}.")
        if self.vectores.shape != (filas, self.manifiesto.dimension):
            raise ValueError("La matriz de vectores no coincide con el manifiesto.")
        if self.clases.shape != (filas,) or self.origenes.shape != (filas,):
            raise ValueError("Clases u orígenes desalineados con los vectores.")
        if Counter(self.clases.tolist()) != Counter(self.manifiesto.instancias_por_clase):
            raise ValueError("El conteo por clase no coincide con el manifiesto.")
        normas = np.linalg.norm(self.vectores, axis=1)
        if not np.allclose(normas, 1, atol=TOLERANCIA_NORMA):
            raise ValueError("La galería contiene vectores no unitarios.")
        return self

    def guardar(self, carpeta: Path) -> Path:
        carpeta.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            carpeta / ARCHIVO_VECTORES,
            vectores=self.vectores, clases=self.clases, origenes=self.origenes,
        )
        manifiesto = self.manifiesto.model_dump_json(indent=2)
        (carpeta / ARCHIVO_MANIFIESTO).write_text(manifiesto, encoding="utf-8")
        return carpeta

    @classmethod
    def cargar(cls, carpeta: Path) -> Self:
        texto = (carpeta / ARCHIVO_MANIFIESTO).read_text(encoding="utf-8")
        manifiesto = ManifiestoGaleria.model_validate_json(texto)
        with np.load(carpeta / ARCHIVO_VECTORES, allow_pickle=False) as datos:
            return cls(
                manifiesto=manifiesto,
                vectores=datos["vectores"], clases=datos["clases"], origenes=datos["origenes"],
            )
