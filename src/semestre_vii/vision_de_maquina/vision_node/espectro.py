"""Objeto fluido para trabajar en el dominio de Fourier."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

import torch

from .signals import espectros

if TYPE_CHECKING:
    from .node import VisionNode


@dataclass(frozen=True, slots=True, eq=False, repr=False)
class EspectroNode:
    """Espectro 2D inmutable con una API fluida, análoga a VisionNode."""

    tensor: torch.Tensor = field(repr=False)
    titulo: str = "Espectro"
    centrado: bool = True
    mascara: torch.Tensor | None = field(default=None, repr=False)
    filtro: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.tensor, torch.Tensor):
            raise TypeError("tensor debe ser torch.Tensor")
        if self.tensor.ndim != 3:
            raise ValueError(f"el espectro debe usar layout CHW, shape={tuple(self.tensor.shape)}")
        if not torch.is_complex(self.tensor):
            raise ValueError("el espectro debe usar un dtype complejo")
        if self.mascara is not None and self.mascara.shape != self.tensor.shape[-2:]:
            raise ValueError("la máscara debe coincidir con alto y ancho del espectro")

    @classmethod
    def desde_imagen(cls, imagen: "VisionNode", *, centrado: bool = True) -> Self:
        tensor = espectros.transformada_centrada(imagen.tensor) if centrado else espectros.transformada_2d(imagen.tensor)
        return cls(tensor=tensor, titulo=f"TF de {imagen.titulo}", centrado=centrado)

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

    def magnitud(self, *, logaritmica: bool = True) -> "VisionNode":
        from .node import VisionNode

        tensor = espectros.magnitud_visual(self.tensor, logaritmica=logaritmica)
        escala = "log" if logaritmica else "lineal"
        return VisionNode(tensor, titulo=f"Magnitud {escala} · {self.titulo}")

    def mascara_imagen(self) -> "VisionNode":
        from .node import VisionNode

        if self.mascara is None:
            raise ValueError("este espectro no tiene una máscara de filtro asociada")
        return VisionNode(self.mascara.unsqueeze(0), titulo=f"H · {self.filtro or 'Filtro'}")

    def pasabajas_ideal(self, corte: float) -> Self:
        mascara = espectros.mascara_pasabajas_ideal(self.tensor, corte)
        return self._filtrar(mascara, f"ILPF(D0={corte:g})")

    def pasabajas_gaussiano(self, corte: float) -> Self:
        mascara = espectros.mascara_pasabajas_gaussiano(self.tensor, corte)
        return self._filtrar(mascara, f"GLPF(D0={corte:g})")

    def pasabajas_butterworth(self, corte: float, orden: int = 2) -> Self:
        mascara = espectros.mascara_pasabajas_butterworth(self.tensor, corte, orden)
        return self._filtrar(mascara, f"BLPF(D0={corte:g}, n={orden})")

    def inversa(self, *, valor_absoluto: bool = False, clip: bool = True) -> "VisionNode":
        from .node import VisionNode

        tensor = espectros.inversa_2d(self.tensor, centrado=self.centrado, valor_absoluto=valor_absoluto)
        if clip:
            tensor = tensor.clamp(0, 1)
        return VisionNode(tensor, titulo=f"IFFT · {self.titulo}")

    def mostrar(self, *, logaritmica: bool = True, block: bool = True) -> Self:
        self.magnitud(logaritmica=logaritmica).mostrar(block=block)
        return self

    def _filtrar(self, mascara: torch.Tensor, nombre: str) -> Self:
        if not self.centrado:
            raise ValueError("los filtros radiales requieren un espectro centrado; usa imagen.fft()")
        tensor = espectros.aplicar_mascara(self.tensor, mascara)
        return type(self)(tensor=tensor, titulo=f"{self.titulo} · {nombre}", centrado=True, mascara=mascara, filtro=nombre)

    def __repr__(self) -> str:
        filtro = f", filtro={self.filtro!r}" if self.filtro else ""
        return f"EspectroNode(shape={self.shape!r}, dtype={self.dtype}, device={self.device}, centrado={self.centrado}{filtro})"
