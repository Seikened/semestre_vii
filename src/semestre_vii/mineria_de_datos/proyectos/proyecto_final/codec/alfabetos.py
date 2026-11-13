"""Alfabetos de transporte; no alteran el contenido binario del códec."""

from base64 import b32decode, b32encode, b64decode, urlsafe_b64encode
from binascii import Error


def codificar(contenido: bytes, formato: str) -> str:
    if formato == "url":
        return "u" + urlsafe_b64encode(contenido).rstrip(b"=").decode("ascii")
    if formato == "qr":
        return "Q" + b32encode(contenido).rstrip(b"=").decode("ascii")
    raise ValueError("Formato desconocido: usar 'url' o 'qr'")


def decodificar(token: str) -> bytes:
    if not isinstance(token, str) or len(token) < 2 or len(token) > 16000:
        raise ValueError("Token inválido")
    formato, valor = token[0], token[1:]
    try:
        if formato == "u":
            datos = b64decode(valor + "=" * (-len(valor) % 4), altchars=b"-_", validate=True)
            esperado = codificar(datos, "url")
        elif formato == "Q":
            datos = b32decode(valor + "=" * (-len(valor) % 8), casefold=False)
            esperado = codificar(datos, "qr")
        else:
            raise ValueError("Alfabeto desconocido")
    except (Error, ValueError, UnicodeError) as error:
        raise ValueError("Token inválido") from error
    if token != esperado:
        raise ValueError("Token no canónico")
    return datos
