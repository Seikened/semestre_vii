"""Punto de entrada de la aplicación del proyecto."""

from semestre_vii.aprendizaje_automatico_iii.proyecto_1 import DATA_DIR, MODEL_PATH
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion.runtime import ejecutar
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import dispositivo

# "0" abre la cámara. También puedes usar DATA_DIR / "concha.jpg".
SOURCE = "0"
DEVICE = "auto"
CONFIDENCE = 0.50
IMAGE_SIZE = 640
GRAYSCALE = True


def main():
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
