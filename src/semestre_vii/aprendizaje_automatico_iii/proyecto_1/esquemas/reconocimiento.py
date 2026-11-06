"""Respuesta de la galería: a qué pan se parece un embedding."""

from pydantic import BaseModel, ConfigDict, Field

from .embedding import Embedding
from .pan import ClasePan

DESCONOCIDO = "desconocido"  # Etiqueta visible; no es una clase del catálogo y no tiene precio.


class Vecino(BaseModel):
    model_config = ConfigDict(frozen=True)

    clase: ClasePan
    similitud: float = Field(ge=-1, le=1)
    indice: int = Field(ge=0)  # Fila de la galería: permite ubicarlo en el mapa del embedding.


class Reconocimiento(BaseModel):
    """Clase votada por los k vecinos; None si ni el más cercano llega al umbral."""

    model_config = ConfigDict(frozen=True)

    clase: ClasePan | None
    vecinos: tuple[Vecino, ...] = Field(min_length=1)
    consulta: Embedding  # El vector del pan que se buscó.
    por_clase: dict[ClasePan, float]  # Similitud con el pan más parecido de cada clase.

    @property
    def conocido(self) -> bool:
        return self.clase is not None

    @property
    def votos(self) -> int:
        """Cuántos de los k vecinos son de la clase elegida."""
        return sum(vecino.clase == self.clase for vecino in self.vecinos)

    @property
    def etiqueta(self) -> str:
        if self.conocido:
            return str(self.clase)
        return DESCONOCIDO

    @property
    def similitud(self) -> float:
        """La del vecino más cercano de la clase elegida, no la de un vecino que perdió la votación."""
        if not self.conocido:
            return self.vecinos[0].similitud
        return max(vecino.similitud for vecino in self.vecinos if vecino.clase == self.clase)
