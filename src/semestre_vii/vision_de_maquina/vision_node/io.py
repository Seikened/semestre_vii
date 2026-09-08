from pathlib import Path

import torch
from PIL import Image
from torchvision.transforms.v2 import functional


def cargar_imagen(
    ruta: str | Path,
    *,
    device: str | torch.device = "cpu",
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    with Image.open(ruta) as imagen:
        tensor = functional.to_image(imagen.convert("RGB"))

    tensor = functional.to_dtype(tensor, dtype=dtype, scale=True)
    return tensor.to(device=device)


def guardar_imagen(tensor: torch.Tensor, ruta: str | Path) -> None:
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    tensor_cpu = tensor.detach().clamp(min=0.0, max=1.0).cpu()
    with functional.to_pil_image(tensor_cpu) as imagen:
        imagen.save(ruta)
