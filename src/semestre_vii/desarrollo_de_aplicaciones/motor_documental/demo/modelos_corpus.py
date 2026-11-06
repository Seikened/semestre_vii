from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class Formato(StrEnum):
    DIGITAL = "digital"
    ESCANEADO = "escaneado"
    MIXTO = "mixto"
    TXT = "txt"


class ClausulaFicticia(BaseModel):
    numero: int
    titulo: str
    texto: str


class PaginaControl(BaseModel):
    numero: int
    metodo: str
    clausulas: list[ClausulaFicticia]


class DocumentoFicticio(BaseModel):
    folio: str
    titulo: str
    archivo: str
    formato: Formato
    variante: str
    inmueble: str
    cedente: str
    receptor: str
    paginas: list[PaginaControl]
    sha256: str = ""


class CasoRecuperacion(BaseModel):
    id: str
    archivo: str
    formato: Formato
    pagina: int
    clausula: int
    cita: str
    natural: str
    libre: str = Field(min_length=1)
    precisa: str


class CorpusFicticio(BaseModel):
    version: Literal["2"]
    semilla: int = 20261102
    documentos: list[DocumentoFicticio] = Field(min_length=1)
    casos: list[CasoRecuperacion]


class CargaDocumento(BaseModel):
    archivo: str
    documento_id: str
    paginas: int
    paginas_ocr: int
    segundos: float | None
    reutilizado: bool = False
    segundos_verificacion: float = 0


class RegistroCarga(BaseModel):
    fecha: str
    coleccion_id: str
    documentos: list[CargaDocumento]
    pendiente: str | None = None


class MedicionConsulta(BaseModel):
    caso_id: str
    archivo: str
    formato: Formato
    pagina: int
    variante: str
    modo: str
    consulta: str
    posicion_pagina: int | None
    posicion_documento: int | None
    cita_en_top5: bool
    cita_literal_en_top5: bool
    segundos: float
    fuentes: list[str]


class ControlExtraccion(BaseModel):
    caso_id: str
    archivo: str
    pagina: int
    metodo_esperado: str
    metodo_observado: str
    cita_preservada: bool
    cita_literal: bool


class InformeEvaluacion(BaseModel):
    fecha: str
    coleccion_id: str
    corpus_sha256: str
    documentos: int
    paginas: int
    paginas_ocr: int
    controles: list[ControlExtraccion]
    consultas: list[MedicionConsulta]
