"""Segundo paso: entrena YOLO26-seg con el dataset preparado."""

from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import directorio
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.entrenamiento.datos import cargar_dataset
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.entrenamiento.segmentacion import (
    Entrenamiento,
    entrenar,
)

# Valores simples para el primer entrenamiento. Puedes cambiarlos después.
MODEL_SIZE = "s"
EPOCHS = 50
BATCH = 4
IMAGE_SIZE = 640
DEVICE = "auto"


def main():
    data = directorio() / "segmentado" / "data.yaml"
    if not data.is_file():
        raise SystemExit("Primero ejecuta entrenamiento/prepare_segmentacion.py")

    dataset = cargar_dataset(data)
    config = Entrenamiento(
        tamano=MODEL_SIZE,
        epochs=EPOCHS,
        batch=BATCH,
        imgsz=IMAGE_SIZE,
        device=DEVICE,
    )

    print(f"Entrenando YOLO26{MODEL_SIZE}-seg | device={DEVICE} | epochs={EPOCHS} | batch={BATCH}")
    pesos = entrenar(data, config, aceptar_pseudo=dataset.pseudoetiquetas)
    print(f"\nModelo terminado:\n{pesos}")
    print("\nSiguiente paso: ejecuta app.py")


if __name__ == "__main__":
    main()
