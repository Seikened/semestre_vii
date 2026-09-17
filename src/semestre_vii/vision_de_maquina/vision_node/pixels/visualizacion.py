from collections.abc import Sequence

"""Visualizaciones de imágenes y distribuciones de píxeles."""

import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.figure import Figure

from ..grafica import dibujar_imagen
from ..grafica import imagen_numpy as _imagen_numpy
from ..grafica import mapa_imagen as _mapa_imagen
from ..grafica import presentar as _presentar
from . import transformaciones

_COLORES_RGB = ("red", "green", "blue")
_NOMBRES_RGB = ("Rojo", "Verde", "Azul")


def mostrar(tensor: torch.Tensor, titulo: str, *, block: bool = True) -> Figure:
    figura, eje = plt.subplots(figsize=(8, 6))
    dibujar_imagen(eje, tensor, titulo, rango="auto")
    return _presentar(figura, block)


def mostrar_diferencias(
    tensor: torch.Tensor,
    comparada: torch.Tensor,
    titulo: str,
    titulo_comparada: str,
    *,
    magnifier: float = 1.0,
    block: bool = True,
) -> Figure:
    diferencia = transformaciones.diferencia_absoluta(tensor, comparada, magnifier)
    figura, ejes = plt.subplots(1, 3, figsize=(15, 5))
    paneles = (
        (tensor, titulo),
        (comparada, titulo_comparada),
        (diferencia, f"Diferencia x{magnifier:g}"),
    )
    for eje, (imagen, nombre) in zip(ejes, paneles, strict=True):
        eje.imshow(_imagen_numpy(imagen), cmap=_mapa_imagen(imagen), vmin=0, vmax=1)
        eje.set_title(nombre)
        eje.axis("off")
    return _presentar(figura, block)


def histograma(tensor: torch.Tensor, titulo: str, *, block: bool = True) -> Figure:
    if tensor.shape[0] == 1:
        figura, ejes = plt.subplots(1, 2, figsize=(12, 4))
        eje_imagen = ejes[0]
        ejes_histograma = (ejes[1],)
    else:
        figura, ejes = plt.subplots(2, 2, figsize=(12, 8))
        eje_imagen = ejes[0, 0]
        ejes_histograma = (ejes[0, 1], ejes[1, 0], ejes[1, 1])

    eje_imagen.imshow(_imagen_numpy(tensor), cmap=_mapa_imagen(tensor), vmin=0, vmax=1)
    eje_imagen.set_title(titulo)
    eje_imagen.axis("off")
    for eje, canal, nombre, color in zip(
        ejes_histograma,
        tensor,
        *_metadatos_canales(tensor),
        strict=True,
    ):
        _dibujar_histograma_canal(eje, canal, nombre, color)
    figura.suptitle(f"Histograma: {titulo}")
    return _presentar(figura, block)


def graficar_acumulado(
    tensor: torch.Tensor,
    titulo: str,
    *,
    block: bool = False,
) -> Figure:
    acumulados = transformaciones.histograma_acumulado(tensor).detach().cpu().numpy()
    figura, eje = plt.subplots(figsize=(9, 5))
    for acumulado, nombre, color in zip(
        acumulados,
        *_metadatos_canales(tensor),
        strict=True,
    ):
        eje.plot(np.arange(256), acumulado, color=color, label=nombre)
    eje.set(title=f"Distribución acumulada: {titulo}", xlabel="Intensidad", ylabel="Proporción")
    eje.set_xlim(0, 255)
    eje.set_ylim(0, 1.02)
    eje.grid(alpha=0.2)
    eje.legend()
    return _presentar(figura, block)


def mostrar_reporte(tensor: torch.Tensor, titulo: str, *, block: bool = True) -> Figure:
    if tensor.shape[0] == 1:
        return mostrar(tensor, titulo, block=block)

    canales = transformaciones.separar_canales(tensor)
    gris = transformaciones.escala_grises(tensor)
    paneles_canales = tuple((canal, nombre) for nombre, canal in canales.items())
    paneles = ((tensor, titulo), *paneles_canales, (gris, "Escala de grises"))
    figura, ejes = plt.subplots(1, len(paneles), figsize=(20, 5))
    for eje, (imagen, nombre) in zip(ejes, paneles, strict=True):
        eje.imshow(_imagen_numpy(imagen), cmap=_mapa_imagen(imagen), vmin=0, vmax=1)
        eje.set_title(nombre)
        eje.axis("off")
    return _presentar(figura, block)


def graficar_transformacion_lineal(
    entrada: Sequence[float],
    salida: Sequence[float],
    *,
    block: bool = False,
) -> Figure:
    figura, eje = plt.subplots(figsize=(6, 6))
    eje.plot(entrada, salida, marker="o")
    eje.plot((0, 255), (0, 255), color="gray", linestyle=":", alpha=0.6)
    eje.set(
        title="Transformación lineal por tramos",
        xlabel="Intensidad de entrada",
        ylabel="Intensidad de salida",
        xlim=(0, 255),
        ylim=(0, 255),
    )
    eje.grid(alpha=0.2)
    return _presentar(figura, block)


def graficar_transformaciones_rgb(
    rojo: Sequence[tuple[float, float]],
    verde: Sequence[tuple[float, float]],
    azul: Sequence[tuple[float, float]],
    *,
    block: bool = False,
) -> Figure:
    figura, eje = plt.subplots(figsize=(6, 6))
    for puntos, nombre, color in zip(
        (rojo, verde, azul),
        _NOMBRES_RGB,
        _COLORES_RGB,
        strict=True,
    ):
        entrada, salida = zip(*puntos, strict=True)
        eje.plot(entrada, salida, marker="o", color=color, label=nombre)
    eje.set(
        title="Transformación por canal",
        xlabel="Intensidad de entrada",
        ylabel="Intensidad de salida",
        xlim=(0, 255),
        ylim=(0, 255),
    )
    eje.grid(alpha=0.2)
    eje.legend()
    return _presentar(figura, block)


def _dibujar_histograma_canal(eje, canal: torch.Tensor, nombre: str, color: str) -> None:
    valores = canal.detach().clamp(0.0, 1.0).mul(255).cpu().numpy().ravel()
    conteos, limites = np.histogram(valores, bins=256, range=(0, 256))
    centros = (limites[:-1] + limites[1:]) / 2
    eje.bar(centros, conteos, width=1, color=color, alpha=0.7)
    eje.axvline(255, color="red", linestyle="--", alpha=0.6, label="Saturación")
    if np.count_nonzero(conteos) >= 26:
        eje.set_yscale("log", nonpositive="clip")
        eje.set_ylabel("Píxeles (log)")
    else:
        eje.set_ylabel("Píxeles")
    eje.set(title=f"Canal {nombre}", xlabel="Intensidad", xlim=(0, 255))
    eje.grid(alpha=0.2)
    eje.legend()


def _metadatos_canales(tensor: torch.Tensor) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if tensor.shape[0] == 1:
        return ("B/N",), ("black",)
    return _NOMBRES_RGB, _COLORES_RGB
