"""Prueba rápida del modelo YOLO26s-seg entrenado para panes mexicanos."""

from semestre_vii.aprendizaje_automatico_iii.proyecto_1 import MODEL_PATH
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion import ejecutar

# "0" abre la primera cámara. También puedes poner una ruta a una foto o video.
SOURCE = "0"
DEVICE = "auto"
CONFIDENCE = 0.50
IMAGE_SIZE = 640


def main() -> None:
    print(f"Modelo: {MODEL_PATH}")
    ejecutar(
        source=SOURCE,
        model=MODEL_PATH,
        device=DEVICE,
        conf=CONFIDENCE,
        imgsz=IMAGE_SIZE,
        sin_ventana=False,
    )


if __name__ == "__main__":
    main()
