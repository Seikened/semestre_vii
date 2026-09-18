from semestre_vii.aprendizaje_automatico_iii.proyecto_2 import PROJECT_DATA_DIR, PROJECT_MODELS_DIR


def test_rutas_del_proyecto_siguen_la_convencion_del_repositorio():
    assert PROJECT_DATA_DIR.parts[-3:] == ("data", "aprendizaje_automatico_iii", "proyecto_2")
    assert PROJECT_MODELS_DIR.parts[-3:] == ("models", "aprendizaje_automatico_iii", "proyecto_2")
