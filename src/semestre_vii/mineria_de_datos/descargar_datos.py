"""Datasets de clase para Minería de Datos.

Los archivos ligeros pueden vivir en Git. Los pesados se reconstruyen desde su fuente pública.
"""

from pathlib import Path

import httpx

from semestre_vii.mineria_de_datos import DATA_DIR

FUENTES = {
    "USA_Housing.csv": "https://raw.githubusercontent.com/siglimuni/Datasets/master/USA_Housing.csv",
    "2026-01.csv": "https://ecobici.mx/wp-content/uploads/2026/02/2026-01.csv",
}


def descargar(nombre: str) -> Path:
    if nombre not in FUENTES:
        raise ValueError(f"Dataset desconocido: {nombre}")

    destino = DATA_DIR / nombre
    if destino.is_file():
        return destino

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(destino.suffix + ".part")

    print(f"Descargando {nombre}...")
    try:
        with httpx.stream(
            "GET",
            FUENTES[nombre],
            follow_redirects=True,
            timeout=120,
            headers={"User-Agent": "semestre-vii-mineria/0.1"},
        ) as respuesta:
            respuesta.raise_for_status()
            with temporal.open("wb") as archivo:
                for bloque in respuesta.iter_bytes(1024 * 1024):
                    archivo.write(bloque)
        temporal.replace(destino)
    except Exception:
        temporal.unlink(missing_ok=True)
        raise

    print(f"Listo: {destino}")
    return destino


def asegurar(nombre: str) -> Path:
    ruta = DATA_DIR / nombre
    return ruta if ruta.is_file() else descargar(nombre)


def main() -> None:
    for nombre in FUENTES:
        asegurar(nombre)


if __name__ == "__main__":
    main()
