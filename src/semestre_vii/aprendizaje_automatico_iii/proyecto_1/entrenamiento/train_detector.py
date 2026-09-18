"""Entrena YOLO26m-detect con Bread Detector v2."""

from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import directorio
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.entrenamiento.detector import (
    EntrenamientoDetector,
    entrenar_detector,
)

MODEL_SIZE = "m"
EPOCHS = 100
BATCH = -1
IMAGE_SIZE = 640
DEVICE = "auto"
PATIENCE = 25
MULTI_SCALE = 0.25


def main() -> None:
    data = directorio() / "datasets" / "bread_detector" / "data.yaml"

    if not data.is_file():
        raise SystemExit("Primero ejecuta download_bread_detector.py")

    config = EntrenamientoDetector(
        tamano=MODEL_SIZE,
        epochs=EPOCHS,
        batch=BATCH,
        imgsz=IMAGE_SIZE,
        device=DEVICE,
        patience=PATIENCE,
        multi_scale=MULTI_SCALE,
    )

    print(
        f"YOLO26{MODEL_SIZE}-detect | epochs={EPOCHS} | batch={BATCH} "
        f"| imgsz={IMAGE_SIZE} | multi_scale={MULTI_SCALE} | device={DEVICE}"
    )
    print("Fine-tuning completo desde pesos preentrenados; no se congela el backbone.")

    pesos = entrenar_detector(data, config)

    print(f"\nEntrenamiento terminado.\nBest weights:\n{pesos}")
    print("\nConserva toda la carpeta del run para revisar métricas antes de publicar el modelo.")


if __name__ == "__main__":
    main()
