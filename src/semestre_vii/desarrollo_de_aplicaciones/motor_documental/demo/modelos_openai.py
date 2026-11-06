from typing import Literal

from pydantic import BaseModel, Field


class ArchivoProveedor(BaseModel):
    id: str
    filename: str
    bytes: int


class ReciboArchivo(BaseModel):
    archivo: str
    sha256: str
    file_id: str
    segundos: float


class RegistroOpenAI(BaseModel):
    corpus_sha256: str
    vector_store_id: str
    archivos: list[ReciboArchivo] = Field(default_factory=list)
    operacion_pendiente: str | None = None
    lote_id: str | None = None


class ContadoresArchivos(BaseModel):
    in_progress: int
    completed: int
    failed: int
    cancelled: int
    total: int


class StoreOpenAI(BaseModel):
    id: str
    name: str
    status: str
    file_counts: ContadoresArchivos
    usage_bytes: int


class NuevoLote(BaseModel):
    file_ids: list[str]


class LoteOpenAI(BaseModel):
    id: str
    status: str
    file_counts: ContadoresArchivos


class ErrorIndexado(BaseModel):
    code: str
    message: str


class ArchivoIndexado(BaseModel):
    id: str
    status: str
    last_error: ErrorIndexado | None = None


class PaginaArchivos(BaseModel):
    data: list[ArchivoIndexado]
    has_more: bool
    last_id: str | None = None


class RankingOpenAI(BaseModel):
    ranker: Literal["auto"] = "auto"
    score_threshold: float = 0


class BusquedaOpenAI(BaseModel):
    query: str
    max_num_results: int = 5
    rewrite_query: bool = False
    ranking_options: RankingOpenAI = Field(default_factory=RankingOpenAI)


class TextoOpenAI(BaseModel):
    type: Literal["text"]
    text: str


class PasajeOpenAI(BaseModel):
    file_id: str
    filename: str
    score: float
    content: list[TextoOpenAI]


class RespuestaBusqueda(BaseModel):
    object: Literal["vector_store.search_results.page"]
    data: list[PasajeOpenAI]
    search_query: list[str]
    has_more: bool


class MedicionOpenAI(BaseModel):
    vector_store_id: str
    corpus_sha256: str
    caso_id: str
    variante: str
    modo_local: str
    archivo_esperado: str
    peticion: BusquedaOpenAI
    respuesta: RespuestaBusqueda
    request_id: str | None
    segundos: float
    posicion_documento: int | None
    cita_normalizada_en_top5: bool
    cita_literal_en_top5: bool
