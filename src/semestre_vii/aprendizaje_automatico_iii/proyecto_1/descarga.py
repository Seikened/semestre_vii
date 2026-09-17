"""Abre Roboflow en el navegador y espera el ZIP descargado localmente."""

from pathlib import Path
import os
import re
import time
import webbrowser
from zipfile import is_zipfile

DOWNLOAD_PAGE = "https://universe.roboflow.com/jpia/mexican-bread/dataset/3/download/yolo26"
TIMEOUT_SECONDS = 15 * 60


def _carpetas_descargas() -> tuple[Path, ...]:
    carpetas = []
    configuracion = Path.home() / ".config" / "user-dirs.dirs"
    if configuracion.is_file():
        texto = configuracion.read_text(encoding="utf-8", errors="ignore")
        coincidencia = re.search(r'^XDG_DOWNLOAD_DIR="([^"]+)"', texto, re.MULTILINE)
        if coincidencia:
            valor = coincidencia.group(1).replace("$HOME", str(Path.home()))
            carpetas.append(Path(os.path.expandvars(valor)).expanduser())

    carpetas.extend((Path.home() / "Downloads", Path.home() / "Descargas"))
    unicas = []
    for carpeta in carpetas:
        carpeta = carpeta.resolve()
        if carpeta not in unicas:
            unicas.append(carpeta)
    return tuple(unicas)


def _zips(carpetas: tuple[Path, ...]) -> set[Path]:
    encontrados = set()
    for carpeta in carpetas:
        if carpeta.is_dir():
            encontrados.update(p.resolve() for p in carpeta.glob("*.zip") if p.is_file())
    return encontrados


def _zip_estable(ruta: Path) -> bool:
    if not ruta.is_file():
        return False
    tamano = ruta.stat().st_size
    if tamano <= 0:
        return False
    time.sleep(1)
    return ruta.is_file() and ruta.stat().st_size == tamano and is_zipfile(ruta)


def esperar_descarga_mexican_bread() -> Path:
    """Abre la descarga YOLO26 y devuelve el ZIP nuevo cuando el navegador termina."""
    carpetas = _carpetas_descargas()
    existentes = _zips(carpetas)

    print("No encontré el dataset local.")
    print("Abriendo Mexican Bread v3 en tu navegador...")
    print("En Roboflow elige 'Download zip to computer' y continúa.")
    print("El programa detectará el ZIP automáticamente y seguirá solo.\n")

    abierto = webbrowser.open(DOWNLOAD_PAGE, new=2)
    if not abierto:
        print(f"Abre manualmente esta página:\n{DOWNLOAD_PAGE}\n")

    limite = time.monotonic() + TIMEOUT_SECONDS
    while time.monotonic() < limite:
        nuevos = _zips(carpetas) - existentes
        if nuevos:
            preferidos = [p for p in nuevos if "mexican" in p.name.casefold() or "bread" in p.name.casefold()]
            candidatos = preferidos or list(nuevos)
            candidato = max(candidatos, key=lambda p: p.stat().st_mtime)
            if _zip_estable(candidato):
                print(f"Dataset descargado: {candidato}")
                return candidato
        time.sleep(1)

    ubicaciones = "\n".join(str(carpeta) for carpeta in carpetas)
    raise RuntimeError(
        "No apareció un ZIP nuevo en la carpeta de descargas en 15 minutos. "
        f"Puedes descargarlo manualmente desde {DOWNLOAD_PAGE}.\nCarpetas vigiladas:\n{ubicaciones}"
    )
