"""Segundo paso: entrena YOLO26-seg con el dataset preparado."""

from ..configuracion import directorio
from .datos import cargar_dataset
from .segmentacion import Entrenamiento, entrenar

# Valores simples para el primer entrenamiento. Puedes cambiarlos después.
MODEL_SIZE = "s"
EPOCHS = 50
BATCH = 4
IMAGE_SIZE = 640
DEVICE = "auto"


def main() -> None:
    data = directorio() / "segmentado" / "data.yaml"
    if not data.is_file():
        raise SystemExit("Primero ejecuta prepare_dataset.py")

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
    print("\nSiguiente paso: ejecuta run_model.py")


if __name__ == "__main__":
    main()
