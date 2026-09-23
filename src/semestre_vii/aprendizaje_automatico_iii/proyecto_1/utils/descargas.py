"""Utilidades para abrir Roboflow y localizar ZIPs descargados."""

import os
import re
import time
import webbrowser
from pathlib import Path
from zipfile import is_zipfile

TIMEOUT_SECONDS = 15 * 60

MEXICAN_BREAD = {
    "nombre": "Mexican Bread v3",
    "pagina": "https://universe.roboflow.com/jpia/mexican-bread/dataset/3/download/yolo26",
    "palabras_zip": ("mexican", "bread"),
}

BREAD_DETECTOR = {
    "nombre": "Bread Detector v2",
    "pagina": "https://universe.roboflow.com/breaddetector/bread-detector/dataset/2/download/yolo26",
    "palabras_zip": ("bread", "detector"),
}


def carpetas_descargas():
    carpetas = []
    configuracion = Path.home() / ".config" / "user-dirs.dirs"

    if configuracion.is_file():
        texto = configuracion.read_text(encoding="utf-8", errors="ignore")
        coincidencia = re.search(r'^XDG_DOWNLOAD_DIR="([^"]+)"', texto, re.MULTILINE)
        if coincidencia:
            valor = coincidencia.group(1).replace("$HOME", str(Path.home()))
            carpetas.append(Path(os.path.expandvars(valor)).expanduser())

    carpetas.extend((Path.home() / "Downloads", Path.home() / "Descargas"))

    resultado = []
    for carpeta in carpetas:
        carpeta = carpeta.resolve()
        if carpeta not in resultado:
            resultado.append(carpeta)

    return tuple(resultado)


def zips(carpetas):
    encontrados = set()
    for carpeta in carpetas:
        if carpeta.is_dir():
            encontrados.update(ruta.resolve() for ruta in carpeta.glob("*.zip") if ruta.is_file())
    return encontrados


def coincide(ruta, dataset):
    nombre = ruta.name.casefold()
    return all(palabra in nombre for palabra in dataset["palabras_zip"])


def zip_estable(ruta):
    if not ruta.is_file() or ruta.stat().st_size <= 0:
        return False

    tamano = ruta.stat().st_size
    time.sleep(1)
    return ruta.is_file() and ruta.stat().st_size == tamano and is_zipfile(ruta)


def zip_existente(carpetas, dataset):
    candidatos = sorted(
        (ruta for ruta in zips(carpetas) if coincide(ruta, dataset)),
        key=lambda ruta: ruta.stat().st_mtime,
        reverse=True,
    )

    for candidato in candidatos:
        if zip_estable(candidato):
            return candidato

    return None


def esperar_descarga(dataset):
    carpetas = carpetas_descargas()
    existente = zip_existente(carpetas, dataset)

    if existente is not None:
        print(f"Dataset ya descargado: {existente}")
        return existente

    existentes = zips(carpetas)
    print(f"No encontré {dataset['nombre']} localmente.")
    print(f"Abriendo {dataset['nombre']} en tu navegador...")
    print("En Roboflow elige 'Download zip to computer'.")
    print("El programa detectará el ZIP y continuará solo.\n")

    if not webbrowser.open(dataset["pagina"], new=2):
        print(f"Abre manualmente esta página:\n{dataset['pagina']}\n")

    limite = time.monotonic() + TIMEOUT_SECONDS

    while time.monotonic() < limite:
        nuevos = zips(carpetas) - existentes

        if nuevos:
            preferidos = [ruta for ruta in nuevos if coincide(ruta, dataset)]
            candidato = max(preferidos or list(nuevos), key=lambda ruta: ruta.stat().st_mtime)

            if zip_estable(candidato):
                print(f"Dataset descargado: {candidato}")
                return candidato

        time.sleep(1)

    ubicaciones = "\n".join(str(carpeta) for carpeta in carpetas)
    raise RuntimeError(
        "No apareció un ZIP nuevo en 15 minutos. "
        f"Puedes descargarlo manualmente desde {dataset['pagina']}.\n"
        f"Carpetas vigiladas:\n{ubicaciones}"
    )


def descargar_mexican_bread():
    return esperar_descarga(MEXICAN_BREAD)


def descargar_bread_detector():
    return esperar_descarga(BREAD_DETECTOR)
