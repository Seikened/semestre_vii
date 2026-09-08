from dataclasses import dataclass, field

import numpy as np
import torch
from skimage.feature import peak_local_max

_NOMBRES_RGB = ("Rojo", "Verde", "Azul")
_COLORES_RGB = ("red", "green", "blue")


@dataclass(frozen=True, slots=True)
class SenalCanal:
    """Señal espacial y espectro de una fila para un canal."""

    nombre: str
    color: str
    intensidades: np.ndarray = field(repr=False)
    frecuencias: np.ndarray = field(repr=False)
    magnitudes: np.ndarray = field(repr=False)


@dataclass(frozen=True, slots=True)
class PicoEspectral:
    """Pico de frecuencia expresado respecto al centro del espectro."""

    fila: int
    columna: int
    desplazamiento_x: int
    desplazamiento_y: int
    frecuencia_x: float
    frecuencia_y: float
    magnitud: float
    periodo_px: float


@dataclass(frozen=True, slots=True)
class EspectroCanal:
    """Espectro bidimensional y sus picos principales."""

    nombre: str
    color: str
    magnitud: np.ndarray = field(repr=False)
    magnitud_lineal: np.ndarray = field(repr=False)
    picos: tuple[PicoEspectral, ...] = ()


def senales_fila(
    tensor: torch.Tensor,
    fila: int,
    *,
    excluir_dc: bool = False,
) -> tuple[SenalCanal, ...]:
    _validar_fila(tensor, fila)
    resultados = []
    for canal, nombre, color in zip(tensor, *_metadatos_canales(tensor), strict=True):
        intensidades = canal[fila].detach().cpu().numpy()
        frecuencias = torch.fft.rfftfreq(canal.shape[1]).numpy()
        magnitudes = torch.fft.rfft(canal[fila]).abs()
        if excluir_dc:
            magnitudes[0] = 0
        resultados.append(
            SenalCanal(
                nombre=nombre,
                color=color,
                intensidades=intensidades,
                frecuencias=frecuencias,
                magnitudes=magnitudes.detach().cpu().numpy(),
            )
        )
    return tuple(resultados)


def analizar_espectros(
    tensor: torch.Tensor,
    *,
    n_picos: int = 0,
    excluir_radio_dc: int = 0,
    distancia_minima: int = 5,
) -> tuple[EspectroCanal, ...]:
    _validar_entero_no_negativo("n_picos", n_picos)
    _validar_entero_no_negativo("excluir_radio_dc", excluir_radio_dc)
    _validar_entero_positivo("distancia_minima", distancia_minima)

    resultados = []
    for canal, nombre, color in zip(tensor, *_metadatos_canales(tensor), strict=True):
        magnitud_lineal = _magnitud_fft2_lineal(canal)
        magnitud = torch.log1p(magnitud_lineal)
        magnitud_busqueda = magnitud.clone()
        if excluir_radio_dc:
            _eliminar_dc(magnitud_busqueda, excluir_radio_dc)
        picos = _detectar_picos(magnitud_busqueda, n_picos, distancia_minima)
        resultados.append(
            EspectroCanal(
                nombre=nombre,
                color=color,
                magnitud=magnitud.detach().cpu().numpy(),
                magnitud_lineal=magnitud_lineal.detach().cpu().numpy(),
                picos=picos,
            )
        )
    return tuple(resultados)


def magnitud_fft2(canal: torch.Tensor, *, excluir_radio_dc: int = 0) -> torch.Tensor:
    if canal.ndim != 2:
        raise ValueError("canal debe ser una matriz bidimensional")
    _validar_entero_no_negativo("excluir_radio_dc", excluir_radio_dc)

    magnitud = torch.log1p(_magnitud_fft2_lineal(canal))
    if excluir_radio_dc:
        _eliminar_dc(magnitud, excluir_radio_dc)
    return magnitud


def _magnitud_fft2_lineal(canal: torch.Tensor) -> torch.Tensor:
    espectro = torch.fft.fftshift(torch.fft.fft2(canal))
    return espectro.abs()


def _detectar_picos(
    magnitud: torch.Tensor,
    n_picos: int,
    distancia_minima: int,
) -> tuple[PicoEspectral, ...]:
    if n_picos == 0:
        return ()

    magnitud_np = magnitud.detach().cpu().numpy()
    coordenadas = peak_local_max(
        magnitud_np,
        min_distance=distancia_minima,
        num_peaks=n_picos,
        exclude_border=False,
    )
    alto, ancho = magnitud_np.shape
    centro_y = alto // 2
    centro_x = ancho // 2
    picos = []
    for fila, columna in coordenadas:
        desplazamiento_x = int(columna) - centro_x
        desplazamiento_y = int(fila) - centro_y
        frecuencia_x = desplazamiento_x / ancho
        frecuencia_y = desplazamiento_y / alto
        frecuencia_radial = float(np.hypot(frecuencia_x, frecuencia_y))
        periodo = float("inf") if frecuencia_radial == 0 else 1 / frecuencia_radial
        picos.append(
            PicoEspectral(
                fila=int(fila),
                columna=int(columna),
                desplazamiento_x=desplazamiento_x,
                desplazamiento_y=desplazamiento_y,
                frecuencia_x=frecuencia_x,
                frecuencia_y=frecuencia_y,
                magnitud=float(magnitud_np[fila, columna]),
                periodo_px=periodo,
            )
        )
    return tuple(picos)


def _eliminar_dc(magnitud: torch.Tensor, radio: int) -> None:
    centro_y = magnitud.shape[0] // 2
    centro_x = magnitud.shape[1] // 2
    filas, columnas = torch.meshgrid(
        torch.arange(magnitud.shape[0], device=magnitud.device),
        torch.arange(magnitud.shape[1], device=magnitud.device),
        indexing="ij",
    )
    mascara_dc = (filas - centro_y).square() + (columnas - centro_x).square() <= radio**2
    magnitud[mascara_dc] = 0


def _metadatos_canales(tensor: torch.Tensor) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if tensor.shape[0] == 1:
        return ("B/N",), ("black",)
    return _NOMBRES_RGB, _COLORES_RGB


def _validar_fila(tensor: torch.Tensor, fila: int) -> None:
    _validar_entero_no_negativo("fila", fila)
    if fila >= tensor.shape[1]:
        raise ValueError(f"fila debe ser menor que {tensor.shape[1]}")


def _validar_entero_no_negativo(nombre: str, valor: int) -> None:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(f"{nombre} debe ser un entero")
    if valor < 0:
        raise ValueError(f"{nombre} debe ser mayor o igual a cero")


def _validar_entero_positivo(nombre: str, valor: int) -> None:
    _validar_entero_no_negativo(nombre, valor)
    if valor == 0:
        raise ValueError(f"{nombre} debe ser mayor que cero")
