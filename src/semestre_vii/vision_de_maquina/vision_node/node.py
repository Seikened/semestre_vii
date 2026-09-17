import inspect
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

import numpy as np
import torch

from .espectro import EspectroNode
from .io import cargar_imagen, guardar_imagen
from .pixels import convoluciones, transformaciones, visualizacion
from .pixels.transformaciones import PuntosControl
from .signals import graficas
from .signals.frecuencias import EspectroCanal, analizar_espectros

_DTYPES_SOPORTADOS = frozenset({torch.float32, torch.float64})
_CANALES_SOPORTADOS = frozenset({1, 3})


@dataclass(frozen=True, slots=True, eq=False, repr=False, init=False)
class VisionNode:
    """Fachada Fluent para experimentar con tensores de imagen CHW."""

    tensor: torch.Tensor = field(repr=False)
    titulo: str = "Imagen"

    def __init__(
        self,
        tensor: torch.Tensor,
        titulo: str = "Imagen",
        *,
        title: str | None = None,
    ) -> None:
        if title is not None:
            if titulo != "Imagen":
                raise ValueError("usa titulo o title, no ambos")
            titulo = title
        object.__setattr__(self, "tensor", tensor)
        object.__setattr__(self, "titulo", titulo)
        self.__post_init__()

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

    @property
    def title(self) -> str:
        return self.titulo

    @property
    def channels(self) -> int:
        return self.canales

    @property
    def height(self) -> int:
        return self.alto

    @property
    def width(self) -> int:
        return self.ancho

    @property
    def is_grayscale(self) -> bool:
        return self.es_grises

    def max(self) -> float:
        return self.tensor.max().item()

    def min(self) -> float:
        return self.tensor.min().item()

    def to_numpy(self) -> np.ndarray:
        """Cruza explícitamente la frontera hacia NumPy, al estilo de una API de datos."""
        tensor = self.tensor.detach().cpu()
        if self.es_grises:
            return tensor[0].numpy()
        return tensor.permute(1, 2, 0).numpy()

    def guardar(self, ruta: str | Path) -> Self:
        guardar_imagen(self.tensor, ruta)
        return self

    def promediar(self, otros: Sequence[Self]) -> Self:
        tensores = [otro.tensor for otro in otros]
        tensor = transformaciones.promediar(self.tensor, tensores)
        return self._nuevo(tensor, f"Promedio de {len(otros) + 1} imágenes")

    def clip(self, minimo: float = 0.0, maximo: float = 1.0) -> Self:
        return self._nuevo(transformaciones.clip(self.tensor, minimo, maximo))

    def negativo(self) -> Self:
        return self._nuevo(transformaciones.negativo(self.tensor))

    def escala_grises(self) -> Self:
        return self._nuevo(transformaciones.escala_grises(self.tensor))

    def separar_canales(self) -> dict[str, Self]:
        canales = transformaciones.separar_canales(self.tensor)
        return {
            nombre: self._nuevo(tensor, f"Canal {nombre}") for nombre, tensor in canales.items()
        }

    def separar_hsv(self) -> dict[str, Self]:
        canales = transformaciones.separar_hsv(self.tensor)
        return {nombre: self._nuevo(tensor, nombre) for nombre, tensor in canales.items()}

    def saturacion(self) -> Self:
        return self._nuevo(transformaciones.saturacion(self.tensor), "Saturación")

    def acromaticidad(self) -> Self:
        return self._nuevo(transformaciones.acromaticidad(self.tensor), "Acromaticidad")

    def ganancia(self, factor: float) -> Self:
        return self._nuevo(transformaciones.ganancia(self.tensor, factor))

    def estirar_contraste(self) -> Self:
        return self._nuevo(transformaciones.estirar_contraste(self.tensor))

    def binarizar(self, umbral: float = 0.5) -> Self:
        return self._nuevo(transformaciones.binarizar(self.tensor, umbral))

    def binarizar_rango(self, minimo: float, maximo: float) -> Self:
        tensor = transformaciones.binarizar_rango(self.tensor, minimo, maximo)
        return self._nuevo(tensor)

    def binarizar_adaptativo(self, kernel_size: int = 15, c: float = 0.05) -> Self:
        tensor = transformaciones.binarizar_adaptativo(self.tensor, kernel_size, c)
        return self._nuevo(tensor)

    def transformacion_log(self) -> Self:
        return self._nuevo(transformaciones.transformacion_log(self.tensor))

    def transformacion_gamma(self, exponente: float) -> Self:
        tensor = transformaciones.transformacion_gamma(self.tensor, exponente)
        return self._nuevo(tensor)

    def cuantizar(self, bits: int = 8) -> Self:
        return self._nuevo(transformaciones.cuantizar(self.tensor, bits))

    def pseudocolor_infrarrojo(self, mapa: str = "inferno") -> Self:
        return self._nuevo(transformaciones.pseudocolor_infrarrojo(self.tensor, mapa))

    def falso_color_infrarrojo(self) -> Self:
        return self._nuevo(transformaciones.falso_color_infrarrojo(self.tensor))

    def transformacion_lineal(
        self,
        entrada: Sequence[float],
        salida: Sequence[float],
        *,
        show_transform: bool = False,
    ) -> Self:
        tensor = transformaciones.transformacion_lineal(self.tensor, entrada, salida)
        if show_transform:
            visualizacion.graficar_transformacion_lineal(entrada, salida)
        return self._nuevo(tensor)

    def transformacion_lineal_por_canal(
        self,
        rojo: PuntosControl,
        verde: PuntosControl,
        azul: PuntosControl,
        *,
        show_transform: bool = False,
    ) -> Self:
        tensor = transformaciones.transformacion_lineal_por_canal(
            self.tensor,
            rojo,
            verde,
            azul,
        )
        if show_transform:
            visualizacion.graficar_transformaciones_rgb(rojo, verde, azul)
        return self._nuevo(tensor)

    def ecualizar(self) -> Self:
        return self._nuevo(transformaciones.ecualizar(self.tensor))

    def convolucion(
        self,
        kernel: np.ndarray | torch.Tensor,
        *,
        flip_kernel: bool = False,
    ) -> Self:
        tensor = convoluciones.convolucion(self.tensor, kernel, flip_kernel=flip_kernel)
        return self._nuevo(tensor)

    def convolucion_separable(self, kernel_1d: np.ndarray | torch.Tensor) -> Self:
        return self._nuevo(convoluciones.convolucion_separable(self.tensor, kernel_1d))

    def suavizar(self, size: int = 3) -> Self:
        return self._nuevo(convoluciones.suavizar(self.tensor, size))

    def piramidal(self, size: int = 3) -> Self:
        return self._nuevo(convoluciones.piramidal(self.tensor, size))

    def gaussiano(self, size: int = 3, sigma: float | None = None) -> Self:
        return self._nuevo(convoluciones.gaussiano(self.tensor, size, sigma))

    def mediana_cruz(self, size: int = 5) -> Self:
        return self._nuevo(convoluciones.mediana_cruz(self.tensor, size))

    def mediana(self, size: int = 3) -> Self:
        return self._nuevo(convoluciones.mediana(self.tensor, size))

    def filtro_sigma(self, size: int = 5, sigma: float = 10.0) -> Self:
        return self._nuevo(convoluciones.filtro_sigma(self.tensor, size, sigma))

    def filtro_umbral(self, filtrada: Self, umbral: float = 0.15) -> Self:
        tensor = convoluciones.filtro_umbral(self.tensor, filtrada.tensor, umbral)
        return self._nuevo(tensor)

    def sal_y_pimienta(
        self,
        cantidad: float = 0.05,
        proporcion_sal: float = 0.5,
        seed: int | None = None,
    ) -> Self:
        tensor = convoluciones.sal_y_pimienta(self.tensor, cantidad, proporcion_sal, seed)
        return self._nuevo(tensor)

    def ruido_uniforme(self, amplitud: float = 0.1, seed: int | None = None) -> Self:
        return self._nuevo(convoluciones.ruido_uniforme(self.tensor, amplitud, seed))

    def laplaciano(
        self,
        *,
        extendido: bool = False,
        valor_absoluto: bool = True,
        crudo: bool = False,
    ) -> Self:
        tensor = convoluciones.laplaciano(
            self.tensor,
            extendido=extendido,
            valor_absoluto=valor_absoluto,
            crudo=crudo,
        )
        return self._nuevo(tensor)

    def fft(self, *, centrado: bool = True) -> EspectroNode:
        """Transforma la imagen al dominio de Fourier y devuelve un nodo fluido de espectro."""
        return EspectroNode.desde_imagen(self, centrado=centrado)

    def fourier(self, *, centrado: bool = True) -> EspectroNode:
        """Alias descriptivo de :meth:`fft`."""
        return self.fft(centrado=centrado)

    def pasabajas_ideal(self, corte: float) -> Self:
        return self.fft().pasabajas_ideal(corte).inversa()

    def pasabajas_gaussiano(self, corte: float) -> Self:
        return self.fft().pasabajas_gaussiano(corte).inversa()

    def pasabajas_butterworth(self, corte: float, orden: int = 2) -> Self:
        return self.fft().pasabajas_butterworth(corte, orden).inversa()

    def pasaaltas_ideal(self, corte: float) -> Self:
        return self.fft().pasaaltas_ideal(corte).inversa()

    def pasaaltas_gaussiano(self, corte: float) -> Self:
        return self.fft().pasaaltas_gaussiano(corte).inversa()

    def pasaaltas_butterworth(self, corte: float, orden: int = 2) -> Self:
        return self.fft().pasaaltas_butterworth(corte, orden).inversa()

    def picos_espectrales(
        self,
        n_picos: int = 6,
        excluir_radio_dc: int = 20,
        distancia_minima: int = 5,
    ) -> tuple[EspectroCanal, ...]:
        return analizar_espectros(
            self.tensor,
            n_picos=n_picos,
            excluir_radio_dc=excluir_radio_dc,
            distancia_minima=distancia_minima,
        )

    def mostrar(self, block: bool = True) -> Self:
        visualizacion.mostrar(self.tensor, self.titulo, block=block)
        return self

    def mostrar_diferencias(
        self,
        comparada: Self,
        magnifier: float = 1.0,
        block: bool = True,
    ) -> Self:
        visualizacion.mostrar_diferencias(
            self.tensor,
            comparada.tensor,
            self.titulo,
            comparada.titulo,
            magnifier=magnifier,
            block=block,
        )
        tensor = transformaciones.diferencia_absoluta(
            self.tensor,
            comparada.tensor,
            magnifier,
        )
        titulo = f"Diferencias: {self.titulo} vs {comparada.titulo}"
        return self._nuevo(tensor, titulo)

    def histograma(self, block: bool = True) -> Self:
        visualizacion.histograma(self.tensor, self.titulo, block=block)
        return self

    def graficar_acumulado(self, title_suffix: str = "", block: bool = False) -> Self:
        titulo = self.titulo
        if title_suffix:
            titulo = f"{titulo} ({title_suffix})"
        visualizacion.graficar_acumulado(self.tensor, titulo, block=block)
        return self

    def mostrar_reporte(self, block: bool = True) -> Self:
        visualizacion.mostrar_reporte(self.tensor, self.titulo, block=block)
        return self

    def senal_por_canal(
        self,
        fila: int | None = None,
        block: bool = False,
        excluir_dc: bool = False,
        magnifier: float = 1.0,
    ) -> Self:
        graficas.senal_por_canal(
            self.tensor,
            self.titulo,
            fila=fila,
            block=block,
            excluir_dc=excluir_dc,
            magnifier=magnifier,
        )
        return self

    def comparar_fft(
        self,
        comparada: Self,
        fila: int | None = None,
        block: bool = False,
        excluir_dc: bool = False,
    ) -> Self:
        graficas.comparar_fft(
            self.tensor,
            comparada.tensor,
            self.titulo,
            comparada.titulo,
            fila=fila,
            block=block,
            excluir_dc=excluir_dc,
        )
        return self

    def transformada_fourier_2d(self, block: bool = False) -> Self:
        graficas.transformada_fourier_2d(self.tensor, self.titulo, block=block)
        return self

    def espectro_2d_picos(
        self,
        n_picos: int = 6,
        excluir_radio_dc: int = 20,
        ventana_supresion: int = 10,
        radio_marcador: int = 12,
        radio_dc_visual: int = 5,
        clip_percentil: float = 99.5,
        block: bool = False,
    ) -> Self:
        graficas.espectro_2d_picos(
            self.tensor,
            self.titulo,
            n_picos=n_picos,
            excluir_radio_dc=excluir_radio_dc,
            ventana_supresion=ventana_supresion,
            radio_marcador=radio_marcador,
            radio_dc_visual=radio_dc_visual,
            clip_percentil=clip_percentil,
            block=block,
        )
        return self

    def espectro_2d_con_perfiles(
        self,
        n_picos: int = 8,
        excluir_radio_dc: int = 20,
        ventana_supresion: int = 10,
        radio_marcador: int = 12,
        radio_dc_visual: int = 5,
        clip_percentil: float = 99.5,
        escala_perfiles: str = "lineal",
        block: bool = False,
    ) -> Self:
        graficas.espectro_2d_con_perfiles(
            self.tensor,
            self.titulo,
            n_picos=n_picos,
            excluir_radio_dc=excluir_radio_dc,
            ventana_supresion=ventana_supresion,
            radio_marcador=radio_marcador,
            radio_dc_visual=radio_dc_visual,
            clip_percentil=clip_percentil,
            escala_perfiles=escala_perfiles,
            block=block,
        )
        return self

    @classmethod
    def describir_api(cls) -> str:
        filas = []
        for nombre, metodo in inspect.getmembers(cls, predicate=callable):
            if nombre.startswith("_"):
                continue
            resumen = inspect.getdoc(metodo) or ""
            descripcion = (
                resumen.splitlines()[0] if resumen else nombre.replace("_", " ").capitalize()
            )
            firma = f"{nombre}{inspect.signature(metodo)}"
            filas.append((firma, descripcion))
        ancho = max(len(firma) for firma, _ in filas)
        tabla = "\n".join(f"{firma.ljust(ancho)}  {descripcion}" for firma, descripcion in filas)
        print(tabla)
        return tabla

    def __add__(self, otro: object) -> Self:
        return self._combinar(otro, "+", lambda a, b: a + b)

    def __sub__(self, otro: object) -> Self:
        return self._combinar(otro, "-", lambda a, b: a - b)

    def __mul__(self, otro: object) -> Self:
        return self._combinar(otro, "*", lambda a, b: a * b)

    def __truediv__(self, otro: object) -> Self:
        return self._combinar(otro, "/", lambda a, b: a / b)

    def __radd__(self, otro: object) -> Self:
        return self._combinar(otro, "+", lambda a, b: b + a)

    def __rsub__(self, otro: object) -> Self:
        return self._combinar(otro, "-", lambda a, b: b - a)

    def __rmul__(self, otro: object) -> Self:
        return self._combinar(otro, "*", lambda a, b: b * a)

    def __rtruediv__(self, otro: object) -> Self:
        return self._combinar(otro, "/", lambda a, b: b / a)

    def __neg__(self) -> Self:
        return self._nuevo(-self.tensor, f"(-{self.titulo})")

    def __repr__(self) -> str:
        return (
            f"VisionNode(shape={self.shape!r}, dtype={self.dtype}, "
            f"device={self.device}, titulo={self.titulo!r})"
        )

    def _combinar(self, otro: object, simbolo: str, operacion) -> Self:
        operando = otro.tensor if isinstance(otro, VisionNode) else otro
        titulo = otro.titulo if isinstance(otro, VisionNode) else str(otro)
        tensor = operacion(self.tensor, operando)
        return self._nuevo(tensor, f"({self.titulo} {simbolo} {titulo})")

    def _nuevo(self, tensor: torch.Tensor, titulo: str | None = None) -> Self:
        return type(self)(tensor=tensor, titulo=self.titulo if titulo is None else titulo)


def _validar_tensor(tensor: torch.Tensor) -> None:
    if not isinstance(tensor, torch.Tensor):
        raise TypeError("tensor debe ser torch.Tensor")
    if tensor.ndim != 3:
        raise ValueError(f"tensor debe usar layout CHW, shape={tuple(tensor.shape)}")
    if tensor.shape[0] not in _CANALES_SOPORTADOS:
        raise ValueError(f"tensor debe tener 1 o 3 canales, canales={tensor.shape[0]}")
    _validar_dtype(tensor.dtype)


def _validar_dtype(dtype: torch.dtype) -> None:
    if dtype not in _DTYPES_SOPORTADOS:
        raise ValueError(f"dtype debe ser float32 o float64, dtype={dtype}")
