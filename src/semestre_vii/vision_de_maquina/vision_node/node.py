from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

import torch

from . import transformaciones
from .io import cargar_imagen, guardar_imagen

_DTYPES_SOPORTADOS = frozenset({torch.float32, torch.float64})
_CANALES_SOPORTADOS = frozenset({1, 3})


@dataclass(frozen=True, slots=True, eq=False, repr=False)
class VisionNode:
    """Fachada Fluent para transformar tensores de imagen CHW."""

    tensor: torch.Tensor = field(repr=False)
    titulo: str = "Imagen"

    def __post_init__(self) -> None:
        _validar_tensor(self.tensor)

    @classmethod
    def desde_archivo(
        cls,
        ruta: str | Path,
        *,
        device: str | torch.device = "cpu",
        dtype: torch.dtype = torch.float32,
    ) -> Self:
        _validar_dtype(dtype)
        tensor = cargar_imagen(ruta, device=device, dtype=dtype)
        return cls(tensor=tensor, titulo=Path(ruta).name)

    @property
    def shape(self) -> tuple[int, int, int]:
        return tuple(self.tensor.shape)

    @property
    def canales(self) -> int:
        return self.tensor.shape[0]

    @property
    def alto(self) -> int:
        return self.tensor.shape[1]

    @property
    def ancho(self) -> int:
        return self.tensor.shape[2]

    @property
    def device(self) -> torch.device:
        return self.tensor.device

    @property
    def dtype(self) -> torch.dtype:
        return self.tensor.dtype

    @property
    def es_grises(self) -> bool:
        return self.canales == 1

    def guardar(self, ruta: str | Path) -> Self:
        guardar_imagen(self.tensor, ruta)
        return self

    def clip(self, minimo: float = 0.0, maximo: float = 1.0) -> Self:
        tensor = transformaciones.clip(self.tensor, minimo, maximo)
        return self._nuevo(tensor)

    def negativo(self) -> Self:
        return self._nuevo(transformaciones.negativo(self.tensor))

    def escala_grises(self) -> Self:
        return self._nuevo(transformaciones.escala_grises(self.tensor))

    def ganancia(self, factor: float) -> Self:
        return self._nuevo(transformaciones.ganancia(self.tensor, factor))

    def transformacion_gamma(self, exponente: float) -> Self:
        tensor = transformaciones.transformacion_gamma(self.tensor, exponente)
        return self._nuevo(tensor)

    def cuantizar(self, bits: int) -> Self:
        return self._nuevo(transformaciones.cuantizar(self.tensor, bits))

    def binarizar(self, umbral: float) -> Self:
        return self._nuevo(transformaciones.binarizar(self.tensor, umbral))

    def binarizar_rango(self, minimo: float, maximo: float) -> Self:
        tensor = transformaciones.binarizar_rango(self.tensor, minimo, maximo)
        return self._nuevo(tensor)

    def __repr__(self) -> str:
        return (
            f"VisionNode(shape={self.shape!r}, dtype={self.dtype}, "
            f"device={self.device}, titulo={self.titulo!r})"
        )

    def _nuevo(self, tensor: torch.Tensor) -> Self:
        return type(self)(tensor=tensor, titulo=self.titulo)


def _validar_tensor(tensor: torch.Tensor) -> None:
    if not isinstance(tensor, torch.Tensor):
        raise TypeError("tensor debe ser torch.Tensor")
    if tensor.ndim != 3:
        raise ValueError(f"tensor debe usar layout CHW; shape={tuple(tensor.shape)}")
    if tensor.shape[0] not in _CANALES_SOPORTADOS:
        raise ValueError(f"tensor debe tener 1 o 3 canales; canales={tensor.shape[0]}")
    _validar_dtype(tensor.dtype)


def _validar_dtype(dtype: torch.dtype) -> None:
    if dtype not in _DTYPES_SOPORTADOS:
        raise ValueError(f"dtype debe ser float32 o float64; dtype={dtype}")
