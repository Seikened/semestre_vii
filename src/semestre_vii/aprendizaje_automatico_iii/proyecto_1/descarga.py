"""Descarga el dataset público Mexican Bread v3 sin guardar credenciales."""

from html import unescape
from itertools import chain
from pathlib import Path
import re
from urllib.parse import urljoin
from zipfile import is_zipfile

import httpx

DATASET_PAGE = "https://universe.roboflow.com/jpia/mexican-bread/dataset/3"
DOWNLOAD_PAGE = f"{DATASET_PAGE}/download/yolo26"
API_EXPORT = "https://api.roboflow.com/jpia/mexican-bread/3/yolo26"
MAX_DOWNLOAD_BYTES = 8 * 1024**3
CHUNK_SIZE = 1024 * 1024

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/153 Safari/537.36",
    "Accept": "text/html,application/zip,application/octet-stream;q=0.9,*/*;q=0.8",
}


def _normalizar_html(texto: str) -> str:
    return unescape(texto).replace("\\/", "/").replace("\\u0026", "&")


def _enlaces_de_descarga(texto: str, base_url: str) -> list[str]:
    """Extrae enlaces firmados o endpoints de descarga presentes en la página."""
    texto = _normalizar_html(texto)
    urls = re.findall(r"https?://[^\"'<>\s]+", texto)
    relativos = re.findall(r"[\"']([^\"']*(?:/ds/|/download/)[^\"']*)[\"']", texto)
    urls.extend(urljoin(base_url, ruta) for ruta in relativos)

    encontrados = []
    for url in urls:
        url = url.rstrip("),]}\\")
        if ("/ds/" in url or "/download/" in url) and url not in encontrados:
            encontrados.append(url)
    return encontrados


def _descargar_si_zip(cliente: httpx.Client, url: str, destino: Path) -> tuple[bool, str]:
    temporal = destino.with_suffix(destino.suffix + ".part")
    temporal.unlink(missing_ok=True)
    texto = bytearray()
    total = 0

    try:
        with cliente.stream("GET", url) as respuesta:
            respuesta.raise_for_status()
            bloques = respuesta.iter_bytes(CHUNK_SIZE)
            primero = next(bloques, b"")
            if not primero:
                return False, ""

            if not primero.startswith(b"PK"):
                texto.extend(primero[: 2 * CHUNK_SIZE])
                for bloque in bloques:
                    if len(texto) >= 2 * CHUNK_SIZE:
                        break
                    texto.extend(bloque[: 2 * CHUNK_SIZE - len(texto)])
                return False, texto.decode("utf-8", errors="ignore")

            destino.parent.mkdir(parents=True, exist_ok=True)
            with temporal.open("wb") as archivo:
                for bloque in chain((primero,), bloques):
                    if total + len(bloque) > MAX_DOWNLOAD_BYTES:
                        raise RuntimeError("La descarga excedió el límite de seguridad de 8 GiB.")
                    archivo.write(bloque)
                    total += len(bloque)
                    print(f"\rDescargando dataset: {total / 1024**2:,.1f} MiB", end="", flush=True)
    except Exception:
        temporal.unlink(missing_ok=True)
        raise

    print()
    if not is_zipfile(temporal):
        temporal.unlink(missing_ok=True)
        return False, ""
    temporal.replace(destino)
    return True, ""


def _enlace_desde_api(cliente: httpx.Client) -> str | None:
    """Algunas exportaciones públicas exponen el enlace sin autenticación."""
    try:
        respuesta = cliente.get(API_EXPORT)
    except httpx.HTTPError:
        return None
    if respuesta.status_code != 200:
        return None
    try:
        contenido = respuesta.json()
    except ValueError:
        return None
    exportacion = contenido.get("export") if isinstance(contenido, dict) else None
    if isinstance(exportacion, dict) and isinstance(exportacion.get("link"), str):
        return exportacion["link"]
    return None


def descargar_mexican_bread(destino: Path) -> Path:
    """Descarga el ZIP YOLO26 público y lo deja listo para el importador local."""
    destino = destino.expanduser().resolve()
    if destino.is_file():
        return destino

    print("No encontré el dataset local. Descargando Mexican Bread v3...")
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=60) as cliente:
        candidatos = [DOWNLOAD_PAGE, f"{DOWNLOAD_PAGE}?download=1"]
        enlace_api = _enlace_desde_api(cliente)
        if enlace_api:
            candidatos.insert(0, enlace_api)

        vistos = set()
        while candidatos:
            url = candidatos.pop(0)
            if url in vistos:
                continue
            vistos.add(url)
            try:
                listo, pagina = _descargar_si_zip(cliente, url, destino)
            except httpx.HTTPError:
                continue
            if listo:
                return destino
            candidatos.extend(enlace for enlace in _enlaces_de_descarga(pagina, url) if enlace not in vistos)

    raise RuntimeError(
        "Roboflow no expuso una descarga ZIP pública utilizable desde Python. "
        f"Revisa que {DOWNLOAD_PAGE} siga disponible."
    )
