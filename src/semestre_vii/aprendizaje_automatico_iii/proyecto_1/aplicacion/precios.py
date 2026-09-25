"""Etiqueta del modelo: nombre visible y precio ficticio en centavos MXN."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Producto:
    nombre: str
    precio_centavos: int


PRODUCTOS = {
    "baguette": Producto("Baguette", 2500),
    "binangkal": Producto("Pan binangkal", 1200),
    "bonete": Producto("Pan de bonete", 1300),
    "cornbread": Producto("Pan de maíz", 1800),
    "croissant": Producto("Cuernito", 1400),
    "ensaymada": Producto("Ensaimada", 1600),
    "flatbread": Producto("Pan plano", 1600),
    "kalihim": Producto("Pan kalihim", 1600),
    "monay": Producto("Pan monay", 1200),
    "pandesal": Producto("Pan de sal", 800),
    "sourdough": Producto("Pan de masa madre", 2800),
    "spanish-bread": Producto("Pan dulce filipino", 1500),
    "wheat-bread": Producto("Pan de trigo", 1500),
    "white-bread": Producto("Pan blanco", 1400),
    "whole-grain-bread": Producto("Pan integral", 1600),
    "Bolillo": Producto("Bolillo", 500),
    "Concha": Producto("Concha", 1200),
    "Cuernito": Producto("Cuernito", 1400),
    "Dona": Producto("Dona", 1500),
    "Mantecada": Producto("Mantecada", 1300),
    "Oreja": Producto("Oreja", 1400),
    "Pinguino": Producto("Pingüino", 1800),
    "Rebanada": Producto("Rebanada", 1200),
    "Reja": Producto("Reja", 1300),
    "Telera": Producto("Telera", 600),
    "Torta": Producto("Torta", 2000),
}
