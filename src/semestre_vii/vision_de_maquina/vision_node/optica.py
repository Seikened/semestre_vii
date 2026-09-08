import math
from collections.abc import Sequence
from dataclasses import dataclass
from numbers import Real

import polars as pl

_MILIMETROS_POR_UNIDAD = {
    "um": 0.001,
    "ucm": 0.01,
    "umm": 0.1,
    "mm": 1.0,
    "cm": 10.0,
    "m": 1000.0,
}


def medida(valor: float, unidad_origen: str, unidad_destino: str) -> float:
    """Convierte una medida entre las unidades métricas soportadas."""
    _validar_finito("valor", valor)
    if unidad_origen not in _MILIMETROS_POR_UNIDAD:
        raise ValueError(f"unidad_origen no soportada: {unidad_origen}")
    if unidad_destino not in _MILIMETROS_POR_UNIDAD:
        raise ValueError(f"unidad_destino no soportada: {unidad_destino}")
    milimetros = valor * _MILIMETROS_POR_UNIDAD[unidad_origen]
    return milimetros / _MILIMETROS_POR_UNIDAD[unidad_destino]


@dataclass(frozen=True, slots=True)
class Camara:
    ancho_px: int
    alto_px: int
    pixel_size_um: float
    nombre: str = ""

    def __post_init__(self) -> None:
        _validar_entero_positivo("ancho_px", self.ancho_px)
        _validar_entero_positivo("alto_px", self.alto_px)
        _validar_positivo("pixel_size_um", self.pixel_size_um)

    @property
    def ancho_mm(self) -> float:
        return medida(self.ancho_px * self.pixel_size_um, "um", "mm")

    @property
    def alto_mm(self) -> float:
        return medida(self.alto_px * self.pixel_size_um, "um", "mm")

    @property
    def diagonal_mm(self) -> float:
        return math.hypot(self.ancho_mm, self.alto_mm)


@dataclass(frozen=True, slots=True)
class Escena:
    fov_ancho_mm: float
    fov_alto_mm: float
    do_mm: float = 600.0

    def __post_init__(self) -> None:
        _validar_positivo("fov_ancho_mm", self.fov_ancho_mm)
        _validar_positivo("fov_alto_mm", self.fov_alto_mm)
        _validar_positivo("do_mm", self.do_mm)


def magnificacion_a_distancia(f_mm: float, do_mm: float) -> float:
    """Calcula la magnificación de una lente delgada a distancia fija."""
    _validar_positivo("f_mm", f_mm)
    _validar_positivo("do_mm", do_mm)
    if do_mm <= f_mm:
        raise ValueError("do_mm debe ser mayor que f_mm")
    return f_mm / (do_mm - f_mm)


def focal_ideal(camara: Camara, escena: Escena) -> float:
    """Calcula la focal máxima que todavía cubre el FOV solicitado."""
    magnificacion = min(
        camara.ancho_mm / escena.fov_ancho_mm,
        camara.alto_mm / escena.fov_alto_mm,
    )
    return magnificacion * escena.do_mm / (1 + magnificacion)


def fov_real(camara: Camara, f_mm: float, do_mm: float) -> tuple[float, float]:
    """Calcula el campo de visión real en milímetros."""
    magnificacion = magnificacion_a_distancia(f_mm, do_mm)
    return camara.ancho_mm / magnificacion, camara.alto_mm / magnificacion


def evaluar_focales(
    camara: Camara,
    escena: Escena,
    focales_mm: Sequence[float],
) -> pl.DataFrame:
    """Compara focales comerciales en una tabla Polars."""
    filas = []
    for focal in focales_mm:
        fov_ancho, fov_alto = fov_real(camara, focal, escena.do_mm)
        magnificacion = magnificacion_a_distancia(focal, escena.do_mm)
        filas.append(
            {
                "f_mm": float(focal),
                "m": round(magnificacion, 5),
                "fov_x_mm": round(fov_ancho, 1),
                "fov_y_mm": round(fov_alto, 1),
                "pS_x_mm": round(fov_ancho / camara.ancho_px, 3),
                "pS_y_mm": round(fov_alto / camara.alto_px, 3),
                "cubre_fov": (fov_ancho >= escena.fov_ancho_mm and fov_alto >= escena.fov_alto_mm),
            }
        )
    return pl.DataFrame(
        filas,
        schema={
            "f_mm": pl.Float64,
            "m": pl.Float64,
            "fov_x_mm": pl.Float64,
            "fov_y_mm": pl.Float64,
            "pS_x_mm": pl.Float64,
            "pS_y_mm": pl.Float64,
            "cubre_fov": pl.Boolean,
        },
    )


def _validar_entero_positivo(nombre: str, valor: int) -> None:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(f"{nombre} debe ser un entero")
    if valor <= 0:
        raise ValueError(f"{nombre} debe ser mayor que cero")


def _validar_positivo(nombre: str, valor: float) -> None:
    _validar_finito(nombre, valor)
    if valor <= 0:
        raise ValueError(f"{nombre} debe ser mayor que cero")


def _validar_finito(nombre: str, valor: float) -> None:
    es_numero = isinstance(valor, Real) and not isinstance(valor, bool)
    if not es_numero:
        raise TypeError(f"{nombre} debe ser un número")
    if not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser finito")
