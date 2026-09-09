import math

import pytest

from semestre_vii.vision_de_maquina.vision_node import (
    Camara,
    Escena,
    evaluar_focales,
    focal_ideal,
    fov_real,
    magnificacion_a_distancia,
    medida,
)


def test_medida_convierte_unidades_metricas() -> None:
    assert medida(1000, "um", "mm") == 1
    assert medida(2.5, "cm", "mm") == 25


def test_camara_calcula_dimensiones_del_sensor() -> None:
    camara = Camara(ancho_px=2448, alto_px=2048, pixel_size_um=3.45)

    assert math.isclose(camara.ancho_mm, 8.4456)
    assert math.isclose(camara.alto_mm, 7.0656)
    assert math.isclose(camara.diagonal_mm, math.hypot(8.4456, 7.0656))


def test_modelo_optico_calcula_focal_y_fov_consistentes() -> None:
    camara = Camara(ancho_px=2448, alto_px=2048, pixel_size_um=3.45)
    escena = Escena(fov_ancho_mm=550, fov_alto_mm=350, do_mm=550)

    focal = focal_ideal(camara, escena)
    fov_ancho, fov_alto = fov_real(camara, focal, escena.do_mm)

    assert magnificacion_a_distancia(focal, escena.do_mm) > 0
    assert fov_ancho >= escena.fov_ancho_mm
    assert fov_alto >= escena.fov_alto_mm
    assert min(fov_ancho / escena.fov_ancho_mm, fov_alto / escena.fov_alto_mm) == pytest.approx(1)


def test_evaluar_focales_entrega_tabla_polars() -> None:
    camara = Camara(ancho_px=2448, alto_px=2048, pixel_size_um=3.45)
    escena = Escena(fov_ancho_mm=550, fov_alto_mm=350, do_mm=550)

    tabla = evaluar_focales(camara, escena, [6, 8, 12, 25])

    assert tabla.shape == (4, 7)
    assert tabla.columns == [
        "f_mm",
        "m",
        "fov_x_mm",
        "fov_y_mm",
        "pS_x_mm",
        "pS_y_mm",
        "cubre_fov",
    ]


@pytest.mark.parametrize(
    ("funcion", "argumentos"),
    [
        (medida, (1, "yardas", "mm")),
        (magnificacion_a_distancia, (50, 50)),
        (Camara, (0, 100, 3.45)),
        (Escena, (100, -1, 600)),
    ],
)
def test_optica_rechaza_parametros_fisicamente_invalidos(funcion, argumentos) -> None:
    with pytest.raises(ValueError):
        funcion(*argumentos)
