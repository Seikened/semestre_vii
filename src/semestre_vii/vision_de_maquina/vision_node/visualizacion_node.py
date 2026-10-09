from typing import Self

import torch

from .pixels import transformaciones, visualizacion
from .signals import graficas


class VisualizacionNode:
    """Métodos de presentación exclusivos de VisionNode."""

    __slots__ = ()
    tensor: torch.Tensor
    titulo: str

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
