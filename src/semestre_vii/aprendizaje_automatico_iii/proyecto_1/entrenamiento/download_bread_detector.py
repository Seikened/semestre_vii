"""Descarga e importa Bread Detector v2 en formato YOLO26."""

import json

from ..configuracion import directorio
from .datos import cargar_dataset
from .descarga import esperar_descarga_bread_detector
from .importacion import importar


def main() -> None:
    destino = directorio() / "datasets" / "bread_detector"
    data = destino / "data.yaml"

    if data.is_file():
        dataset = cargar_dataset(data, verificar_fugas=True)
        print("Bread Detector ya está listo.")
        print(json.dumps(dataset.resumen(), indent=2, ensure_ascii=False))
        print("\nSiguiente paso: ejecuta entrenamiento/train_detector.py")
        return

    if destino.exists():
        raise SystemExit(
            f"Existe {destino}, pero no contiene data.yaml. "
            "Revisa o elimina esa carpeta incompleta antes de continuar."
        )

    zip_path = esperar_descarga_bread_detector()
    print(f"Importando: {zip_path.name}")
    data = importar(zip_path, destino)

    dataset = cargar_dataset(data, verificar_fugas=True)
    poligonos = sum(
        etiqueta.segmentacion
        for muestra in dataset.muestras
        for etiqueta in muestra.etiquetas
    )

    if poligonos:
        raise SystemExit(
            "Bread Detector debería ser object detection, pero encontré polígonos. "
            "Revisa el formato exportado antes de entrenar."
        )

    print("\nDataset listo:")
    print(data)
    print(json.dumps(dataset.resumen(), indent=2, ensure_ascii=False))
    print("\nSiguiente paso: ejecuta train_detector.py")


if __name__ == "__main__":
    main()
