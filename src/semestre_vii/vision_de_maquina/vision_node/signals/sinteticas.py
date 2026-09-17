"""Señales e imágenes sintéticas usadas en los ejercicios de clase."""

import torch


def chirp_espacial(
    size: int = 500,
    *,
    frecuencia_inicial: float = 1.0,
    frecuencia_final: float = 40.0,
    amplitud_inicial: float = 0.05,
    amplitud_final: float = 0.45,
    offset: float = 0.5,
    device: str | torch.device = "cpu",
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """Genera una imagen cuadrada cuya frecuencia horizontal aumenta hacia la derecha."""
    if size < 2:
        raise ValueError("size debe ser mayor o igual que 2")
    if frecuencia_inicial < 0 or frecuencia_final < 0:
        raise ValueError("las frecuencias deben ser mayores o iguales que cero")
    if amplitud_inicial < 0 or amplitud_final < 0:
        raise ValueError("las amplitudes deben ser mayores o iguales que cero")
    if not torch.empty((), dtype=dtype).is_floating_point():
        raise TypeError("dtype debe ser de punto flotante")

    t = torch.linspace(0, 1, size, device=device, dtype=dtype)
    fase_ciclos = frecuencia_inicial * t + 0.5 * (frecuencia_final - frecuencia_inicial) * t.square()
    fase = 2 * torch.pi * fase_ciclos
    amplitud = amplitud_inicial + (amplitud_final - amplitud_inicial) * t
    fila = (offset + amplitud * torch.sin(fase)).clamp(0, 1)
    return fila.repeat(size, 1).unsqueeze(0)
