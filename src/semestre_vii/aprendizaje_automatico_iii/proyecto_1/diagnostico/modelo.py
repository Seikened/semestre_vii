"""Diagnóstico del checkpoint final sin necesitar el dataset de entrenamiento."""

import cv2
import numpy as np
from ultralytics import YOLO

from .. import DATA_DIR, MODEL_PATH
from ..configuracion import dispositivo

SOURCE = DATA_DIR / "concha.jpg"
DEVICE = "auto"
CONFIDENCE = 0.001


def checkpoint_info() -> None:
    modelo = YOLO(str(MODEL_PATH))
    ckpt = getattr(modelo, "ckpt", {}) or {}
    args = ckpt.get("train_args", {}) or {}

    print("=== CHECKPOINT ===")
    print(f"Pesos: {MODEL_PATH}")
    print(f"Task: {modelo.task}")
    print(f"Clases: {modelo.names}")
    print(f"Epoch guardada: {ckpt.get('epoch', 'n/d')}")
    print(f"Best fitness: {ckpt.get('best_fitness', 'n/d')}")

    if args:
        print("Entrenamiento embebido:")
        for clave in ("model", "data", "epochs", "batch", "imgsz", "device", "optimizer", "pretrained"):
            if clave in args:
                print(f"  {clave}: {args[clave]}")


def reducir_en_frame(imagen: np.ndarray, escala: float) -> np.ndarray:
    alto, ancho = imagen.shape[:2]
    nuevo_ancho = max(1, int(ancho * escala))
    nuevo_alto = max(1, int(alto * escala))
    reducida = cv2.resize(imagen, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)

    fondo = np.full_like(imagen, 127)
    x = (ancho - nuevo_ancho) // 2
    y = (alto - nuevo_alto) // 2
    fondo[y:y + nuevo_alto, x:x + nuevo_ancho] = reducida
    return fondo


def probar(nombre: str, imagen: np.ndarray, device: str, imgsz: int) -> None:
    modelo = YOLO(str(MODEL_PATH))
    resultado = modelo.predict(
        source=imagen,
        device=device,
        conf=CONFIDENCE,
        imgsz=imgsz,
        retina_masks=False,
        max_det=100,
        verbose=False,
    )[0]

    cajas = resultado.boxes
    print(f"\n=== {nombre} | device={device} | imgsz={imgsz} ===")

    if cajas is None or len(cajas) == 0:
        print("0 detecciones")
        return

    predicciones = []
    for clase, confianza, xyxy in zip(
        cajas.cls.int().cpu().tolist(),
        cajas.conf.cpu().tolist(),
        cajas.xyxy.cpu().tolist(),
        strict=True,
    ):
        predicciones.append(
            (
                float(confianza),
                modelo.names[int(clase)],
                tuple(round(float(valor), 1) for valor in xyxy),
            )
        )

    predicciones.sort(reverse=True)
    for indice, (confianza, clase, caja) in enumerate(predicciones[:10], 1):
        print(f"{indice:02d}. {clase:<12} conf={confianza:.6f} box={caja}")


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"No existe la imagen: {SOURCE}")

    imagen = cv2.imread(str(SOURCE))
    if imagen is None:
        raise ValueError(f"No se puede leer la imagen: {SOURCE}")

    device = dispositivo(DEVICE)

    checkpoint_info()
    print(f"Imagen: {SOURCE}")
    print(f"Forma: {imagen.shape[1]}x{imagen.shape[0]}")
    print(f"Confidence diagnóstico: {CONFIDENCE}")

    # 1) Descarta un problema específico de MPS comparando contra CPU.
    probar("Original", imagen, device, 640)
    if device != "cpu":
        probar("Original control CPU", imagen, "cpu", 640)

    # 2) Descarta que 640 esté destruyendo demasiado detalle.
    probar("Original alta resolución", imagen, device, 1280)

    # 3) Prueba si el objeto ocupa demasiado frame respecto al dominio de entrenamiento.
    for escala in (0.75, 0.50, 0.33):
        probar(f"Frame reducido a {escala:.0%}", reducir_en_frame(imagen, escala), device, 640)


if __name__ == "__main__":
    main()
