import matplotlib.pyplot as plt
import numpy as np
import torch

from semestre_vii.vision_de_maquina.vision_node import VisionNode, graficas_frecuencia
from semestre_vii.vision_de_maquina.vision_node.frecuencias import analizar_espectros, senales_fila


def _patron_periodico(size: int = 32) -> torch.Tensor:
    x = torch.arange(size, dtype=torch.float32)
    fila = (torch.sin(2 * torch.pi * 4 * x / size) + 1) / 2
    return fila.repeat(size, 1).unsqueeze(0)


def test_senales_fila_entrega_senal_y_fft_real() -> None:
    tensor = _patron_periodico()

    senales = senales_fila(tensor, 10, excluir_dc=True)

    assert len(senales) == 1
    assert senales[0].intensidades.shape == (32,)
    assert senales[0].frecuencias.shape == (17,)
    assert senales[0].magnitudes.shape == (17,)
    assert senales[0].magnitudes[0] == 0


def test_analisis_espectral_detecta_el_periodo_principal() -> None:
    espectros = analizar_espectros(
        _patron_periodico(),
        n_picos=2,
        excluir_radio_dc=1,
        distancia_minima=2,
    )

    periodos = [pico.periodo_px for pico in espectros[0].picos]

    assert len(periodos) == 2
    assert any(np.isclose(periodo, 8.0) for periodo in periodos)
    assert np.allclose(np.log1p(espectros[0].magnitud_lineal), espectros[0].magnitud)


def test_node_expone_resultados_espectrales_como_datos() -> None:
    node = VisionNode(_patron_periodico())

    espectros = node.picos_espectrales(2, excluir_radio_dc=1, distancia_minima=2)

    assert espectros[0].nombre == "B/N"
    assert len(espectros[0].picos) == 2


def test_graficas_de_frecuencia_conservan_la_api_fluent() -> None:
    node = VisionNode(_patron_periodico(16), titulo="Patrón")

    assert node.senal_por_canal(fila=5, block=False, excluir_dc=True) is node
    assert node.comparar_fft(node.gaussiano(), fila=5, block=False, excluir_dc=True) is node
    assert node.transformada_fourier_2d(block=False) is node
    assert node.espectro_2d_picos(2, excluir_radio_dc=1, block=False) is node
    assert (
        node.espectro_2d_con_perfiles(
            2,
            excluir_radio_dc=1,
            escala_perfiles="log",
            block=False,
        )
        is node
    )
    plt.close("all")


def test_perfiles_espectrales_alinean_ejes_y_marcan_picos() -> None:
    figura = graficas_frecuencia.espectro_2d_con_perfiles(
        _patron_periodico(),
        "Patrón",
        n_picos=2,
        excluir_radio_dc=1,
        ventana_supresion=2,
        escala_perfiles="log",
        block=False,
    )
    perfil_horizontal = figura.axes[1]
    perfil_vertical = figura.axes[2]

    assert perfil_horizontal.get_yscale() == "log"
    assert perfil_vertical.get_xscale() == "log"
    assert perfil_vertical.yaxis_inverted()
    assert len(perfil_horizontal.lines) == 3
    assert len(perfil_vertical.lines) == 3
    assert any("T≈" in texto.get_text() for texto in figura.axes[0].texts)
    plt.close(figura)


def test_senal_por_canal_incluye_lupa_interactiva() -> None:
    figura = graficas_frecuencia.senal_por_canal(
        _patron_periodico(),
        "Patrón",
        fila=4,
        block=False,
    )

    assert any(eje.get_title() == "Lupa" for eje in figura.axes[0].child_axes)
    assert figura.vision_node_lupa_callback > 0
    plt.close(figura)
