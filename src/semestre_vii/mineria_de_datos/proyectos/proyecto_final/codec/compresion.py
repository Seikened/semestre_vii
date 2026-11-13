"""Baseline DEFLATE adaptado de EPOK Links v0.3.0.

Origen: Seikened/epok_links, commit 626614f, tokens/compresion.py.
"""

import zlib


def comprimir(contenido: bytes) -> bytes:
    return zlib.compress(contenido, level=9, wbits=-zlib.MAX_WBITS)


def descomprimir(contenido: bytes, limite: int) -> bytes:
    descompresor = zlib.decompressobj(-zlib.MAX_WBITS)
    plano = descompresor.decompress(contenido, limite + 1)
    if len(plano) > limite:
        raise ValueError("El contenido reconstruido supera el límite")
    if not descompresor.eof or descompresor.unused_data or descompresor.unconsumed_tail:
        raise ValueError("El flujo comprimido es inválido o está incompleto")
    return plano
