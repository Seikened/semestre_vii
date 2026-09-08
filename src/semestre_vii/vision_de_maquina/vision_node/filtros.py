import math
from numbers import Real

import kornia
import numpy as np
import torch
from scipy import ndimage

type Kernel = np.ndarray | torch.Tensor


def convolucion(
    tensor: torch.Tensor,
    kernel: Kernel,
    *,
    flip_kernel: bool = False,
) -> torch.Tensor:
    kernel_tensor = _preparar_kernel(kernel, tensor, dimensiones=2)
    alto, ancho = kernel_tensor.shape
    _validar_dimensiones_impares(alto, ancho)
    comportamiento = "conv" if flip_kernel else "corr"
    resultado = kornia.filters.filter2d(
        tensor.unsqueeze(0),
        kernel_tensor.unsqueeze(0),
        border_type="reflect",
        behaviour=comportamiento,
    )
    return resultado.squeeze(0).clamp(0.0, 1.0)


def convolucion_separable(tensor: torch.Tensor, kernel_1d: Kernel) -> torch.Tensor:
    kernel = _preparar_kernel(kernel_1d, tensor, dimensiones=1)
    _validar_tamano(kernel.numel())
    kernel = kernel.unsqueeze(0)
    resultado = kornia.filters.filter2d_separable(
        tensor.unsqueeze(0),
        kernel,
        kernel,
        border_type="reflect",
    )
    return resultado.squeeze(0).clamp(0.0, 1.0)


def suavizar(tensor: torch.Tensor, size: int = 3) -> torch.Tensor:
    _validar_tamano(size)
    resultado = kornia.filters.box_blur(tensor.unsqueeze(0), size, separable=True)
    return resultado.squeeze(0).clamp(0.0, 1.0)


def piramidal(tensor: torch.Tensor, size: int = 3) -> torch.Tensor:
    _validar_tamano(size)
    ventana = torch.bartlett_window(
        size + 2,
        periodic=False,
        dtype=tensor.dtype,
        device=tensor.device,
    )[1:-1]
    kernel = torch.outer(ventana, ventana)
    kernel /= kernel.sum()
    return convolucion(tensor, kernel)


def gaussiano(
    tensor: torch.Tensor,
    size: int = 3,
    sigma: float | None = None,
) -> torch.Tensor:
    _validar_tamano(size)
    sigma = _sigma_automatico(size) if sigma is None else sigma
    _validar_positivo("sigma", sigma)
    resultado = kornia.filters.gaussian_blur2d(
        tensor.unsqueeze(0),
        size,
        (sigma, sigma),
        border_type="reflect",
        separable=True,
    )
    return resultado.squeeze(0).clamp(0.0, 1.0)


def mediana(tensor: torch.Tensor, size: int = 3) -> torch.Tensor:
    _validar_tamano(size)
    resultado = kornia.filters.median_blur(tensor.unsqueeze(0), size)
    return resultado.squeeze(0).clamp(0.0, 1.0)


def mediana_cruz(tensor: torch.Tensor, size: int = 5) -> torch.Tensor:
    _validar_tamano(size)
    centro = size // 2
    mascara = np.zeros((size, size), dtype=bool)
    mascara[centro, :] = True
    mascara[:, centro] = True
    canales = [
        ndimage.median_filter(canal.detach().cpu().numpy(), footprint=mascara, mode="reflect")
        for canal in tensor
    ]
    resultado = np.stack(canales)
    return torch.as_tensor(resultado, dtype=tensor.dtype, device=tensor.device)


def filtro_sigma(tensor: torch.Tensor, size: int = 5, sigma: float = 10.0) -> torch.Tensor:
    _validar_tamano(size)
    _validar_positivo("sigma", sigma)
    lote = tensor.unsqueeze(0)
    media_local = kornia.filters.box_blur(lote, size, separable=True)
    media_cuadrada = kornia.filters.box_blur(lote.square(), size, separable=True)
    varianza_local = (media_cuadrada - media_local.square()).clamp_min(0.0)
    varianza_umbral = (sigma / 255.0) ** 2
    peso_suavizado = (varianza_umbral / (varianza_local + 1e-12)).clamp(0.0, 1.0)
    resultado = peso_suavizado * media_local + (1 - peso_suavizado) * lote
    return resultado.squeeze(0).clamp(0.0, 1.0)


def filtro_umbral(
    tensor: torch.Tensor,
    filtrada: torch.Tensor,
    umbral: float = 0.15,
) -> torch.Tensor:
    if filtrada.shape != tensor.shape:
        raise ValueError(f"shape incompatible: {tuple(filtrada.shape)} vs {tuple(tensor.shape)}")
    _validar_no_negativo("umbral", umbral)
    mascara = (tensor - filtrada).abs() > umbral
    return torch.where(mascara, filtrada, tensor)


def sal_y_pimienta(
    tensor: torch.Tensor,
    cantidad: float = 0.05,
    proporcion_sal: float = 0.5,
    seed: int | None = None,
) -> torch.Tensor:
    _validar_proporcion("cantidad", cantidad)
    _validar_proporcion("proporcion_sal", proporcion_sal)
    ruido = kornia.augmentation.RandomSaltAndPepperNoise(
        amount=cantidad,
        salt_vs_pepper=proporcion_sal,
        p=1.0,
        keepdim=True,
    )
    if seed is None:
        return ruido(tensor)
    with torch.random.fork_rng():
        torch.manual_seed(seed)
        return ruido(tensor)


def ruido_uniforme(
    tensor: torch.Tensor,
    amplitud: float = 0.1,
    seed: int | None = None,
) -> torch.Tensor:
    _validar_no_negativo("amplitud", amplitud)
    generador = None
    if seed is not None:
        generador = torch.Generator(device=tensor.device).manual_seed(seed)
    ruido = torch.rand(
        tensor.shape,
        dtype=tensor.dtype,
        device=tensor.device,
        generator=generador,
    )
    return (tensor + (ruido * 2 - 1) * amplitud).clamp(0.0, 1.0)


def laplaciano(
    tensor: torch.Tensor,
    *,
    extendido: bool = False,
    valor_absoluto: bool = True,
    crudo: bool = False,
) -> torch.Tensor:
    lote = tensor.unsqueeze(0)
    if extendido:
        derivada = kornia.filters.laplacian(lote, 3, normalized=False)
    else:
        kernel = torch.tensor(
            [[0, 1, 0], [1, -4, 1], [0, 1, 0]],
            dtype=tensor.dtype,
            device=tensor.device,
        )
        derivada = kornia.filters.filter2d(lote, kernel.unsqueeze(0), border_type="reflect")
    derivada = derivada.squeeze(0)
    if crudo:
        return derivada

    pico = derivada.abs().max()
    if pico.item() == 0:
        return torch.zeros_like(derivada)
    if valor_absoluto:
        return derivada.abs() / pico
    return (derivada / pico + 1) / 2


def _preparar_kernel(
    kernel: Kernel,
    tensor: torch.Tensor,
    *,
    dimensiones: int,
) -> torch.Tensor:
    preparado = torch.as_tensor(kernel, dtype=tensor.dtype, device=tensor.device)
    if preparado.ndim != dimensiones:
        raise ValueError(f"kernel debe tener {dimensiones} dimensiones")
    return preparado


def _validar_dimensiones_impares(alto: int, ancho: int) -> None:
    _validar_tamano(alto)
    _validar_tamano(ancho)


def _validar_tamano(size: int) -> None:
    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError("size debe ser un entero")
    if size < 1 or size % 2 == 0:
        raise ValueError("size debe ser impar y mayor o igual a uno")


def _sigma_automatico(size: int) -> float:
    return 0.3 * ((size - 1) / 2 - 1) + 0.8


def _validar_proporcion(nombre: str, valor: float) -> None:
    _validar_finito(nombre, valor)
    if not 0 <= valor <= 1:
        raise ValueError(f"{nombre} debe estar entre cero y uno")


def _validar_no_negativo(nombre: str, valor: float) -> None:
    _validar_finito(nombre, valor)
    if valor < 0:
        raise ValueError(f"{nombre} debe ser mayor o igual a cero")


def _validar_positivo(nombre: str, valor: float) -> None:
    _validar_finito(nombre, valor)
    if valor <= 0:
        raise ValueError(f"{nombre} debe ser mayor que cero")


def _validar_finito(nombre: str, valor: float) -> None:
    es_numero = isinstance(valor, Real) and not isinstance(valor, bool)
    if not es_numero:
        raise TypeError(f"{nombre} debe ser un número")
    if not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser finito")
