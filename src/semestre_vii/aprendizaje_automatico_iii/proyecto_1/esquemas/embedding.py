"""Salida del encoder: un vector unitario por pan recortado."""

import numpy as np
from pydantic import BaseModel, ConfigDict, field_validator

TOLERANCIA_NORMA = 1e-3


class Embedding(BaseModel):
    """Vector L2 unitario: el producto punto entre dos embeddings es su similitud coseno."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    vector: np.ndarray

    @field_validator("vector")
    @classmethod
    def exigir_unitario(cls, vector: np.ndarray) -> np.ndarray:
        if vector.ndim != 1 or not np.isfinite(vector).all():
            raise ValueError("El embedding debe ser un vector 1-D finito.")
        if abs(np.linalg.norm(vector) - 1) > TOLERANCIA_NORMA:
            raise ValueError("El embedding debe tener norma L2 igual a 1.")
        return vector
