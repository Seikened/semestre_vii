"""Estimador QR de un solo modo, nivel de corrección M (15%).

Calcula el menor QR estándar que cabe sin segmentación mixta ni ECI.
La cantidad de datos por versión proviene de las tablas ISO/IEC 18004.
"""

from dataclasses import dataclass

# Codewords de datos para ECC M, versiones 1 a 40.
DATOS_M = (
    16, 28, 44, 64, 86, 108, 124, 154, 182, 216,
    254, 290, 334, 365, 415, 453, 507, 563, 627, 669,
    714, 782, 860, 914, 1000, 1062, 1128, 1193, 1267, 1373,
    1455, 1541, 1631, 1725, 1812, 1914, 1992, 2102, 2216, 2334,
)
ALFANUMERICO = frozenset("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")


@dataclass(frozen=True)
class MetricaQR:
    version: int | None
    modulos: int | None
    modo: str


def medir_qr(texto: str) -> MetricaQR:
    alfanumerico = all(c in ALFANUMERICO for c in texto)
    longitud = len(texto) if alfanumerico else len(texto.encode("utf-8"))
    bits_carga = 11 * (longitud // 2) + 6 * (longitud % 2) if alfanumerico else 8 * longitud
    for version, palabras in enumerate(DATOS_M, start=1):
        if alfanumerico:
            bits_longitud = 9 if version <= 9 else 11 if version <= 26 else 13
        else:
            bits_longitud = 8 if version <= 9 else 16
        if 4 + bits_longitud + bits_carga <= 8 * palabras:
            return MetricaQR(version, 17 + 4 * version, "alfanumérico" if alfanumerico else "byte")
    return MetricaQR(None, None, "alfanumérico" if alfanumerico else "byte")
