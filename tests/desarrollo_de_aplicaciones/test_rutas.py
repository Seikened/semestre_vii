from semestre_vii.desarrollo_de_aplicaciones import DATA_DIR, MODELS_DIR
from semestre_vii.desarrollo_de_aplicaciones.proyecto_1 import (
    PROJECT_DATA_DIR,
    PROJECT_MODELS_DIR,
)


def test_materia_expone_sus_rutas():
    assert DATA_DIR.parts[-2:] == ("data", "desarrollo_de_aplicaciones")
    assert MODELS_DIR.parts[-2:] == ("models", "desarrollo_de_aplicaciones")


def test_proyecto_1_extiende_las_rutas_de_la_materia():
    assert PROJECT_DATA_DIR == DATA_DIR / "proyecto_1"
    assert PROJECT_MODELS_DIR == MODELS_DIR / "proyecto_1"
