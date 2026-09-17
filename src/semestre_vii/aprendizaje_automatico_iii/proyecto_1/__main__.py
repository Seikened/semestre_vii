"""CLI local por etapas; los imports pesados se hacen sólo cuando se necesitan."""

import argparse
import json
from pathlib import Path

from .configuracion import directorio


def construir_parser() -> argparse.ArgumentParser:
    base = directorio()
    raw = base / "dataset" / "data.yaml"
    anterior = base / "roboflow" / "data.yaml"
    if not raw.is_file() and anterior.is_file():
        raw = anterior  # Compatibilidad con archivos locales ya descargados; no usa el SDK.
    segmentado = base / "segmentado" / "data.yaml"
    preferido = segmentado if segmentado.is_file() else raw
    parser = argparse.ArgumentParser(description="Proyecto 1: caja asistida local con YOLO26-seg, sin API key.")
    comandos = parser.add_subparsers(dest="comando", required=True)
    importar = comandos.add_parser("importar", help="Importar un ZIP, carpeta o data.yaml desde tu PC.")
    importar.add_argument("origen", type=Path, help="Ruta local al ZIP, carpeta o data.yaml.")
    importar.add_argument("--destino", type=Path, default=base / "dataset")
    inspeccionar = comandos.add_parser("inspeccionar", help="Validar etiquetas y contar cajas/polígonos.")
    preparar = comandos.add_parser("preparar", help="Conservar polígonos o proponer máscaras con SAM.")
    revisar = comandos.add_parser("revisar", help="Exportar anotaciones superpuestas para revisión.")
    entrenar = comandos.add_parser("entrenar", help="Fine-tuning local de YOLO26-seg.")
    evaluar = comandos.add_parser("evaluar", help="mAP de máscaras y errores de conteo/importe.")
    caja = comandos.add_parser("caja", help="Segmentar una foto, video o cámara y estimar el total.")
    comandos.add_parser("precios", help="Mostrar el catálogo ficticio MXN.")
    for comando in (inspeccionar, preparar, revisar, entrenar, evaluar):
        comando.add_argument("--data", type=Path, default=raw if comando is preparar else preferido)
    inspeccionar.add_argument("--verificar-fugas", action="store_true")
    preparar.add_argument("--destino", type=Path, default=base / "segmentado")
    preparar.add_argument("--con-sam", action="store_true")
    revisar.add_argument("--split", choices=("train", "val", "test"), default="train")
    revisar.add_argument("--limite", type=int, default=20, help="0 exporta todas las imágenes del split.")
    revisar.add_argument("--destino", type=Path, default=base / "revision")
    for comando in (preparar, entrenar, evaluar, caja):
        comando.add_argument("--device", default="auto")
    for comando in (entrenar, evaluar):
        comando.add_argument("--aceptar-pseudoetiquetas", action="store_true")
    entrenar.add_argument("--tamano", choices=tuple("nsmlx"), default="n")
    entrenar.add_argument("--epochs", type=int, default=30)
    entrenar.add_argument("--batch", type=int, default=4)
    entrenar.add_argument("--fraction", type=float, default=1.0)
    entrenar.add_argument("--seed", type=int, default=42)
    for comando in (entrenar, caja):
        comando.add_argument("--imgsz", type=int, default=640)
    for comando in (evaluar, caja):
        comando.add_argument("--model", type=Path)
        comando.add_argument("--conf", type=float, default=.5)
    evaluar.add_argument("--split", choices=("val", "test"), default="val")
    caja.add_argument("--source", default="0")
    caja.add_argument("--sin-ventana", action="store_true")
    return parser


def main() -> None:
    parser = construir_parser()
    args = parser.parse_args()
    try:
        if args.comando == "precios":
            from .precios import PRECIOS
            print(json.dumps({nombre: f"{precio / 100:.2f} MXN" for nombre, precio in PRECIOS.items()}, indent=2))
        elif args.comando == "importar":
            from .importacion import importar
            ruta = importar(args.origen, args.destino)
            print(f"Dataset local importado: {ruta}")
            print(f'Siguiente: inspeccionar --data "{ruta}" --verificar-fugas')
        elif args.comando == "inspeccionar":
            from .datos import cargar_dataset
            print(json.dumps(cargar_dataset(args.data, args.verificar_fugas).resumen(), indent=2, ensure_ascii=False))
        elif args.comando == "preparar":
            from .preparacion import preparar
            print(preparar(args.data, args.destino, args.con_sam, args.device))
        elif args.comando == "revisar":
            from .interfaz import revisar
            print(revisar(args.data, args.split, args.destino, args.limite))
        elif args.comando == "entrenar":
            from .entrenamiento import Entrenamiento, entrenar
            config = Entrenamiento(args.tamano, args.epochs, args.batch, args.imgsz, args.device, args.fraction, args.seed)
            print(entrenar(args.data, config, args.aceptar_pseudoetiquetas))
        elif args.comando == "evaluar":
            from .entrenamiento import evaluar
            print(evaluar(args.data, args.model, args.split, args.device, args.conf, args.aceptar_pseudoetiquetas))
        elif args.comando == "caja":
            from .aplicacion import ejecutar
            ejecutar(args.source, args.model, args.device, args.conf, args.imgsz, args.sin_ventana)
    except ModuleNotFoundError as exc:
        parser.exit(2, f"Falta {exc.name}. Ejecuta: uv add ultralytics opencv-python pyyaml\n")
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    except KeyboardInterrupt:
        parser.exit(130, "Operación cancelada.\n")


if __name__ == "__main__":
    main()
