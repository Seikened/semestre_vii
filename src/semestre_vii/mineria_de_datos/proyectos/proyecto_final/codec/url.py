"""Formato experimental v1: versión, modo/prefijo y cuerpo bruto o DEFLATE."""

import zlib
from urllib.parse import urlsplit

from .alfabetos import codificar, decodificar
from .compresion import comprimir, descomprimir

LIMITE_URL = 8192  # bytes UTF-8
VERSION = 1
PREFIJOS = (b"https://www.", b"https://", b"http://www.", b"http://", b"")
MODO_DEFLATE = 0x80


def validar(url: str) -> bytes:
    if not isinstance(url, str) or not url:
        raise ValueError("Se requiere una URL HTTP(S) sin caracteres de control")
    if any(ord(c) < 32 or ord(c) == 127 for c in url):
        raise ValueError("Se requiere una URL HTTP(S) sin caracteres de control")
    try:
        datos = url.encode("utf-8")
        partes = urlsplit(url)
        if partes.scheme.lower() not in ("http", "https") or not partes.hostname:
            raise ValueError("Se requiere una URL HTTP(S) con host")
    except (UnicodeError, ValueError) as error:
        raise ValueError("URL inválida") from error
    if len(datos) > LIMITE_URL:
        raise ValueError("La URL supera 8192 bytes UTF-8")
    return datos


def compactar(url: str, formato: str = "url") -> str:
    datos = validar(url)
    indice = 4
    for posicion, prefijo in enumerate(PREFIJOS[:-1]):
        if datos.startswith(prefijo):
            indice = posicion
            break
    cuerpo = datos[len(PREFIJOS[indice]):]
    comprimido = comprimir(cuerpo)
    usar_deflate = len(comprimido) < len(cuerpo)
    carga = comprimido if usar_deflate else cuerpo
    cabecera = bytes((VERSION, indice | (MODO_DEFLATE if usar_deflate else 0)))
    return codificar(cabecera + carga, formato)


def descompactar(token: str) -> str:
    datos = decodificar(token)
    if len(datos) < 2 or datos[0] != VERSION:
        raise ValueError("Versión de códec desconocida")
    modo = datos[1]
    indice = modo & 0x7F
    if indice >= len(PREFIJOS):
        raise ValueError("Prefijo desconocido")
    try:
        cuerpo = descomprimir(datos[2:], LIMITE_URL) if modo & MODO_DEFLATE else datos[2:]
        url = (PREFIJOS[indice] + cuerpo).decode("utf-8")
    except (UnicodeError, zlib.error) as error:
        raise ValueError("Token dañado") from error
    validar(url)
    return url
