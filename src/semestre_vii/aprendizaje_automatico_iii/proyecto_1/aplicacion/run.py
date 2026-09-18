"""Prueba rápida del modelo entrenado con cámara, foto o video."""

from semestre_vii.aprendizaje_automatico_iii.proyecto_1 import DATA_DIR, MODEL_PATH
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion.runtime import ejecutar
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import dispositivo

# Cámara en vivo. Para volver a la foto:
SOURCE = "0"
# SOURCE = DATA_DIR / "concha.jpg"

DEVICE = "auto"
CONFIDENCE = 0.50
IMAGE_SIZE = 640
GRAYSCALE = True


def main() -> None:
    device = dispositivo(DEVICE)

    print(f"Modelo: {MODEL_PATH}")
    print(f"Dispositivo: {device}")
    print(f"Blanco y negro: {GRAYSCALE}")

    ejecutar(
        source=SOURCE,
        model=MODEL_PATH,
        device=device,
        conf=CONFIDENCE,
        imgsz=IMAGE_SIZE,
        sin_ventana=False,
        grayscale=GRAYSCALE,
    )


if __name__ == "__main__":
    main()
