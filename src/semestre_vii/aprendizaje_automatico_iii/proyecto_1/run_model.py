"""Tercer paso: abre la cámara y ejecuta el último modelo entrenado."""

from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion import ejecutar

# "0" abre la primera cámara. También puedes poner aquí una ruta a una foto o video.
SOURCE = "0"
DEVICE = "auto"
CONFIDENCE = 0.50
IMAGE_SIZE = 640


def main() -> None:
    ejecutar(
        source=SOURCE,
        model=None,
        device=DEVICE,
        conf=CONFIDENCE,
        imgsz=IMAGE_SIZE,
        sin_ventana=False,
    )


if __name__ == "__main__":
    main()
