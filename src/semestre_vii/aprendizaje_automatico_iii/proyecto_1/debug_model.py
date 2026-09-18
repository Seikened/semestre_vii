"""Diagnóstico mínimo del checkpoint final sobre una imagen externa."""

from ultralytics import YOLO

from semestre_vii.aprendizaje_automatico_iii.proyecto_1 import DATA_DIR, MODEL_PATH
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import dispositivo

SOURCE = DATA_DIR / "concha.jpg"
DEVICE = "auto"
CONFIDENCE = 0.001
IMAGE_SIZE = 640


def main() -> None:
    device = dispositivo(DEVICE)
    modelo = YOLO(str(MODEL_PATH))

    print("=== CHECKPOINT ===")
    print(f"Pesos: {MODEL_PATH}")
    print(f"Task: {modelo.task}")
    print(f"Clases: {modelo.names}")
    print(f"Dispositivo: {device}")
    print(f"Imagen: {SOURCE}")
    print(f"Confidence diagnóstico: {CONFIDENCE}")

    if not SOURCE.is_file():
        raise FileNotFoundError(f"No existe la imagen: {SOURCE}")

    resultado = modelo.predict(
        source=str(SOURCE),
        device=device,
        conf=CONFIDENCE,
        imgsz=IMAGE_SIZE,
        retina_masks=True,
        max_det=100,
        verbose=False,
    )[0]

    cajas = resultado.boxes
    print("\n=== PREDICCIONES CRUDAS ===")

    if cajas is None or len(cajas) == 0:
        print("0 detecciones incluso con confidence=0.001")
        print("Esto ya no es un problema del umbral 0.50/0.05.")
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

    for indice, (confianza, clase, caja) in enumerate(predicciones[:20], 1):
        print(f"{indice:02d}. {clase:<12} conf={confianza:.6f} box={caja}")

    print(f"\nTotal: {len(predicciones)} detecciones")


if __name__ == "__main__":
    main()
