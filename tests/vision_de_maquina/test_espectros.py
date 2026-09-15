import pytest
import torch

from semestre_vii.vision_de_maquina.vision_node.signals.espectros import (
    mascara_pasabajas_gaussiano,
    mascara_pasabajas_ideal,
)


def test_mascara_ideal_reproduce_formula_mathcad() -> None:
    tensor = torch.zeros((1, 8, 8), dtype=torch.float32)
    mascara = mascara_pasabajas_ideal(tensor, 2)

    assert mascara[4, 4] == 1
    assert mascara[4, 5] == 1
    assert mascara[4, 6] == 0


def test_mascara_gaussiana_reproduce_formula_mathcad() -> None:
    tensor = torch.zeros((1, 8, 8), dtype=torch.float32)
    mascara = mascara_pasabajas_gaussiano(tensor, 2)
    esperado = torch.exp(torch.tensor(-1 / 8, dtype=torch.float32))

    assert mascara[4, 4] == 1
    torch.testing.assert_close(mascara[4, 5], esperado)


@pytest.mark.parametrize("corte", [0, -1])
def test_mascaras_rechazan_frecuencia_de_corte_no_positiva(corte: float) -> None:
    tensor = torch.zeros((1, 8, 8), dtype=torch.float32)

    with pytest.raises(ValueError, match="D0"):
        mascara_pasabajas_ideal(tensor, corte)
    with pytest.raises(ValueError, match="D0"):
        mascara_pasabajas_gaussiano(tensor, corte)
