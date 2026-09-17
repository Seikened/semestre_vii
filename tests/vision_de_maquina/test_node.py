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


def test_operadores_aritmeticos_aceptan_nodos_y_escalares() -> None:
    node = VisionNode(torch.full((1, 2, 2), 0.5), titulo="Base")

    assert torch.equal((node + 0.5).tensor, torch.ones(1, 2, 2))
    assert torch.equal((1 - node).tensor, torch.full((1, 2, 2), 0.5))
    assert torch.equal((node * node).tensor, torch.full((1, 2, 2), 0.25))
    assert torch.equal((node / 0.5).tensor, torch.ones(1, 2, 2))
    assert torch.equal((-node).tensor, torch.full((1, 2, 2), -0.5))


def test_promediar_no_muta_los_nodos_de_entrada() -> None:
    base = VisionNode(torch.zeros(1, 2, 2))
    otra = VisionNode(torch.ones(1, 2, 2))

    resultado = base.promediar([otra])

    assert torch.equal(resultado.tensor, torch.full((1, 2, 2), 0.5))
    assert torch.equal(base.tensor, torch.zeros(1, 2, 2))
    assert torch.equal(otra.tensor, torch.ones(1, 2, 2))


def test_chirp_espacial_es_cuadrado_y_aumenta_su_frecuencia() -> None:
    node = VisionNode.chirp_espacial(
        size=64,
        frecuencia_inicial=1,
        frecuencia_final=12,
        amplitud_inicial=0.1,
        amplitud_final=0.4,
    )

    assert node.shape == (1, 64, 64)
    torch.testing.assert_close(node.tensor[0, 0], node.tensor[0, -1])
    assert 0 <= node.min() <= node.max() <= 1

    centrada = node.tensor[0, 0] >= 0.5
    cambios = centrada[1:] != centrada[:-1]
    assert cambios[32:].sum() > cambios[:32].sum()


def test_chirp_profesor_reproduce_formula_de_clase() -> None:
    node = VisionNode.chirp_profesor()
    j = torch.tensor(15.0)
    esperado = (127 + 30 * torch.cos((2 * torch.pi / 500) * (2 * j / 30) * j)) / 255

    assert node.shape == (1, 500, 500)
    torch.testing.assert_close(node.tensor[0, 0, 0], torch.tensor(157 / 255))
    torch.testing.assert_close(node.tensor[0, 0, 15], esperado)
    torch.testing.assert_close(node.tensor[0, 0], node.tensor[0, -1])


def test_aliases_legacy_y_descripcion_de_api_siguen_disponibles(capsys) -> None:
    node = VisionNode(torch.zeros(1, 2, 3), title="Prueba")

    tabla = VisionNode.describir_api()

    assert node.title == "Prueba"
    assert node.channels == 1
    assert node.height == 2
    assert node.width == 3
    assert node.is_grayscale
    assert "gaussiano" in tabla
    assert "picos_espectrales" in tabla
    assert "gaussiano" in capsys.readouterr().out
