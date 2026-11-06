"""Salida de la lectura de un fotograma: dónde hay pan y qué clase se le asignó."""

from pydantic import BaseModel, ConfigDict, Field

from .reconocimiento import Reconocimiento

type Punto = tuple[float, float]


class Instancia(BaseModel):
    """Un pan localizado. `reconocimiento` sólo existe cuando la clase viene de la galería."""

    model_config = ConfigDict(frozen=True)

    clase: str
    confianza: float = Field(ge=0, le=1)
    poligono: tuple[Punto, ...] = Field(min_length=3)
    reconocimiento: Reconocimiento | None = None

    @property
    def similitud(self) -> float | None:
        if self.reconocimiento is None:
            return None
        return self.reconocimiento.similitud


class Lectura(BaseModel):
    model_config = ConfigDict(frozen=True)

    instancias: tuple[Instancia, ...]
    inferencia_ms: float = Field(ge=0)
