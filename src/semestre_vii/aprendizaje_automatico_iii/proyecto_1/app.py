"""Punto de entrada de la aplicación del proyecto."""

import sys

from semestre_vii.aprendizaje_automatico_iii.proyecto_1 import MODEL_PATH
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion.runtime import ejecutar

MODELOS = {
    "bread-v2_m_previo": MODEL_PATH / "bread_detector_best.pt",
    "mexican-v3_s_previo": MODEL_PATH / "yolo26s_mexican_bread_seg_best.pt",
    **{
        ruta.parent.parent.name: ruta
        for ruta in MODEL_PATH.glob("yolo26*/weights/best.pt")
        if (ruta.parent.parent / ".gitignore").is_file()
    },
}
MODELO = "bread-v2_m_previo"
SOURCE = "0"
DEVICE = "auto"
CONFIDENCE = 0.50
IMAGE_SIZE = 640
GRAYSCALE = False


def seleccionar_modelo(nombre):
    if nombre not in MODELOS:
        raise SystemExit(f"Modelos disponibles: {', '.join(MODELOS)}")
    return MODELOS[nombre]


def main():
    nombre = sys.argv[1] if len(sys.argv) > 1 else MODELO
    modelo = seleccionar_modelo(nombre)

    print(f"Modelo: {nombre} ({modelo})")

    ejecutar(
        source=SOURCE,
        model=modelo,
        device=DEVICE,
        conf=CONFIDENCE,
        imgsz=IMAGE_SIZE,
        sin_ventana=False,
        grayscale=GRAYSCALE,
    )


if __name__ == "__main__":
    main()
