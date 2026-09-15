"""Transformadas y filtros aplicados sobre el espectro de Fourier."""

import torch
from kornia.enhance import normalize_min_max


def centrar(canal: torch.Tensor) -> torch.Tensor:
    alto, ancho = canal.shape[-2:]
    filas = torch.arange(alto, device=canal.device)
    columnas = torch.arange(ancho, device=canal.device)
    signos = 1 - 2 * ((filas[:, None] + columnas) % 2)
    return canal * signos.to(canal)


def transformada_2d(canal: torch.Tensor, *, centrada: bool = False) -> torch.Tensor:
    entrada = centrar(canal) if centrada else canal
    return torch.fft.fft2(entrada)


def magnitud_visual(espectro: torch.Tensor, *, logaritmica: bool = True) -> torch.Tensor:
    magnitud = espectro.abs()
    if logaritmica:
        magnitud = torch.log1p(magnitud)
    return normalize_min_max(magnitud)


def mascara_pasabajas_ideal(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    """ILPF del profesor: H(u,v)=1 si D(u,v)<D0 y 0 en otro caso."""
    _validar_corte(corte)
    return (_radio(tensor) < corte).to(tensor.dtype)


def mascara_pasabajas_gaussiano(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    """GLPF del profesor: H(u,v)=exp(-D(u,v)^2 / (2 D0^2))."""
    _validar_corte(corte)
    radio = _radio(tensor)
    return torch.exp(-radio.square() / (2 * corte**2))


def pasabajas_ideal(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    return _filtrar(tensor, mascara_pasabajas_ideal(tensor, corte))


def pasabajas_gaussiano(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    return _filtrar(tensor, mascara_pasabajas_gaussiano(tensor, corte))


def pasabajas_butterworth(tensor: torch.Tensor, corte: float, orden: int = 2) -> torch.Tensor:
    _validar_corte(corte)
    radio = _radio(tensor)
    mascara = 1 / (1 + (radio / corte).pow(2 * orden))
    return _filtrar(tensor, mascara)


def _filtrar(tensor: torch.Tensor, mascara: torch.Tensor) -> torch.Tensor:
    espectro = torch.fft.fftshift(torch.fft.fft2(tensor), dim=(-2, -1))
    filtrado = torch.fft.ifftshift(espectro * mascara, dim=(-2, -1))
    return torch.fft.ifft2(filtrado).real.clamp(0, 1)


def _radio(tensor: torch.Tensor) -> torch.Tensor:
    alto, ancho = tensor.shape[-2:]
    y, x = torch.meshgrid(
        torch.arange(alto, dtype=tensor.dtype, device=tensor.device),
        torch.arange(ancho, dtype=tensor.dtype, device=tensor.device),
        indexing="ij",
    )
    return torch.hypot(y - alto / 2, x - ancho / 2)


def _validar_corte(corte: float) -> None:
    if corte <= 0:
        raise ValueError("La frecuencia de corte D0 debe ser mayor que cero.")
