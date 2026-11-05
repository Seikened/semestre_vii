from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from app.contratos import Entrada, ModoBusqueda, ResultadoBusqueda

TextoChat = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
TextoConsulta = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]


class MensajeChat(Entrada):
    rol: Literal["user", "assistant"]
    texto: TextoChat


class ConsultaChat(Entrada):
    texto: TextoConsulta = Field(examples=["¿Cuándo se devuelve el depósito de Aurora?"])
    modo: ModoBusqueda = ModoBusqueda.HIBRIDA
    coleccion_id: UUID | None = None
    historial: list[MensajeChat] = Field(default_factory=list, max_length=6)


class ArgumentosBusqueda(Entrada):
    texto: TextoConsulta


class RespuestaLuna(Entrada):
    respuesta: TextoChat
    citas: list[int] = Field(max_length=5)


class RespuestaChat(BaseModel):
    respuesta: str = Field(examples=["Se devuelve dentro de treinta días naturales, descontando daños documentados. [1]"])
    resultado: ResultadoBusqueda
    modelo: str
