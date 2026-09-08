import math
from numbers import Real

import torch


def clip(tensor: torch.Tensor, minimo: float = 0.0, maximo: float = 1.0) -> torch.Tensor:
    _validar_intervalo(minimo, maximo)
    return tensor.clamp(min=minimo, max=maximo)


def negativo(tensor: torch.Tensor) -> torch.Tensor:
    return 1.0 - tensor


def escala_grises(tensor: torch.Tensor) -> torch.Tensor:
    if tensor.shape[0] == 1:
        return tensor.clone()

    rojo, verde, azul = tensor.unbind(dim=0)
    gris = 0.299 * rojo + 0.587 * verde + 0.114 * azul
    return gris.unsqueeze(0)


def ganancia(tensor: torch.Tensor, factor: float) -> torch.Tensor:
    _validar_finito("factor", factor)
    if factor < 0:
        raise ValueError("factor debe ser mayor o igual a cero")
    return (tensor * factor).clamp(min=0.0, max=1.0)


def transformacion_gamma(tensor: torch.Tensor, exponente: float) -> torch.Tensor:
    _validar_finito("exponente", exponente)
    if exponente <= 0:
        raise ValueError("exponente debe ser mayor que cero")
    return tensor.clamp(min=0.0, max=1.0).pow(exponente)


def cuantizar(tensor: torch.Tensor, bits: int) -> torch.Tensor:
    if isinstance(bits, bool) or not isinstance(bits, int):
        raise TypeError("bits debe ser un entero")
    if not 1 <= bits <= 16:
        raise ValueError("bits debe estar entre 1 y 16")

    nivel_maximo = (1 << bits) - 1
    normalizado = tensor.clamp(min=0.0, max=1.0)
    return torch.round(normalizado * nivel_maximo) / nivel_maximo


def binarizar(tensor: torch.Tensor, umbral: float) -> torch.Tensor:
    _validar_finito("umbral", umbral)
    return (tensor >= umbral).to(dtype=tensor.dtype)


def binarizar_rango(
    tensor: torch.Tensor,
    minimo: float,
    maximo: float,
) -> torch.Tensor:
    _validar_intervalo(minimo, maximo)
    dentro_del_rango = (tensor >= minimo) & (tensor <= maximo)
    return dentro_del_rango.to(dtype=tensor.dtype)


def _validar_intervalo(minimo: float, maximo: float) -> None:
    _validar_finito("minimo", minimo)
    _validar_finito("maximo", maximo)
    if minimo > maximo:
        raise ValueError("minimo no puede ser mayor que maximo")


def _validar_finito(nombre: str, valor: float) -> None:
    es_numero = isinstance(valor, Real) and not isinstance(valor, bool)
    if not es_numero:
        raise TypeError(f"{nombre} debe ser un número")
    if not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser finito")
