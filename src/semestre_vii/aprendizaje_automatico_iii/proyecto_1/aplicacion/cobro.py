"""Reglas deterministas, independientes de YOLO, OpenCV y archivos."""

import unicodedata
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .precios import PRECIOS


def normalizar(nombre: str) -> str:
    texto = unicodedata.normalize("NFKD", nombre.strip().casefold())
    return " ".join("".join(c for c in texto if not unicodedata.combining(c)).split())


def catalogo(precios: Mapping[str, int]) -> dict[str, tuple[str, int]]:
    resultado = {}
    for nombre, precio in precios.items():
        clave = normalizar(nombre)
        if not clave or clave in resultado:
            raise ValueError(f"Nombre vacío o duplicado en precios: {nombre!r}")
        if type(precio) is not int or precio < 0:
            raise ValueError(f"El precio de {nombre} debe ser un entero no negativo en centavos.")
        resultado[clave] = (nombre, precio)
    return resultado


@dataclass(frozen=True)
class Renglon:
    clase: str
    cantidad: int
    precio_centavos: int | None
    subtotal_centavos: int | None


@dataclass(frozen=True)
class Ticket:
    renglones: tuple[Renglon, ...]
    piezas: int
    subtotal_conocido_centavos: int
    total_centavos: int | None

    @property
    def completo(self) -> bool:
        return self.total_centavos is not None


def calcular_ticket(clases: Iterable[str], precios: Mapping[str, int] = PRECIOS) -> Ticket:
    """Cuenta sólo esta imagen. Una clase sin precio invalida el total, nunca vale cero."""
    productos = catalogo(precios)
    cantidades = Counter(normalizar(clase) for clase in clases)
    renglones = []
    for clave, cantidad in sorted(cantidades.items()):
        nombre, precio = productos.get(clave, (clave or "sin clase", None))
        subtotal = None if precio is None else precio * cantidad
        renglones.append(Renglon(nombre, cantidad, precio, subtotal))
    conocido = sum(r.subtotal_centavos or 0 for r in renglones)
    completo = all(r.precio_centavos is not None for r in renglones)
    return Ticket(tuple(renglones), sum(cantidades.values()), conocido, conocido if completo else None)


class Estabilidad:
    """Indicador visual; nunca conserva un ticket viejo ni acumula detecciones."""

    def __init__(self, cuadros: int = 5) -> None:
        if cuadros < 1:
            raise ValueError("La estabilidad requiere al menos un cuadro.")
        self.cuadros = cuadros
        self.firma = None
        self.repeticiones = 0

    def actualizar(self, ticket: Ticket) -> bool:
        firma = tuple((r.clase, r.cantidad, r.precio_centavos) for r in ticket.renglones)
        self.repeticiones = self.repeticiones + 1 if firma == self.firma else 1
        self.firma = firma
        return ticket.completo and self.repeticiones >= self.cuadros
