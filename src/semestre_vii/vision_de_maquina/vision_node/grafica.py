"""Composición declarativa de gráficas para VisionNode y EspectroNode."""

from collections.abc import Callable
from dataclasses import dataclass
from math import ceil
from typing import Literal, Self

import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.axes import Axes
from matplotlib.figure import Figure

RangoImagen = Literal["auto", "unidad", "simetrico"] | tuple[float, float]


@dataclass(slots=True)
class _Panel:
    dibujar: Callable[[Axes], None]


class Grafica:
    """Builder fluido para componer imágenes, señales, espectros y filtros sin repetir Matplotlib."""

    def __init__(
        self,
        titulo: str | None = None,
        *,
        columnas: int = 3,
        ancho_panel: float = 4.8,
        alto_panel: float = 3.8,
    ) -> None:
        if columnas < 1:
            raise ValueError("columnas debe ser mayor o igual que 1")
        if ancho_panel <= 0 or alto_panel <= 0:
            raise ValueError("el tamaño de panel debe ser positivo")
        self.titulo = titulo
        self.columnas = columnas
        self.ancho_panel = ancho_panel
        self.alto_panel = alto_panel
        self._paneles: list[_Panel] = []

    def imagen(
        self,
        nodo,
        titulo: str | None = None,
        *,
        rango: RangoImagen = "auto",
        cmap: str | None = None,
    ) -> Self:
        tensor = _tensor(nodo)
        nombre = titulo or getattr(nodo, "titulo", "Imagen")
        self._paneles.append(
            _Panel(lambda eje, t=tensor, n=nombre, r=rango, c=cmap: dibujar_imagen(eje, t, n, rango=r, cmap=c))
        )
        return self

    def senal(
        self,
        nodo,
        *,
        fila: int | None = None,
        canal: int = 0,
        titulo: str | None = None,
        etiqueta: str | None = None,
        cero: bool = False,
    ) -> Self:
        nombre = etiqueta or getattr(nodo, "titulo", "Señal")
        return self.senales((nodo, nombre), fila=fila, canal=canal, titulo=titulo, cero=cero)

    def senales(
        self,
        *series: tuple[object, str],
        fila: int | None = None,
        canal: int = 0,
        titulo: str | None = None,
        cero: bool = False,
        ylabel: str = "Intensidad",
    ) -> Self:
        if not series:
            raise ValueError("se necesita al menos una señal")
        tensores = [(_tensor(nodo), etiqueta) for nodo, etiqueta in series]
        fila_resuelta = tensores[0][0].shape[1] // 2 if fila is None else fila
        for tensor, _ in tensores:
            _validar_fila_canal(tensor, fila_resuelta, canal)
        nombre = titulo or f"Señal · fila {fila_resuelta}"

        def dibujar(eje: Axes) -> None:
            for tensor, etiqueta in tensores:
                valores = tensor[canal, fila_resuelta].detach().cpu().numpy()
                eje.plot(np.arange(valores.size), valores, label=etiqueta)
            if cero:
                eje.axhline(0, linewidth=1, alpha=0.5)
            eje.set(title=nombre, xlabel="j", ylabel=ylabel)
            eje.grid(alpha=0.25)
            if len(tensores) > 1:
                eje.legend()

        self._paneles.append(_Panel(dibujar))
        return self

    def espectro(self, espectro, titulo: str | None = None, *, logaritmica: bool = True) -> Self:
        magnitud = espectro.magnitud(logaritmica=logaritmica)
        nombre = titulo or ("TF centrada" if getattr(espectro, "centrado", False) else "TF")
        return self.imagen(magnitud, nombre, rango="unidad")

    def mascara(self, espectro, titulo: str | None = None) -> Self:
        nombre = titulo or f"H · {getattr(espectro, 'filtro', None) or 'Filtro'}"
        return self.imagen(espectro.mascara_imagen(), nombre, rango="unidad")

    def filtro(self, espectro, nombre: str | None = None, *, valor_absoluto: bool = False) -> Self:
        etiqueta = nombre or getattr(espectro, "filtro", None) or "Filtro"
        reconstruida = espectro.inversa(valor_absoluto=valor_absoluto)
        titulo_reconstruida = f"IFFT {etiqueta}"
        if reconstruida.min() < 0:
            titulo_reconstruida += f"\nmin={reconstruida.min():.3g}, max={reconstruida.max():.3g}"
        return (
            self.mascara(espectro, f"H {etiqueta}")
            .espectro(espectro, "TF · H")
            .imagen(reconstruida, titulo_reconstruida, rango="auto")
        )

    def vacio(self) -> Self:
        self._paneles.append(_Panel(lambda eje: eje.axis("off")))
        return self

    def mostrar(self, *, block: bool = True) -> Figure:
        if not self._paneles:
            raise ValueError("la gráfica no contiene paneles")
        filas = ceil(len(self._paneles) / self.columnas)
        figura, ejes = plt.subplots(
            filas,
            self.columnas,
            figsize=(self.columnas * self.ancho_panel, filas * self.alto_panel),
            squeeze=False,
            layout="constrained",
        )
        for eje, panel in zip(ejes.flat, self._paneles, strict=False):
            panel.dibujar(eje)
        for eje in tuple(ejes.flat)[len(self._paneles):]:
            eje.axis("off")
        if self.titulo:
            figura.suptitle(self.titulo)
        return presentar(figura, block, ajustar=False)

    def __len__(self) -> int:
        return len(self._paneles)


def dibujar_imagen(
    eje: Axes,
    tensor: torch.Tensor,
    titulo: str,
    *,
    rango: RangoImagen = "auto",
    cmap: str | None = None,
) -> None:
    if tensor.ndim != 3:
        raise ValueError(f"tensor debe usar layout CHW, shape={tuple(tensor.shape)}")
    mapa = cmap if cmap is not None else mapa_imagen(tensor)
    if tensor.shape[0] == 1:
        imagen = imagen_numpy(tensor, clip=False)
        vmin, vmax = resolver_rango(tensor, rango)
        eje.imshow(imagen, cmap=mapa, vmin=vmin, vmax=vmax)
    else:
        eje.imshow(imagen_numpy(tensor, clip=True), cmap=mapa)
    eje.set_title(titulo)
    eje.axis("off")


def imagen_numpy(tensor: torch.Tensor, *, clip: bool = True) -> np.ndarray:
    imagen = tensor.detach().cpu()
    if clip:
        imagen = imagen.clamp(0.0, 1.0)
    if tensor.shape[0] == 1:
        return imagen.squeeze(0).numpy()
    return imagen.permute(1, 2, 0).numpy()


def mapa_imagen(tensor: torch.Tensor) -> str | None:
    return "gray" if tensor.shape[0] == 1 else None


def resolver_rango(tensor: torch.Tensor, rango: RangoImagen) -> tuple[float | None, float | None]:
    if isinstance(rango, tuple):
        if len(rango) != 2 or rango[0] >= rango[1]:
            raise ValueError("rango debe ser (minimo, maximo) con minimo < maximo")
        return float(rango[0]), float(rango[1])
    if rango == "unidad":
        return 0.0, 1.0

    minimo = float(tensor.min().item())
    maximo = float(tensor.max().item())
    if rango == "simetrico" or (rango == "auto" and minimo < 0 < maximo):
        limite = max(abs(minimo), abs(maximo), 1e-12)
        return -limite, limite
    if rango != "auto":
        raise ValueError("rango debe ser 'auto', 'unidad', 'simetrico' o una tupla")
    if 0 <= minimo and maximo <= 1:
        return 0.0, 1.0
    if minimo == maximo:
        margen = max(abs(minimo) * 0.01, 1e-6)
        return minimo - margen, maximo + margen
    return minimo, maximo


def presentar(figura: Figure, block: bool, *, ajustar: bool = True) -> Figure:
    if ajustar:
        figura.tight_layout()
    if plt.get_backend().lower() != "agg":
        plt.show(block=block)
    return figura


def _tensor(nodo) -> torch.Tensor:
    tensor = nodo if isinstance(nodo, torch.Tensor) else getattr(nodo, "tensor", None)
    if not isinstance(tensor, torch.Tensor):
        raise TypeError("se esperaba VisionNode, EspectroNode o torch.Tensor")
    return tensor


def _validar_fila_canal(tensor: torch.Tensor, fila: int, canal: int) -> None:
    if not 0 <= fila < tensor.shape[1]:
        raise IndexError(f"fila fuera de rango: {fila}")
    if not 0 <= canal < tensor.shape[0]:
        raise IndexError(f"canal fuera de rango: {canal}")
