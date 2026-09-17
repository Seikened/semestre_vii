import numpy as np
import torch

from semestre_vii.vision_de_maquina.vision_node import EspectroNode, VisionNode


def _patron(size: int = 32) -> VisionNode:
    x = torch.arange(size, dtype=torch.float32)
    fila = ((x // 4) % 2).to(torch.float32)
    return VisionNode(fila.repeat(size, 1).unsqueeze(0), titulo="Patrón")


def test_fft_entra_a_un_objeto_de_dominio_espectral() -> None:
    espectro = _patron().fft()

    assert isinstance(espectro, EspectroNode)
    assert espectro.centrado
    assert torch.is_complex(espectro.tensor)
    assert espectro.shape == (1, 32, 32)


def test_fft_inversa_recupera_la_imagen() -> None:
    imagen = _patron()
    reconstruida = imagen.fft().inversa()

    torch.testing.assert_close(reconstruida.tensor, imagen.tensor, atol=1e-5, rtol=1e-5)


def test_filtros_espectrales_se_encadenan_sin_salir_de_la_api() -> None:
    espectro = _patron().fft()
    filtrado = espectro.pasabajas_butterworth(6, orden=2)

    assert isinstance(filtrado, EspectroNode)
    assert filtrado.filtro == "BLPF(D0=6, n=2)"
    assert filtrado.mascara_imagen().shape == (1, 32, 32)
    assert filtrado.inversa().shape == (1, 32, 32)


def test_ifft_pasaaltas_conserva_valores_negativos_por_defecto() -> None:
    tensor = torch.zeros((1, 32, 32), dtype=torch.float32)
    tensor[0, 16, 16] = 1
    imagen = VisionNode(tensor)

    reconstruida = imagen.fft().pasaaltas_gaussiano(4).inversa()

    assert reconstruida.min() < 0
    assert reconstruida.max() > 0


def test_to_numpy_es_frontera_explicita_para_visualizacion() -> None:
    imagen = _patron(8)
    arreglo = imagen.to_numpy()

    assert isinstance(arreglo, np.ndarray)
    assert arreglo.shape == (8, 8)
