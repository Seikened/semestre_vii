"""CLI de laboratorio: sin red, servidor, credenciales ni persistencia."""

import argparse
import json

from .experimentos.comparar import BASE, comparar


def main() -> None:
    parser = argparse.ArgumentParser(description="Laboratorio reversible de compresión de URLs")
    parser.add_argument("url", help="URL HTTP(S) a compactar")
    parser.add_argument("--base", default=BASE, help="Origen simulado de enlaces compactos")
    parser.add_argument("--json", action="store_true", help="Mostrar resultados como JSON")
    args = parser.parse_args()
    try:
        resultado = comparar(args.url, args.base)
    except ValueError as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return
    print("Laboratorio EPOK Links | Códec v1 (baseline DEFLATE)")
    print("Enlaces simulados; /c/ aún no es una ruta pública.")
    for nombre, enlace in resultado["muestras"].items():
        metrica = resultado["metricas"][nombre]
        qr = metrica["qr"]
        print(f"\n{nombre}: {enlace}")
        qr_texto = (
            f"QR M v{qr['version']} ({qr['modulos']}x{qr['modulos']}, {qr['modo']})"
            if qr["version"] is not None
            else "QR M: fuera de capacidad"
        )
        print(f"  {metrica['caracteres']} caracteres | {metrica['bytes_utf8']} bytes | {qr_texto}")
    print("\nRecuperación exacta (URL y QR): sí")


if __name__ == "__main__":
    main()
