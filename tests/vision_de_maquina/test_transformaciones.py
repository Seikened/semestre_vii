import pytest
import torch

from semestre_vii.vision_de_maquina.vision_node import VisionNode


def test_clip_limita_los_valores_al_intervalo() -> None:
    tensor = torch.tensor([[[-1.0, 0.5, 2.0]]])

    resultado = VisionNode(tensor).clip(0.0, 1.0)

    assert torch.equal(resultado.tensor, torch.tensor([[[0.0, 0.5, 1.0]]]))


def test_negativo_invierte_intensidades_normalizadas() -> None:
    tensor = torch.tensor([[[0.0, 0.25, 1.0]]])

    resultado = VisionNode(tensor).negativo()

    assert torch.equal(resultado.tensor, torch.tensor([[[1.0, 0.75, 0.0]]]))


def test_escala_grises_aplica_luminancia_rgb() -> None:
    tensor = torch.zeros(3, 2, 2)
    tensor[0] = 1.0

    resultado = VisionNode(tensor).escala_grises()

    assert resultado.shape == (1, 2, 2)
    assert torch.allclose(resultado.tensor, torch.full((1, 2, 2), 0.299))


def test_ganancia_multiplica_y_satura_intensidades() -> None:
    tensor = torch.tensor([[[0.25, 0.75]]])

    resultado = VisionNode(tensor).ganancia(2.0)

    assert torch.equal(resultado.tensor, torch.tensor([[[0.5, 1.0]]]))


def test_gamma_aplica_exponente_sobre_intervalo_normalizado() -> None:
    tensor = torch.tensor([[[-1.0, 0.25, 2.0]]])

    resultado = VisionNode(tensor).transformacion_gamma(0.5)

    assert torch.equal(resultado.tensor, torch.tensor([[[0.0, 0.5, 1.0]]]))


def test_cuantizar_redondea_a_la_cantidad_solicitada_de_niveles() -> None:
    tensor = torch.tensor([[[0.1, 0.3, 0.8, 1.2]]])

    resultado = VisionNode(tensor).cuantizar(2)

    esperado = torch.tensor([[[0.0, 1 / 3, 2 / 3, 1.0]]])
    assert torch.allclose(resultado.tensor, esperado)


def test_binarizar_usa_un_umbral_inclusivo() -> None:
    tensor = torch.tensor([[[0.2, 0.5, 0.8]]])

    resultado = VisionNode(tensor).binarizar(0.5)

    assert torch.equal(resultado.tensor, torch.tensor([[[0.0, 1.0, 1.0]]]))


def test_binarizar_rango_incluye_ambos_limites() -> None:
    tensor = torch.tensor([[[0.2, 0.4, 0.6, 0.8]]])

    resultado = VisionNode(tensor).binarizar_rango(0.4, 0.6)

    assert torch.equal(resultado.tensor, torch.tensor([[[0.0, 1.0, 1.0, 0.0]]]))


@pytest.mark.parametrize(
    ("metodo", "argumentos", "error"),
    [
        ("clip", (1.0, 0.0), ValueError),
        ("ganancia", (-1.0,), ValueError),
        ("transformacion_gamma", (0.0,), ValueError),
        ("cuantizar", (0,), ValueError),
        ("cuantizar", (True,), TypeError),
        ("binarizar", (float("nan"),), ValueError),
        ("binarizar_rango", (0.8, 0.2), ValueError),
    ],
)
def test_transformaciones_rechazan_parametros_invalidos(
    metodo: str,
    argumentos: tuple[object, ...],
    error: type[Exception],
) -> None:
    node = VisionNode(torch.zeros(1, 2, 2))

    with pytest.raises(error):
        getattr(node, metodo)(*argumentos)
