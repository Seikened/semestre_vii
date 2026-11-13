"""Compara la longitud completa y la complejidad QR de los enlaces."""

from dataclasses import asdict
from urllib.parse import urlsplit

from ..codec import compactar, descompactar
from ..codec.qr import medir_qr

BASE = "https://rd.epok.com.mx"  # Solo simulación: /c/ NO está desplegado.


def comparar(url: str, base: str = BASE) -> dict:
    partes = urlsplit(base)
    if (
        partes.scheme.lower() != "https"
        or not partes.hostname
        or partes.path not in ("", "/")
        or partes.query
        or partes.fragment
    ):
        raise ValueError("La base experimental debe ser un origen HTTPS sin ruta, query ni fragmento")
    origen = base.rstrip("/")
    token_url = compactar(url, "url")
    token_qr = compactar(url, "qr")
    if descompactar(token_url) != url or descompactar(token_qr) != url:
        raise ValueError("La recuperación no coincide con la URL original")
    enlace_url = f"{origen}/c/{token_url}"
    # El modo alfanumérico QR requiere protocolo, host y ruta en mayúsculas.
    enlace_qr = f"{origen.upper()}/C/{token_qr}"
    muestras = {"original": url, "compacto_url": enlace_url, "compacto_qr": enlace_qr}
    metricas = {
        nombre: {
            "caracteres": len(valor),
            "bytes_utf8": len(valor.encode("utf-8")),
            "qr": asdict(medir_qr(valor)),
        }
        for nombre, valor in muestras.items()
    }
    return {
        "token_url": token_url,
        "token_qr": token_qr,
        "muestras": muestras,
        "metricas": metricas,
        "recuperacion_exacta": True,
        "simulacion": True,
    }
