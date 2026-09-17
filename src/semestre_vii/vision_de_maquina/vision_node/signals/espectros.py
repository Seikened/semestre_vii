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
    espectro = torch.fft.fft2(canal)
    return torch.fft.fftshift(espectro, dim=(-2, -1)) if centrada else espectro


def transformada_centrada(tensor: torch.Tensor) -> torch.Tensor:
    return torch.fft.fftshift(torch.fft.fft2(tensor), dim=(-2, -1))


def inversa_2d(espectro: torch.Tensor, *, centrado: bool = True, valor_absoluto: bool = False) -> torch.Tensor:
    entrada = torch.fft.ifftshift(espectro, dim=(-2, -1)) if centrado else espectro
    imagen = torch.fft.ifft2(entrada)
    return imagen.abs() if valor_absoluto else imagen.real


def magnitud_visual(espectro: torch.Tensor, *, logaritmica: bool = True) -> torch.Tensor:
    magnitud = espectro.abs()
    if logaritmica:
        magnitud = torch.log1p(magnitud)
    return normalize_min_max(magnitud)


def mascara_pasabajas_ideal(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    """ILPF del profesor: H(u,v)=1 si D(u,v)<D0 y 0 en otro caso."""
    _validar_corte(corte)
    return (_radio(tensor) < corte).to(tensor.real.dtype)


def mascara_pasabajas_gaussiano(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    """GLPF del profesor: H(u,v)=exp(-D(u,v)^2 / (2 D0^2))."""
    _validar_corte(corte)
    radio = _radio(tensor)
    return torch.exp(-radio.square() / (2 * corte**2))


def mascara_pasabajas_butterworth(tensor: torch.Tensor, corte: float, orden: int = 2) -> torch.Tensor:
    """BLPF: H(u,v)=1/(1+(D(u,v)/D0)^(2n))."""
    _validar_corte(corte)
    _validar_orden(orden)
    radio = _radio(tensor)
    return 1 / (1 + (radio / corte).pow(2 * orden))


def mascara_pasaaltas_ideal(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    """IHPF del profesor: H(u,v)=1 si D(u,v)>D0 y 0 en otro caso."""
    _validar_corte(corte)
    return (_radio(tensor) > corte).to(tensor.real.dtype)


def mascara_pasaaltas_gaussiano(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    """GHPF: H(u,v)=1-exp(-D(u,v)^2 / (2 D0^2))."""
    return 1 - mascara_pasabajas_gaussiano(tensor, corte)


def mascara_pasaaltas_butterworth(tensor: torch.Tensor, corte: float, orden: int = 2) -> torch.Tensor:
    """BHPF: H(u,v)=1/(1+(D0/D(u,v))^(2n)), evaluado como 1-BLPF."""
    return 1 - mascara_pasabajas_butterworth(tensor, corte, orden)


def aplicar_mascara(espectro: torch.Tensor, mascara: torch.Tensor) -> torch.Tensor:
    if mascara.shape != espectro.shape[-2:]:
        raise ValueError("la máscara debe coincidir con alto y ancho del espectro")
    return espectro * mascara


def pasabajas_ideal(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    espectro = transformada_centrada(tensor)
    return inversa_2d(aplicar_mascara(espectro, mascara_pasabajas_ideal(tensor, corte)))


def pasabajas_gaussiano(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    espectro = transformada_centrada(tensor)
    return inversa_2d(aplicar_mascara(espectro, mascara_pasabajas_gaussiano(tensor, corte)))


def pasabajas_butterworth(tensor: torch.Tensor, corte: float, orden: int = 2) -> torch.Tensor:
    espectro = transformada_centrada(tensor)
    mascara = mascara_pasabajas_butterworth(tensor, corte, orden)
    return inversa_2d(aplicar_mascara(espectro, mascara))


def pasaaltas_ideal(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    espectro = transformada_centrada(tensor)
    return inversa_2d(aplicar_mascara(espectro, mascara_pasaaltas_ideal(tensor, corte)))


def pasaaltas_gaussiano(tensor: torch.Tensor, corte: float) -> torch.Tensor:
    espectro = transformada_centrada(tensor)
    return inversa_2d(aplicar_mascara(espectro, mascara_pasaaltas_gaussiano(tensor, corte)))


def pasaaltas_butterworth(tensor: torch.Tensor, corte: float, orden: int = 2) -> torch.Tensor:
    espectro = transformada_centrada(tensor)
    mascara = mascara_pasaaltas_butterworth(tensor, corte, orden)
    return inversa_2d(aplicar_mascara(espectro, mascara))


def _radio(tensor: torch.Tensor) -> torch.Tensor:
    alto, ancho = tensor.shape[-2:]
    dtype = tensor.real.dtype if torch.is_complex(tensor) else tensor.dtype
    y, x = torch.meshgrid(
        torch.arange(alto, dtype=dtype, device=tensor.device),
        torch.arange(ancho, dtype=dtype, device=tensor.device),
        indexing="ij",
    )
    return torch.hypot(y - alto / 2, x - ancho / 2)


def _validar_corte(corte: float) -> None:
    if corte <= 0:
        raise ValueError("la frecuencia de corte D0 debe ser mayor que cero")


def _validar_orden(orden: int) -> None:
    if not isinstance(orden, int):
        raise TypeError("el orden de Butterworth debe ser int")
    if orden < 1:
        raise ValueError("el orden de Butterworth debe ser mayor o igual que 1")
