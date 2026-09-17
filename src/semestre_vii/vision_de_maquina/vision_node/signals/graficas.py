"""Gráficas interactivas de señales y espectros."""

import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.figure import Figure
from matplotlib.widgets import Slider

from ..grafica import imagen_numpy as _imagen_numpy
from ..grafica import mapa_imagen as _mapa_imagen
from ..grafica import presentar as _presentar
from .frecuencias import EspectroCanal, analizar_espectros, senales_fila


def senal_por_canal(
    tensor: torch.Tensor,
    titulo: str,
    *,
    fila: int | None = None,
    block: bool = False,
    excluir_dc: bool = False,
    magnifier: float = 1.0,
) -> Figure:
    fila = tensor.shape[1] // 2 if fila is None else fila
    if magnifier <= 0:
        raise ValueError("magnifier debe ser mayor que cero")
    senales = senales_fila(tensor, fila, excluir_dc=excluir_dc)
    figura, ejes = plt.subplots(
        len(senales) + 1,
        2,
        figsize=(14 * magnifier, (4 + 3 * len(senales)) * magnifier),
        squeeze=False,
    )
    figura.subplots_adjust(bottom=0.12)
    eje_imagen = ejes[0, 0]
    eje_imagen.imshow(_imagen_numpy(tensor), cmap=_mapa_imagen(tensor), vmin=0, vmax=1)
    linea_fila = eje_imagen.axhline(fila, color="yellow", linewidth=1)
    eje_imagen.set_title(titulo)
    eje_imagen.axis("off")
    ejes[0, 1].axis("off")
    lupa = eje_imagen.inset_axes((0.66, 0.62, 0.32, 0.34))
    lupa.imshow(_imagen_numpy(tensor), cmap=_mapa_imagen(tensor), vmin=0, vmax=1)
    lupa.set_title("Lupa", fontsize=8)
    lupa.set_xticks([])
    lupa.set_yticks([])
    _centrar_lupa(lupa, tensor.shape[2] / 2, tensor.shape[1] / 2, tensor.shape, magnifier)

    lineas = []
    for indice, senal in enumerate(senales, start=1):
        linea_espacial = ejes[indice, 0].plot(
            senal.intensidades,
            color=senal.color,
        )[0]
        linea_fft = ejes[indice, 1].plot(
            senal.frecuencias,
            senal.magnitudes,
            color=senal.color,
        )[0]
        ejes[indice, 0].set(
            title=f"Señal: {senal.nombre}",
            xlabel="Columna",
            ylabel="Intensidad",
            ylim=(0, 1),
        )
        ejes[indice, 1].set(
            title=f"FFT: {senal.nombre}",
            xlabel="Frecuencia normalizada",
            ylabel="Magnitud",
        )
        lineas.append((linea_espacial, linea_fft, ejes[indice, 1]))

    eje_slider = figura.add_axes((0.18, 0.035, 0.64, 0.025))
    slider = Slider(eje_slider, "Fila", 0, tensor.shape[1] - 1, valinit=fila, valstep=1)

    def actualizar(valor: float) -> None:
        nueva_fila = int(valor)
        linea_fila.set_ydata([nueva_fila, nueva_fila])
        nuevas_senales = senales_fila(tensor, nueva_fila, excluir_dc=excluir_dc)
        for referencia, senal in zip(lineas, nuevas_senales, strict=True):
            linea_espacial, linea_fft, eje_fft = referencia
            linea_espacial.set_ydata(senal.intensidades)
            linea_fft.set_ydata(senal.magnitudes)
            eje_fft.relim()
            eje_fft.autoscale_view()
        figura.canvas.draw_idle()

    slider.on_changed(actualizar)
    callback_lupa = figura.canvas.mpl_connect(
        "motion_notify_event",
        lambda evento: _mover_lupa(evento, eje_imagen, lupa, tensor.shape, magnifier),
    )
    figura.vision_node_slider = slider
    figura.vision_node_lupa_callback = callback_lupa
    return _presentar(figura, block, ajustar=False)


def comparar_fft(
    tensor: torch.Tensor,
    comparada: torch.Tensor,
    titulo: str,
    titulo_comparada: str,
    *,
    fila: int | None = None,
    block: bool = False,
    excluir_dc: bool = False,
) -> Figure:
    if tensor.shape != comparada.shape:
        raise ValueError(f"shape incompatible: {tuple(comparada.shape)} vs {tuple(tensor.shape)}")
    fila = tensor.shape[1] // 2 if fila is None else fila
    originales = senales_fila(tensor, fila, excluir_dc=excluir_dc)
    comparadas = senales_fila(comparada, fila, excluir_dc=excluir_dc)
    figura, ejes = plt.subplots(len(originales) + 1, 2, figsize=(14, 4 + 3 * len(originales)))
    figura.subplots_adjust(bottom=0.12)
    lineas_fila = []
    for eje, imagen, nombre in zip(
        ejes[0],
        (tensor, comparada),
        (titulo, titulo_comparada),
        strict=True,
    ):
        eje.imshow(_imagen_numpy(imagen), cmap=_mapa_imagen(imagen), vmin=0, vmax=1)
        lineas_fila.append(eje.axhline(fila, color="yellow", linewidth=1))
        eje.set_title(nombre)
        eje.axis("off")

    referencias = []
    for indice, (original, filtrada) in enumerate(
        zip(originales, comparadas, strict=True), start=1
    ):
        eje = ejes[indice, 0]
        linea_original = eje.plot(original.frecuencias, original.magnitudes, label=titulo)[0]
        linea_comparada = eje.plot(
            filtrada.frecuencias, filtrada.magnitudes, label=titulo_comparada
        )[0]
        eje.set(title=f"FFT: {original.nombre}", xlabel="Frecuencia", ylabel="Magnitud")
        eje.legend()
        referencias.append((linea_original, linea_comparada, eje))
        ejes[indice, 1].axis("off")

    eje_slider = figura.add_axes((0.18, 0.035, 0.64, 0.025))
    slider = Slider(eje_slider, "Fila", 0, tensor.shape[1] - 1, valinit=fila, valstep=1)

    def actualizar(valor: float) -> None:
        nueva_fila = int(valor)
        for linea in lineas_fila:
            linea.set_ydata([nueva_fila, nueva_fila])
        nuevas_originales = senales_fila(tensor, nueva_fila, excluir_dc=excluir_dc)
        nuevas_comparadas = senales_fila(comparada, nueva_fila, excluir_dc=excluir_dc)
        for referencia, original, filtrada in zip(
            referencias,
            nuevas_originales,
            nuevas_comparadas,
            strict=True,
        ):
            linea_original, linea_comparada, eje = referencia
            linea_original.set_ydata(original.magnitudes)
            linea_comparada.set_ydata(filtrada.magnitudes)
            eje.relim()
            eje.autoscale_view()
        figura.canvas.draw_idle()

    slider.on_changed(actualizar)
    figura.vision_node_slider = slider
    return _presentar(figura, block, ajustar=False)


def transformada_fourier_2d(
    tensor: torch.Tensor,
    titulo: str,
    *,
    block: bool = False,
) -> Figure:
    espectros = analizar_espectros(tensor)
    figura, ejes = plt.subplots(1, len(espectros) + 1, figsize=(6 * (len(espectros) + 1), 5))
    ejes[0].imshow(_imagen_numpy(tensor), cmap=_mapa_imagen(tensor), vmin=0, vmax=1)
    ejes[0].set_title(titulo)
    ejes[0].axis("off")
    for eje, espectro in zip(ejes[1:], espectros, strict=True):
        eje.imshow(espectro.magnitud, cmap="magma")
        eje.set_title(f"FFT 2D: {espectro.nombre}")
        eje.axis("off")
    return _presentar(figura, block)


def espectro_2d_picos(
    tensor: torch.Tensor,
    titulo: str,
    *,
    n_picos: int = 6,
    excluir_radio_dc: int = 20,
    ventana_supresion: int = 10,
    radio_marcador: int = 12,
    radio_dc_visual: int = 5,
    clip_percentil: float = 99.5,
    block: bool = False,
) -> Figure:
    espectros = analizar_espectros(
        tensor,
        n_picos=n_picos,
        excluir_radio_dc=excluir_radio_dc,
        distancia_minima=ventana_supresion,
    )
    figura, ejes = plt.subplots(1, len(espectros), figsize=(6 * len(espectros), 5), squeeze=False)
    for eje, espectro in zip(ejes[0], espectros, strict=True):
        _dibujar_espectro(
            eje,
            espectro,
            f"{titulo}: {espectro.nombre}",
            radio_marcador=radio_marcador,
            radio_dc_visual=radio_dc_visual,
            clip_percentil=clip_percentil,
        )
    return _presentar(figura, block)


def espectro_2d_con_perfiles(
    tensor: torch.Tensor,
    titulo: str,
    *,
    n_picos: int = 8,
    excluir_radio_dc: int = 20,
    ventana_supresion: int = 10,
    radio_marcador: int = 12,
    radio_dc_visual: int = 5,
    clip_percentil: float = 99.5,
    escala_perfiles: str = "lineal",
    block: bool = False,
) -> Figure:
    if escala_perfiles not in ("lineal", "log"):
        raise ValueError("escala_perfiles debe ser 'lineal' o 'log'")
    espectros = analizar_espectros(
        tensor,
        n_picos=n_picos,
        excluir_radio_dc=excluir_radio_dc,
        distancia_minima=ventana_supresion,
    )
    figura, ejes = plt.subplots(len(espectros), 3, figsize=(18, 5 * len(espectros)), squeeze=False)
    for fila_ejes, espectro in zip(ejes, espectros, strict=True):
        _dibujar_espectro(
            fila_ejes[0],
            espectro,
            f"{titulo}: {espectro.nombre}",
            radio_marcador=radio_marcador,
            radio_dc_visual=radio_dc_visual,
            clip_percentil=clip_percentil,
        )
        magnitud_perfiles = _suprimir_dc(espectro.magnitud_lineal, excluir_radio_dc)
        fila_ejes[1].plot(magnitud_perfiles.max(axis=0), color=espectro.color)
        fila_ejes[1].set(title="Perfil horizontal máximo", xlabel="Columna", ylabel="Magnitud")
        fila_ejes[2].plot(magnitud_perfiles.max(axis=1), np.arange(magnitud_perfiles.shape[0]))
        fila_ejes[2].set(title="Perfil vertical máximo", xlabel="Magnitud", ylabel="Fila")
        fila_ejes[2].set_ylim(magnitud_perfiles.shape[0] - 1, 0)
        for pico in espectro.picos:
            fila_ejes[1].axvline(pico.columna, color="red", linestyle=":", linewidth=0.8)
            fila_ejes[2].axhline(pico.fila, color="red", linestyle=":", linewidth=0.8)
        if escala_perfiles == "log":
            fila_ejes[1].set_yscale("log")
            fila_ejes[2].set_xscale("log")
    return _presentar(figura, block)


def _dibujar_espectro(
    eje,
    espectro: EspectroCanal,
    titulo: str,
    *,
    radio_marcador: int = 12,
    radio_dc_visual: int = 0,
    clip_percentil: float = 100,
) -> None:
    magnitud = _normalizar_espectro(espectro.magnitud, radio_dc_visual, clip_percentil)
    eje.imshow(magnitud, cmap="magma", vmin=0, vmax=1)
    for indice, pico in enumerate(espectro.picos, start=1):
        eje.plot(
            pico.columna,
            pico.fila,
            marker="o",
            markersize=max(3, radio_marcador / 2),
            markerfacecolor="none",
            color="cyan",
        )
        etiqueta = (
            f"#{indice}\n"
            f"({pico.desplazamiento_x:+d},{pico.desplazamiento_y:+d})\n"
            f"T≈{pico.periodo_px:.1f}px"
        )
        eje.annotate(etiqueta, (pico.columna, pico.fila), color="white", fontsize=7)
    eje.set_title(titulo)
    eje.axis("off")


def _normalizar_espectro(
    magnitud: np.ndarray,
    radio_dc: int,
    clip_percentil: float,
) -> np.ndarray:
    if not 0 < clip_percentil <= 100:
        raise ValueError("clip_percentil debe estar entre cero y cien")
    visible = _suprimir_dc(magnitud, radio_dc)
    limite = np.percentile(visible, clip_percentil)
    if limite <= 0:
        return np.zeros_like(visible)
    return np.clip(visible / limite, 0, 1)


def _suprimir_dc(magnitud: np.ndarray, radio: int) -> np.ndarray:
    if radio < 0:
        raise ValueError("radio debe ser mayor o igual a cero")
    resultado = magnitud.copy()
    if radio == 0:
        return resultado
    centro_y = resultado.shape[0] // 2
    centro_x = resultado.shape[1] // 2
    filas, columnas = np.ogrid[: resultado.shape[0], : resultado.shape[1]]
    mascara = (filas - centro_y) ** 2 + (columnas - centro_x) ** 2 <= radio**2
    resultado[mascara] = 0
    return resultado


def _mover_lupa(evento, eje_imagen, lupa, shape: tuple[int, int, int], zoom: float) -> None:
    if evento.inaxes is not eje_imagen or evento.xdata is None or evento.ydata is None:
        return
    _centrar_lupa(lupa, evento.xdata, evento.ydata, shape, zoom)
    eje_imagen.figure.canvas.draw_idle()


def _centrar_lupa(
    lupa,
    centro_x: float,
    centro_y: float,
    shape: tuple[int, int, int],
    zoom: float,
) -> None:
    _, alto, ancho = shape
    radio_x = max(ancho / (8 * zoom), 1)
    radio_y = max(alto / (8 * zoom), 1)
    lupa.set_xlim(centro_x - radio_x, centro_x + radio_x)
    lupa.set_ylim(centro_y + radio_y, centro_y - radio_y)
