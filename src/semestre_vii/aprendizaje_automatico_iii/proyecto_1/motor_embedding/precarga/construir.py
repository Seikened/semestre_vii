"""Dataset con polígonos → recortes → embeddings → galería lista para guardar."""

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import cv2
import numpy as np

from ...entrenamiento.datos import Dataset, cargar_dataset
from ...esquemas.galeria import Galeria, ManifiestoGaleria
from ..encoder import DIMENSION, NOMBRE, Encoder
from ..recorte import a_gris, recortar
from ..vecinos import k_vecinos, votar

K = 3  # Elegido por macro-F1 de validación en el Colab 02; test no se tocó.
PERCENTIL_UMBRAL = 5
AVISO_CADA = 250


@dataclass(frozen=True)
class SplitVectorizado:
    vectores: np.ndarray
    clases: np.ndarray
    origenes: np.ndarray
    omitidas: int


def construir_galeria(
    data_yaml: Path, encoder: Encoder, clases: tuple[str, ...] | None, gris: bool,
) -> Galeria:
    """La galería es train; validación mide la exactitud y calibra el umbral de desconocido."""
    dataset = cargar_dataset(data_yaml)
    elegidas = set(clases or dataset.nombres)
    ausentes = elegidas - set(dataset.nombres)
    if ausentes:
        raise ValueError(f"Clases inexistentes en el dataset: {sorted(ausentes)}")

    train = vectorizar_split(dataset, "train", encoder, elegidas, gris)
    validacion = vectorizar_split(dataset, "val", encoder, elegidas, gris)
    exactitud, umbral = evaluar(train, validacion)

    manifiesto = ManifiestoGaleria(
        encoder=NOMBRE, dimension=DIMENSION, k=K, umbral=umbral,
        dataset=str(data_yaml.parent),
        instancias_por_clase=dict(sorted(Counter(train.clases.tolist()).items())),
        omitidas=train.omitidas, gris=gris, exactitud_validacion=exactitud,
        creada=datetime.now(UTC),
    )
    return Galeria(
        manifiesto=manifiesto,
        vectores=train.vectores, clases=train.clases, origenes=train.origenes,
    )


def vectorizar_split(
    dataset: Dataset, split: str, encoder: Encoder, elegidas: set[str], gris: bool,
) -> SplitVectorizado:
    vectores, clases, origenes, omitidas = [], [], [], 0
    muestras = [m for m in dataset.muestras if m.split == split]
    for numero, muestra in enumerate(muestras, 1):
        imagen = cv2.imread(str(muestra.imagen))
        if imagen is None:
            raise ValueError(f"No se puede leer {muestra.imagen}")
        if gris:
            imagen = a_gris(imagen)
        alto, ancho = imagen.shape[:2]
        recortes = []
        for indice, etiqueta in enumerate(muestra.etiquetas):
            nombre = dataset.nombres[etiqueta.clase]
            if nombre not in elegidas:
                continue
            if not etiqueta.segmentacion:
                omitidas += 1  # Una caja no es silueta: recortarla metería fondo al vector.
                continue
            poligono = np.asarray(etiqueta.coordenadas).reshape(-1, 2) * (ancho, alto)
            recorte = recortar(imagen, poligono)
            if recorte is None:
                omitidas += 1
                continue
            recortes.append(recorte)
            clases.append(nombre)
            origenes.append(f"{muestra.imagen.name}#{indice}")
        vectores.extend(embedding.vector for embedding in encoder.vectorizar(recortes))
        if numero % AVISO_CADA == 0:
            print(f"  {split}: {numero}/{len(muestras)} imágenes")

    if not vectores:
        raise ValueError(f"El split {split} no produjo ningún recorte.")
    print(f"  {split}: {len(vectores)} panes vectorizados, {omitidas} omitidos")
    matriz = np.stack(vectores).astype(np.float32)
    return SplitVectorizado(matriz, np.asarray(clases), np.asarray(origenes), omitidas)


def evaluar(galeria: SplitVectorizado, validacion: SplitVectorizado) -> tuple[float, float]:
    """Exactitud k-NN en validación y umbral: percentil bajo de la similitud de los aciertos."""
    aciertos, similitudes = [], []
    for vector, clase in zip(validacion.vectores, validacion.clases, strict=True):
        vecinos = k_vecinos(galeria.vectores @ vector, galeria.clases, K)
        acierto = votar(vecinos) == clase
        aciertos.append(acierto)
        if acierto:
            similitudes.append(vecinos[0].similitud)
    if not similitudes:
        raise ValueError("Ningún pan de validación se reconoció; no hay con qué calibrar el umbral.")
    exactitud = float(np.mean(aciertos))
    umbral = float(np.percentile(similitudes, PERCENTIL_UMBRAL))
    return exactitud, umbral
