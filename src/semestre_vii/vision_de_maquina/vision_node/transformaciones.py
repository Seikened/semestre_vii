import math
from collections.abc import Sequence
from itertools import pairwise
from numbers import Real

import kornia
import matplotlib as mpl
import torch

type PuntosControl = Sequence[tuple[float, float]]


def promediar(tensor: torch.Tensor, otros: Sequence[torch.Tensor]) -> torch.Tensor:
    for otro in otros:
        if otro.shape != tensor.shape:
            raise ValueError(f"shape incompatible: {tuple(otro.shape)} vs {tuple(tensor.shape)}")
    return torch.stack((tensor, *otros)).mean(dim=0)


def clip(tensor: torch.Tensor, minimo: float = 0.0, maximo: float = 1.0) -> torch.Tensor:
    _validar_intervalo(minimo, maximo)
    return tensor.clamp(min=minimo, max=maximo)


def negativo(tensor: torch.Tensor) -> torch.Tensor:
    return kornia.enhance.invert(tensor)


def escala_grises(tensor: torch.Tensor) -> torch.Tensor:
    if tensor.shape[0] == 1:
        return tensor.clone()
    return kornia.color.rgb_to_grayscale(tensor)


def separar_canales(tensor: torch.Tensor) -> dict[str, torch.Tensor]:
    _validar_rgb(tensor, "separar canales")
    return {
        "Rojo": tensor[0:1],
        "Verde": tensor[1:2],
        "Azul": tensor[2:3],
    }


def separar_hsv(tensor: torch.Tensor) -> dict[str, torch.Tensor]:
    _validar_rgb(tensor, "separar HSV")
    matiz, saturacion_hsv, valor = kornia.color.rgb_to_hsv(tensor).split(1)
    return {
        "Matiz": matiz / (2 * math.pi),
        "Saturación": saturacion_hsv,
        "Valor": valor,
    }


def saturacion(tensor: torch.Tensor) -> torch.Tensor:
    return separar_hsv(tensor)["Saturación"]


def acromaticidad(tensor: torch.Tensor) -> torch.Tensor:
    _validar_rgb(tensor, "calcular acromaticidad")
    return tensor.amin(dim=0, keepdim=True)


def ganancia(tensor: torch.Tensor, factor: float) -> torch.Tensor:
    _validar_finito("factor", factor)
    if factor < 0:
        raise ValueError("factor debe ser mayor o igual a cero")
    return kornia.enhance.adjust_contrast(tensor, factor)


def estirar_contraste(tensor: torch.Tensor) -> torch.Tensor:
    if tensor.max() == tensor.min():
        return tensor.clone()
    lote = tensor.contiguous().reshape(1, 1, -1)
    return kornia.enhance.normalize_min_max(lote).reshape_as(tensor)


def binarizar(tensor: torch.Tensor, umbral: float) -> torch.Tensor:
    _validar_finito("umbral", umbral)
    return (tensor >= umbral).to(dtype=tensor.dtype)


def binarizar_rango(
    tensor: torch.Tensor,
    minimo: float,
    maximo: float,
) -> torch.Tensor:
    _validar_intervalo(minimo, maximo)
    return ((tensor >= minimo) & (tensor <= maximo)).to(dtype=tensor.dtype)


def binarizar_adaptativo(
    tensor: torch.Tensor,
    kernel_size: int = 15,
    c: float = 0.05,
) -> torch.Tensor:
    _validar_kernel_impar(kernel_size, "kernel_size")
    _validar_finito("c", c)
    media_local = kornia.filters.box_blur(
        tensor.unsqueeze(0),
        kernel_size,
        separable=True,
    ).squeeze(0)
    return (tensor > media_local - c).to(dtype=tensor.dtype)


def transformacion_log(tensor: torch.Tensor) -> torch.Tensor:
    return kornia.enhance.adjust_log(tensor.clamp(0.0, 1.0))


def transformacion_gamma(tensor: torch.Tensor, exponente: float) -> torch.Tensor:
    _validar_finito("exponente", exponente)
    if exponente <= 0:
        raise ValueError("exponente debe ser mayor que cero")
    return kornia.enhance.adjust_gamma(tensor.clamp(0.0, 1.0), exponente)


def cuantizar(tensor: torch.Tensor, bits: int) -> torch.Tensor:
    if isinstance(bits, bool) or not isinstance(bits, int):
        raise TypeError("bits debe ser un entero")
    if not 1 <= bits <= 16:
        raise ValueError("bits debe estar entre 1 y 16")
    nivel_maximo = (1 << bits) - 1
    normalizado = tensor.clamp(min=0.0, max=1.0)
    return torch.round(normalizado * nivel_maximo) / nivel_maximo


def pseudocolor_infrarrojo(tensor: torch.Tensor, mapa: str = "inferno") -> torch.Tensor:
    gris = escala_grises(tensor).squeeze(0).detach().cpu().numpy()
    coloreada = mpl.colormaps[mapa](gris)[..., :3]
    return torch.as_tensor(coloreada, dtype=tensor.dtype, device=tensor.device).permute(2, 0, 1)


def falso_color_infrarrojo(tensor: torch.Tensor) -> torch.Tensor:
    _validar_rgb(tensor, "aplicar falso color infrarrojo")
    return tensor[[1, 0, 2]]


def diferencia_absoluta(
    tensor: torch.Tensor,
    comparada: torch.Tensor,
    magnifier: float = 1.0,
) -> torch.Tensor:
    if tensor.shape != comparada.shape:
        raise ValueError(f"shape incompatible: {tuple(comparada.shape)} vs {tuple(tensor.shape)}")
    _validar_finito("magnifier", magnifier)
    if magnifier <= 0:
        raise ValueError("magnifier debe ser mayor que cero")
    return (tensor - comparada).abs().mul(magnifier).clamp(0.0, 1.0)


def transformacion_lineal(
    tensor: torch.Tensor,
    entrada: Sequence[float],
    salida: Sequence[float],
) -> torch.Tensor:
    entradas, salidas = _puntos_normalizados(tensor, entrada, salida)
    limitado = tensor.clamp(entradas[0].item(), entradas[-1].item()).contiguous()
    indices = torch.bucketize(limitado, entradas).clamp(1, len(entradas) - 1)
    entrada_inicial = entradas[indices - 1]
    entrada_final = entradas[indices]
    salida_inicial = salidas[indices - 1]
    salida_final = salidas[indices]
    proporcion = (limitado - entrada_inicial) / (entrada_final - entrada_inicial)
    interpolado = torch.lerp(salida_inicial, salida_final, proporcion)
    return interpolado.clamp(0.0, 1.0)


def transformacion_lineal_por_canal(
    tensor: torch.Tensor,
    rojo: PuntosControl,
    verde: PuntosControl,
    azul: PuntosControl,
) -> torch.Tensor:
    if tensor.shape[0] not in (1, 3):
        raise ValueError("la transformación por canal requiere uno o tres canales")
    fuentes = (tensor[0:1],) * 3 if tensor.shape[0] == 1 else tensor.split(1)
    canales = []
    for fuente, puntos in zip(fuentes, (rojo, verde, azul), strict=True):
        if len(puntos) < 2:
            raise ValueError("cada canal requiere al menos dos puntos de control")
        entrada, salida = zip(*puntos, strict=True)
        canales.append(transformacion_lineal(fuente, entrada, salida))
    return torch.cat(canales, dim=0)


def histograma_acumulado(tensor: torch.Tensor) -> torch.Tensor:
    total_pixeles = tensor.shape[1] * tensor.shape[2]
    acumulados = []
    for canal in tensor:
        indices = (canal.clamp(0.0, 1.0) * 255).round().to(torch.long)
        histograma = torch.bincount(indices.flatten(), minlength=256)
        acumulados.append(histograma.cumsum(0) / total_pixeles)
    return torch.stack(acumulados)


def ecualizar(tensor: torch.Tensor) -> torch.Tensor:
    return kornia.enhance.equalize(tensor.unsqueeze(0)).squeeze(0)


def _puntos_normalizados(
    tensor: torch.Tensor,
    entrada: Sequence[float],
    salida: Sequence[float],
) -> tuple[torch.Tensor, torch.Tensor]:
    if len(entrada) != len(salida) or len(entrada) < 2:
        raise ValueError("entrada y salida deben tener al menos dos puntos y la misma longitud")
    for nombre, valores in (("entrada", entrada), ("salida", salida)):
        for valor in valores:
            _validar_finito(nombre, valor)
            if not 0 <= valor <= 255:
                raise ValueError(f"{nombre} debe contener valores entre 0 y 255")
    if any(actual >= siguiente for actual, siguiente in pairwise(entrada)):
        raise ValueError("los puntos de entrada deben estar ordenados sin repetirse")
    entradas = torch.as_tensor(entrada, dtype=tensor.dtype, device=tensor.device) / 255
    salidas = torch.as_tensor(salida, dtype=tensor.dtype, device=tensor.device) / 255
    return entradas, salidas


def _validar_rgb(tensor: torch.Tensor, operacion: str) -> None:
    if tensor.shape[0] != 3:
        raise ValueError(f"se requieren tres canales RGB para {operacion}")


def _validar_kernel_impar(valor: int, nombre: str) -> None:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(f"{nombre} debe ser un entero")
    if valor < 1 or valor % 2 == 0:
        raise ValueError(f"{nombre} debe ser impar y mayor o igual a uno")


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
