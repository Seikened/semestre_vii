"""Primer paso: consigue, importa y prepara Mexican Bread con una sola ejecución."""

from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import directorio
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.entrenamiento.datos import cargar_dataset
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.utils.descargas import descargar_mexican_bread
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.utils.importacion import importar
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.entrenamiento.preparacion import preparar


def buscar_o_descargar(entrada):
    entrada.mkdir(parents=True, exist_ok=True)
    candidatos = sorted(entrada.glob("*.zip"))
    candidatos += sorted(p for p in entrada.iterdir() if p.is_dir())

    if len(candidatos) > 1:
        raise SystemExit(f"Deja sólo un ZIP o carpeta dentro de {entrada}")
    if candidatos:
        return candidatos[0]
    return descargar_mexican_bread()


def main():
    base = directorio()
    dataset_yaml = base / "dataset" / "data.yaml"
    segmentado_yaml = base / "segmentado" / "data.yaml"

    if segmentado_yaml.is_file():
        print(f"Dataset ya preparado:\n{segmentado_yaml}")
        print("\nSiguiente paso: ejecuta entrenamiento/train_segmentacion.py")
        return

    if not dataset_yaml.is_file():
        origen = buscar_o_descargar(base / "entrada")
        print(f"Importando dataset: {origen.name}")
        dataset_yaml = importar(origen, base / "dataset")

    dataset = cargar_dataset(dataset_yaml, verificar_fugas=True)
    hay_cajas = any(not etiqueta.segmentacion for muestra in dataset.muestras for etiqueta in muestra.etiquetas)

    if hay_cajas:
        print("El dataset tiene cajas. Generando máscaras con SAM en tu PC...")
    else:
        print("El dataset ya tiene polígonos de segmentación.")

    salida = preparar(dataset_yaml, base / "segmentado", con_sam=hay_cajas, device="auto")
    print(f"\nDataset preparado:\n{salida}")
    print("\nSiguiente paso: ejecuta entrenamiento/train_segmentacion.py")


if __name__ == "__main__":
    main()
