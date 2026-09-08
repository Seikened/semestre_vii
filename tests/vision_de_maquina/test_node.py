import pytest
import torch

from semestre_vii.vision_de_maquina.vision_node import VisionNode


def test_node_expone_metadatos_del_tensor_chw() -> None:
    tensor = torch.zeros(3, 5, 7, dtype=torch.float64)

    node = VisionNode(tensor, titulo="Prueba")

    assert node.shape == (3, 5, 7)
    assert node.canales == 3
    assert node.alto == 5
    assert node.ancho == 7
    assert node.dtype is torch.float64
    assert node.device == tensor.device
    assert not node.es_grises
    assert "shape=(3, 5, 7)" in repr(node)


@pytest.mark.parametrize(
    ("tensor", "error"),
    [
        ("no es tensor", TypeError),
        (torch.zeros(3, 4), ValueError),
        (torch.zeros(2, 4, 4), ValueError),
        (torch.zeros(3, 4, 4, dtype=torch.int64), ValueError),
    ],
)
def test_node_rechaza_tensores_fuera_del_contrato(
    tensor: object,
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        VisionNode(tensor)


def test_cadena_fluent_devuelve_nodos_nuevos_sin_mutar_el_origen() -> None:
    tensor = torch.tensor([[[0.2, 0.8]]], dtype=torch.float32)
    original = tensor.clone()
    node = VisionNode(tensor)

    resultado = node.negativo().ganancia(0.5).cuantizar(2)

    assert resultado is not node
    assert torch.equal(node.tensor, original)
    assert torch.allclose(resultado.tensor, torch.tensor([[[1 / 3, 0.0]]]))


def test_transformaciones_diferenciables_conservan_dtype_y_autograd() -> None:
    tensor = torch.rand(3, 4, 5, dtype=torch.float64, requires_grad=True)

    resultado = VisionNode(tensor).transformacion_gamma(0.8).ganancia(0.9)
    resultado.tensor.sum().backward()

    assert resultado.dtype is torch.float64
    assert resultado.device == tensor.device
    assert tensor.grad is not None
    assert torch.isfinite(tensor.grad).all()
