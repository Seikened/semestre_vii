"""Primer paso: deja un ZIP del dataset en data/.../proyecto_1/entrada y ejecuta este archivo."""

from pathlib import Path

from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import directorio
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.datos import cargar_dataset
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.importacion import importar
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.preparacion import preparar


def buscar_origen(entrada: Path) -> Path:
    entrada.mkdir(parents=True, exist_ok=True)
    candidatos = sorted(entrada.glob("*.zip"))
    candidatos += sorted(p for p in entrada.iterdir() if p.is_dir())

    if not candidatos:
        raise SystemExit(
            f"\nNo encontré el dataset.\n"
            f"Pon el ZIP descargado en:\n{entrada}\n\n"
            "Después vuelve a ejecutar prepare_dataset.py.\n"
        )
    if len(candidatos) > 1:
        raise SystemExit(f"Deja sólo un ZIP o carpeta dentro de {entrada}")
    return candidatos[0]


def main() -> None:
    base = directorio()
    dataset_yaml = base / "dataset" / "data.yaml"
    segmentado_yaml = base / "segmentado" / "data.yaml"

    if segmentado_yaml.is_file():
        print(f"Dataset ya preparado:\n{segmentado_yaml}")
        print("\nSiguiente paso: ejecuta train_model.py")
        return

    if not dataset_yaml.is_file():
        origen = buscar_origen(base / "entrada")
        print(f"Importando dataset local: {origen.name}")
        dataset_yaml = importar(origen, base / "dataset")

    dataset = cargar_dataset(dataset_yaml, verificar_fugas=True)
    hay_cajas = any(not etiqueta.segmentacion for muestra in dataset.muestras for etiqueta in muestra.etiquetas)

    if hay_cajas:
        print("El dataset tiene cajas. Generando máscaras con SAM en tu PC...")
    else:
        print("El dataset ya tiene polígonos de segmentación.")

    salida = preparar(dataset_yaml, base / "segmentado", con_sam=hay_cajas, device="auto")
    print(f"\nDataset preparado:\n{salida}")
    print("\nSiguiente paso: ejecuta train_model.py")


if __name__ == "__main__":
    main()
