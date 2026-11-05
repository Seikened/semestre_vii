from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.modelos import MetodoExtraccion, PaginaExtraida

Titulo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NuevaColeccion(Entrada):
    nombre: str = Field(min_length=1, max_length=120, examples=["Contratos ficticios"])

    @model_validator(mode="after")
    def validar_nombre(self):
        self.nombre = self.nombre.strip()
        if not self.nombre:
            raise ValueError("El nombre no puede estar vacío.")
        return self


class Coleccion(BaseModel):
    id: UUID
    nombre: str
    creada_en: datetime


class Documento(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{
        "id": "c563feab-223a-4b2c-b743-d92f7463de3c",
        "coleccion_id": "8c9fac40-7aee-4aa6-a08c-3e1ad438da91",
        "titulo": "Contrato ficticio Aurora", "nombre_original": "FIC-001_digital.pdf",
        "extension": "pdf", "modelo": "intfloat/multilingual-e5-small",
        "creado_en": "2026-11-02T12:00:00-06:00", "paginas": 2, "paginas_ocr": 0
    }]})

    id: UUID
    coleccion_id: UUID
    titulo: str
    nombre_original: str
    extension: str
    modelo: str
    creado_en: datetime
    paginas: int
    paginas_ocr: int


class DetalleDocumento(BaseModel):
    documento: Documento
    paginas: list[PaginaExtraida]


class EditarDocumento(Entrada):
    titulo: Titulo | None = None
    coleccion_id: UUID | None = None

    @model_validator(mode="after")
    def validar_cambio(self):
        if self.titulo is None and self.coleccion_id is None:
            raise ValueError("Indica título o colección.")
        return self


class ModoBusqueda(StrEnum):
    TEXTO = "texto"
    VECTOR = "vector"
    HIBRIDA = "hibrida"


class Consulta(Entrada):
    model_config = ConfigDict(extra="forbid", json_schema_extra={"examples": [
        {"texto": "¿Cuándo se devuelve el depósito de Aurora?", "modo": "hibrida", "limite": 5}
    ]})

    texto: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
    modo: ModoBusqueda = ModoBusqueda.HIBRIDA
    limite: int = Field(default=5, ge=1, le=20)
    coleccion_id: UUID | None = None


class Coincidencia(BaseModel):
    documento_id: UUID
    titulo: str
    nombre_original: str
    pagina: int
    metodo: MetodoExtraccion
    texto: str
    puntuacion: float


class ResultadoBusqueda(BaseModel):
    consulta: str
    modo: ModoBusqueda
    coincidencias: list[Coincidencia]


class ErrorRespuesta(BaseModel):
    codigo: str = Field(examples=["DOCUMENTO_NO_ENCONTRADO"])
    detalle: str = Field(examples=["El documento no está disponible."])


class Salud(BaseModel):
    estado: str = "disponible"
    modelo: str
    dimension: int
