"""Descarga e importa Bread Detector v2 en formato YOLO26."""

import json

from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import directorio
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.entrenamiento.datos import (
    cargar_dataset,
    eliminar_fugas_entre_splits,
)
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.utils.descargas import descargar_bread_detector
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.utils.importacion import importar


def _cargar_sin_fugas(data):
    raiz = data.parent
    eliminadas = eliminar_fugas_entre_splits(data, raiz_permitida=raiz)

    if eliminadas:
        total = sum(eliminadas.values())
        detalle = ", ".join(f"{split}={cantidad}" for split, cantidad in eliminadas.items())
        print(f"Se limpiaron {total} imagen(es) duplicadas entre splits ({detalle}).")
        print("Se conserva la primera copia con prioridad train > val > test.")

    return cargar_dataset(data, verificar_fugas=True, raiz_permitida=raiz)


def main():
    destino = directorio() / "datasets" / "bread_detector"
    data = destino / "data.yaml"

    if data.is_file():
        dataset = _cargar_sin_fugas(data)
        print("Bread Detector ya está listo.")
        print(json.dumps(dataset.resumen(), indent=2, ensure_ascii=False))
        print("\nSiguiente paso: ejecuta entrenamiento/train_detector.py")
        return

    if destino.exists():
        raise SystemExit(
            f"Existe {destino}, pero no contiene data.yaml. "
            "Revisa o elimina esa carpeta incompleta antes de continuar."
        )

    zip_path = descargar_bread_detector()
    print(f"Importando: {zip_path.name}")
    data = importar(zip_path, destino)

    dataset = _cargar_sin_fugas(data)
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
    print("\nSiguiente paso: ejecuta entrenamiento/train_detector.py")


if __name__ == "__main__":
    main()
