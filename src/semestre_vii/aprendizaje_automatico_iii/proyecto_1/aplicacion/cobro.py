"""Reglas deterministas, independientes de YOLO, OpenCV y archivos."""

import unicodedata
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .precios import PRODUCTOS, Producto


def normalizar(nombre: str) -> str:
    texto = unicodedata.normalize("NFKD", nombre.strip().casefold())
    return " ".join("".join(c for c in texto if not unicodedata.combining(c)).split())


def catalogo(productos: Mapping[str, Producto]) -> dict[str, Producto]:
    resultado = {}
    for etiqueta, producto in productos.items():
        clave = normalizar(etiqueta)
        if not clave or clave in resultado:
            raise ValueError(f"Etiqueta vacía o duplicada en productos: {etiqueta!r}")
        if not producto.nombre.strip():
            raise ValueError(f"Falta el nombre visible de {etiqueta!r}.")
        if type(producto.precio_centavos) is not int or producto.precio_centavos < 0:
            raise ValueError(f"El precio de {etiqueta} debe ser un entero no negativo en centavos.")
        resultado[clave] = producto
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


def calcular_ticket(clases: Iterable[str], productos: Mapping[str, Producto] = PRODUCTOS) -> Ticket:
    """Cuenta sólo esta imagen. Una clase sin precio invalida el total, nunca vale cero."""
    referencias = catalogo(productos)
    cantidades = Counter(normalizar(clase) for clase in clases)
    renglones = []
    for clave, cantidad in sorted(cantidades.items()):
        producto = referencias.get(clave)
        nombre = producto.nombre if producto else clave or "sin clase"
        precio = producto.precio_centavos if producto else None
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
