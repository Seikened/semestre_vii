from dataclasses import dataclass
from math import isfinite
from typing import Self


@dataclass(frozen=True, slots=True)
class PuntoNotch:
    fila: float
    columna: float
    radio: float
    activo: bool = True

    @classmethod
    def desde_json(cls, contenido: object, alto: int, ancho: int) -> Self:
        if not isinstance(contenido, dict):
            raise TypeError("cada punto debe contener fila, columna y radio")
        valores = [contenido.get(nombre) for nombre in ("fila", "columna", "radio")]
        if any(isinstance(valor, bool) or not isinstance(valor, (int, float)) for valor in valores):
            raise ValueError("fila, columna y radio deben ser números")
        try:
            valores = [float(valor) for valor in valores]
        except OverflowError:
            raise ValueError("fila, columna y radio deben ser números finitos") from None
        if not all(isfinite(valor) for valor in valores):
            raise ValueError("fila, columna y radio deben ser números finitos")
        fila, columna, radio = valores
        if not -(alto // 2) <= fila <= alto - 1 - alto // 2:
            raise ValueError("la fila está fuera del espectro")
        if not -(ancho // 2) <= columna <= ancho - 1 - ancho // 2:
            raise ValueError("la columna está fuera del espectro")
        if radio <= 0:
            raise ValueError("el radio debe ser mayor que cero")
        activo = contenido.get("activo", True)
        if not isinstance(activo, bool):
            raise TypeError("el estado activo debe ser booleano")
        return cls(fila, columna, radio, activo)


@dataclass(frozen=True, slots=True)
class SolicitudFiltro:
    puntos: tuple[PuntoNotch, ...]

    @classmethod
    def desde_json(cls, contenido: object, alto: int, ancho: int) -> Self:
        if not isinstance(contenido, dict) or not isinstance(contenido.get("puntos"), list):
            raise TypeError("se necesita una lista de puntos")
        if len(contenido["puntos"]) > 128:
            raise ValueError("el experimento admite hasta 128 pares notch")
        puntos = tuple(PuntoNotch.desde_json(punto, alto, ancho) for punto in contenido["puntos"])
        return cls(puntos)


@dataclass(frozen=True, slots=True)
class InfoImagen:
    nombre: str
    ancho: int
    alto: int
    dc_fila: int
    dc_columna: int


@dataclass(frozen=True, slots=True)
class ConfiguracionFiltro:
    imagen: str
    ancho: int
    alto: int
    recorte: str
    puntos: tuple[PuntoNotch, ...]


@dataclass(frozen=True, slots=True)
class ResultadoFiltro:
    imagen: str
    espectro: str
    porcentaje_rechazado: float
    dc_rechazada: bool


@dataclass(frozen=True, slots=True)
class ErrorRespuesta:
    mensaje: str
