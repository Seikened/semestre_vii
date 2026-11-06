"""Fase 1: descarga Mexican Bread v3, recorta cada pan anotado y guarda su galería."""

from pathlib import Path

from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import (
    DATASET_MEXICAN,
    GALERIA_PANES,
    AjustesConstruccion,
    AjustesPrecarga,
)
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.esquemas.pan import ClasePan
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.motor_embedding.encoder import Encoder
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.motor_embedding.precarga.construir import (
    construir_galeria,
)
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.motor_embedding.precarga.roboflow import (
    descargar_mexican_bread,
)


class AjustesCarga(AjustesPrecarga):
    """Parámetros de la precarga. Sobrescriben configuracion.py; entorno y .env aún los ajustan."""

    dispositivo: str = "auto"
    galeria: Path = GALERIA_PANES
    construccion: AjustesConstruccion = AjustesConstruccion(
        dataset=DATASET_MEXICAN,
        clases=(  # None = las 11 del dataset.
            ClasePan.BOLILLO, ClasePan.CONCHA, ClasePan.CUERNITO, ClasePan.DONA,
        ),
        gris=True,  # Mexican Bread v3 ya viene en gris; así queda explícito en el manifiesto.
    )


def main():
    try:
        precargar(AjustesCarga())
    except (ValueError, OSError, RuntimeError) as error:
        # Frontera con la terminal: clave faltante, red caída o dataset inválido.
        raise SystemExit(f"Error: {error}") from None


def precargar(ajustes: AjustesPrecarga):
    construccion = ajustes.construccion
    data_yaml = descargar_mexican_bread(construccion.dataset, ajustes.roboflow_api_key)
    print("Construyendo la galería con ResNet50...")
    encoder = Encoder(ajustes.dispositivo)
    galeria = construir_galeria(data_yaml, encoder, construccion.clases, construccion.gris)
    carpeta = galeria.guardar(ajustes.galeria)
    print(galeria.manifiesto.model_dump_json(indent=2))
    print(f"Galería guardada en {carpeta}")


if __name__ == "__main__":
    main()
