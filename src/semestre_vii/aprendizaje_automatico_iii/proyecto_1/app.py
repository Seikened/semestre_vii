import sys

from semestre_vii.aprendizaje_automatico_iii.proyecto_1 import MODEL_PATH
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion.runtime import ejecutar

DATASETS = {"bread-v2": "det", "mexican-v3": "seg"}
DATASET = "bread-v2"

TAMANO = "x"
SOURCE = "0"
DEVICE = "auto"
CONFIDENCE = 0.50
IMAGE_SIZE = 640
GRAYSCALE = False


def seleccionar_modelo(dataset, tamano):
    if dataset not in DATASETS or tamano not in ("n", "s", "m", "l", "x"):
        raise SystemExit("Dataset: bread-v2 o mexican-v3. Tamaño: n, s, m, l o x.")

    nombre = f"yolo26{tamano}_{dataset}_{DATASETS[dataset]}"
    modelo = MODEL_PATH / nombre / "weights/best.pt"
    if not modelo.is_file():
        raise SystemExit(f"No se encontró el peso: {modelo}")
    return modelo


def main():
    if len(sys.argv) == 1:
        dataset, tamano = DATASET, TAMANO
    elif len(sys.argv) == 3:
        dataset, tamano = sys.argv[1:]
    else:
        raise SystemExit("Uso: app.py [bread-v2|mexican-v3] [n|s|m|l|x]")

    modelo = seleccionar_modelo(dataset, tamano)

    print(f"Modelo: {modelo.parent.parent.name} ({modelo})")

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
