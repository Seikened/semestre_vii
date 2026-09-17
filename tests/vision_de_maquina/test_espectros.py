import pytest
import torch

from semestre_vii.vision_de_maquina.vision_node.signals.espectros import (
    mascara_pasaaltas_butterworth,
    mascara_pasaaltas_gaussiano,
    mascara_pasaaltas_ideal,
    mascara_pasabajas_butterworth,
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


def test_mascara_butterworth_reproduce_formula_de_clase() -> None:
    tensor = torch.zeros((1, 8, 8), dtype=torch.float32)
    mascara = mascara_pasabajas_butterworth(tensor, corte=2, orden=1)

    assert mascara[4, 4] == 1
    torch.testing.assert_close(mascara[4, 6], torch.tensor(0.5))


def test_mascara_pasaaltas_ideal_reproduce_formula_de_clase() -> None:
    tensor = torch.zeros((1, 8, 8), dtype=torch.float32)
    mascara = mascara_pasaaltas_ideal(tensor, 2)

    assert mascara[4, 4] == 0
    assert mascara[4, 6] == 0
    assert mascara[4, 7] == 1


def test_mascara_pasaaltas_gaussiana_reproduce_formula_de_clase() -> None:
    tensor = torch.zeros((1, 8, 8), dtype=torch.float32)
    mascara = mascara_pasaaltas_gaussiano(tensor, 2)
    esperado = 1 - torch.exp(torch.tensor(-1 / 8, dtype=torch.float32))

    assert mascara[4, 4] == 0
    torch.testing.assert_close(mascara[4, 5], esperado)


def test_mascara_pasaaltas_butterworth_reproduce_formula_de_clase() -> None:
    tensor = torch.zeros((1, 8, 8), dtype=torch.float32)
    mascara = mascara_pasaaltas_butterworth(tensor, corte=2, orden=1)

    assert mascara[4, 4] == 0
    torch.testing.assert_close(mascara[4, 6], torch.tensor(0.5))


@pytest.mark.parametrize("corte", [0, -1])
def test_mascaras_rechazan_frecuencia_de_corte_no_positiva(corte: float) -> None:
    tensor = torch.zeros((1, 8, 8), dtype=torch.float32)

    with pytest.raises(ValueError, match="D0"):
        mascara_pasabajas_ideal(tensor, corte)
    with pytest.raises(ValueError, match="D0"):
        mascara_pasabajas_gaussiano(tensor, corte)
    with pytest.raises(ValueError, match="D0"):
        mascara_pasabajas_butterworth(tensor, corte)
    with pytest.raises(ValueError, match="D0"):
        mascara_pasaaltas_ideal(tensor, corte)
    with pytest.raises(ValueError, match="D0"):
        mascara_pasaaltas_gaussiano(tensor, corte)
    with pytest.raises(ValueError, match="D0"):
        mascara_pasaaltas_butterworth(tensor, corte)


@pytest.mark.parametrize("orden", [0, -1])
def test_butterworth_rechaza_orden_no_positivo(orden: int) -> None:
    tensor = torch.zeros((1, 8, 8), dtype=torch.float32)

    with pytest.raises(ValueError, match="orden"):
        mascara_pasabajas_butterworth(tensor, corte=2, orden=orden)
    with pytest.raises(ValueError, match="orden"):
        mascara_pasaaltas_butterworth(tensor, corte=2, orden=orden)
