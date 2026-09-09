import numpy as np
import pytest
import torch

from semestre_vii.vision_de_maquina.vision_node import VisionNode


def test_convoluciones_identidad_conservan_el_tensor() -> None:
    tensor = torch.rand(1, 7, 7)
    node = VisionNode(tensor)
    kernel_2d = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
    kernel_1d = np.array([0, 1, 0])

    resultado_2d = node.convolucion(kernel_2d)
    resultado_separable = node.convolucion_separable(kernel_1d)

    assert torch.allclose(resultado_2d.tensor, tensor)
    assert torch.allclose(resultado_separable.tensor, tensor)


@pytest.mark.parametrize("metodo", ["suavizar", "piramidal", "gaussiano", "mediana"])
def test_convoluciones_establecidas_conservan_shape_y_rango(metodo: str) -> None:
    node = VisionNode(torch.rand(3, 9, 9))

    resultado = getattr(node, metodo)(3)

    assert resultado.shape == node.shape
    assert resultado.min() >= 0
    assert resultado.max() <= 1


def test_mediana_cruz_elimina_un_impulso_aislado() -> None:
    tensor = torch.zeros(1, 7, 7)
    tensor[0, 3, 3] = 1

    resultado = VisionNode(tensor).mediana_cruz(3)

    assert resultado.tensor[0, 3, 3] == 0


def test_filtro_sigma_preserva_shape_y_rango() -> None:
    generador = torch.Generator().manual_seed(4)
    tensor = 0.5 + (torch.rand((1, 21, 21), generator=generador) - 0.5) * 0.04
    node = VisionNode(tensor)

    resultado = node.filtro_sigma(5, sigma=10)

    assert resultado.shape == node.shape
    assert resultado.min() >= 0
    assert resultado.max() <= 1
    assert resultado.tensor.var() < node.tensor.var()


def test_filtro_umbral_sustituye_solo_diferencias_grandes() -> None:
    original = VisionNode(torch.tensor([[[0.1, 0.5, 0.9]]]))
    filtrada = VisionNode(torch.tensor([[[0.2, 0.55, 0.4]]]))

    resultado = original.filtro_umbral(filtrada, umbral=0.15)

    assert torch.allclose(resultado.tensor, torch.tensor([[[0.1, 0.5, 0.4]]]))


def test_ruidos_con_seed_son_reproducibles() -> None:
    node = VisionNode(torch.full((1, 20, 20), 0.5))

    uniforme_a = node.ruido_uniforme(seed=7)
    uniforme_b = node.ruido_uniforme(seed=7)
    impulsivo_a = node.sal_y_pimienta(cantidad=0.2, seed=7)
    impulsivo_b = node.sal_y_pimienta(cantidad=0.2, seed=7)

    assert torch.equal(uniforme_a.tensor, uniforme_b.tensor)
    assert torch.equal(impulsivo_a.tensor, impulsivo_b.tensor)
    assert set(impulsivo_a.tensor.unique().tolist()) <= {0.0, 0.5, 1.0}


def test_laplaciano_detecta_un_impulso() -> None:
    tensor = torch.zeros(1, 7, 7)
    tensor[0, 3, 3] = 1

    resultado = VisionNode(tensor).laplaciano()
    crudo = VisionNode(tensor).laplaciano(crudo=True)

    assert resultado.max() == 1
    assert crudo.tensor[0, 3, 3] < 0
