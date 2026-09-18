"""Prueba rápida del modelo entrenado con cámara, foto o video."""

from semestre_vii.aprendizaje_automatico_iii.proyecto_1 import MODEL_PATH
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion import ejecutar
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import dispositivo

# "0" = primera cámara. También puedes poner una ruta a una foto o video.
SOURCE = "0"
DEVICE = "auto"
CONFIDENCE = 0.50
IMAGE_SIZE = 640


def main() -> None:
    device = dispositivo(DEVICE)

    print(f"Modelo: {MODEL_PATH}")
    print(f"Dispositivo: {device}")

    ejecutar(
        source=SOURCE,
        model=MODEL_PATH,
        device=device,
        conf=CONFIDENCE,
        imgsz=IMAGE_SIZE,
        sin_ventana=False,
    )


if __name__ == "__main__":
    main()
