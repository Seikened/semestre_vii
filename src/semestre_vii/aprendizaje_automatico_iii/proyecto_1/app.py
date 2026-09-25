"""Punto de entrada de la aplicación del proyecto."""

from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion.runtime import ejecutar
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import (
    MODELO_CAJA,
    dispositivo,
)

SOURCE = "0"
DEVICE = "auto"
CONFIDENCE = 0.50
IMAGE_SIZE = 640
GRAYSCALE = False


def main():
    device = dispositivo(DEVICE)

    print(f"Modelo: {MODELO_CAJA}")
    print(f"Dispositivo: {device}")
    print(f"Blanco y negro: {GRAYSCALE}")

    ejecutar(
        source=SOURCE,
        model=MODELO_CAJA,
        device=device,
        conf=CONFIDENCE,
        imgsz=IMAGE_SIZE,
        sin_ventana=False,
        grayscale=GRAYSCALE,
    )


if __name__ == "__main__":
    main()
