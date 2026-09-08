import math

import torch

from semestre_vii.vision_de_maquina.vision_node import VisionNode


def test_separaciones_de_color_conservan_el_contrato_chw() -> None:
    tensor = torch.tensor(
        [
            [[1.0, 0.2]],
            [[0.0, 0.2]],
            [[0.0, 0.2]],
        ]
    )
    node = VisionNode(tensor)

    rgb = node.separar_canales()
    hsv = node.separar_hsv()

    assert set(rgb) == {"Rojo", "Verde", "Azul"}
    assert set(hsv) == {"Matiz", "Saturación", "Valor"}
    assert all(canal.shape == (1, 1, 2) for canal in (*rgb.values(), *hsv.values()))
    assert hsv["Saturación"].tensor[0, 0, 0] == 1
    assert hsv["Saturación"].tensor[0, 0, 1] == 0


def test_saturacion_y_acromaticidad_resumen_el_color() -> None:
    tensor = torch.tensor([[[0.8]], [[0.5]], [[0.2]]])

    saturacion = VisionNode(tensor).saturacion()
    acromaticidad = VisionNode(tensor).acromaticidad()

    assert torch.allclose(saturacion.tensor, torch.tensor([[[0.75]]]))
    assert torch.equal(acromaticidad.tensor, torch.tensor([[[0.2]]]))


def test_estirar_contraste_usa_todo_el_intervalo() -> None:
    tensor = torch.tensor([[[0.2, 0.4, 0.6]]])

    resultado = VisionNode(tensor).estirar_contraste()

    assert resultado.min() == 0
    assert math.isclose(resultado.max(), 1, abs_tol=3e-6)
    assert torch.allclose(resultado.tensor, torch.tensor([[[0.0, 0.5, 1.0]]]))


def test_ajustes_aceptan_vistas_no_contiguas() -> None:
    tensor = torch.rand(3, 8, 8)[:, :5, :5]
    assert not tensor.is_contiguous()

    contraste = VisionNode(tensor).estirar_contraste()
    lineal = VisionNode(tensor).transformacion_lineal((0, 255), (0, 255))

    assert contraste.shape == tensor.shape
    assert lineal.shape == tensor.shape


def test_estirar_contraste_preserva_una_imagen_constante() -> None:
    tensor = torch.full((1, 4, 4), 0.5)

    resultado = VisionNode(tensor).estirar_contraste()

    assert torch.equal(resultado.tensor, tensor)


def test_estirar_contraste_usa_un_rango_global_en_rgb() -> None:
    tensor = torch.tensor([[[0.2, 0.4]], [[0.6, 0.8]], [[0.3, 0.7]]])

    resultado = VisionNode(tensor).estirar_contraste()

    esperado = (tensor - 0.2) / 0.6
    assert torch.allclose(resultado.tensor, esperado, atol=3e-6)


def test_binarizacion_adaptativa_produce_una_mascara() -> None:
    tensor = torch.linspace(0, 1, 25).reshape(1, 5, 5)

    resultado = VisionNode(tensor).binarizar_adaptativo(kernel_size=3, c=0.0)

    assert resultado.shape == tensor.shape
    assert set(resultado.tensor.unique().tolist()) <= {0.0, 1.0}


def test_transformacion_logaritmica_es_monotona_y_normalizada() -> None:
    tensor = torch.tensor([[[0.0, 0.25, 0.5, 1.0]]])

    resultado = VisionNode(tensor).transformacion_log()

    assert torch.all(resultado.tensor[:, :, 1:] >= resultado.tensor[:, :, :-1])
    assert math.isclose(resultado.max(), 1.0)


def test_transformacion_lineal_interpola_y_respeta_los_extremos() -> None:
    tensor = torch.tensor([[[0.0, 125 / 255, 1.0]]])

    resultado = VisionNode(tensor).transformacion_lineal((50, 200), (100, 220))

    esperado = torch.tensor([[[100 / 255, 160 / 255, 220 / 255]]])
    assert torch.allclose(resultado.tensor, esperado)


def test_transformacion_lineal_por_canal_aplica_curvas_independientes() -> None:
    tensor = torch.full((3, 1, 1), 0.5)
    identidad = ((0, 0), (255, 255))
    invertida = ((0, 255), (255, 0))

    resultado = VisionNode(tensor).transformacion_lineal_por_canal(
        identidad,
        invertida,
        ((0, 0), (255, 127.5)),
    )

    assert torch.allclose(resultado.tensor[:, 0, 0], torch.tensor([0.5, 0.5, 0.25]))


def test_pseudocolor_y_falso_color_producen_rgb() -> None:
    gris = VisionNode(torch.linspace(0, 1, 9).reshape(1, 3, 3))
    rgb = VisionNode(torch.stack((torch.zeros(2, 2), torch.ones(2, 2), torch.full((2, 2), 0.5))))

    pseudocolor = gris.pseudocolor_infrarrojo()
    falso_color = rgb.falso_color_infrarrojo()

    assert pseudocolor.shape == (3, 3, 3)
    assert pseudocolor.min() >= 0
    assert pseudocolor.max() <= 1
    assert torch.equal(falso_color.tensor[0], rgb.tensor[1])
    assert torch.equal(falso_color.tensor[1], rgb.tensor[0])


def test_histograma_acumulado_y_ecualizacion_conservan_la_imagen() -> None:
    node = VisionNode(torch.linspace(0, 1, 256).reshape(1, 16, 16))

    ecualizada = node.ecualizar()

    assert ecualizada.shape == node.shape
    assert ecualizada.dtype is node.dtype
    assert ecualizada.min() >= 0
    assert ecualizada.max() <= 1
