"""ResNet50 de ImageNet congelada: de recorte RGB a embedding de 2048 dimensiones."""

import numpy as np
import torch
from torch.nn import functional as F
from torchvision.models import ResNet50_Weights, resnet50

from ..configuracion import dispositivo
from ..esquemas.embedding import Embedding

NOMBRE = "resnet50-imagenet1k-v2-avgpool"
DIMENSION = 2048
LOTE = 32


class Encoder:
    """Sin reentrenar: los pesos de ImageNet sólo se usan para proyectar cada pan a un vector."""

    def __init__(self, device="auto"):
        pesos = ResNet50_Weights.IMAGENET1K_V2
        red = resnet50(weights=pesos)
        red.fc = torch.nn.Identity()
        elegido = dispositivo(device)
        if elegido.isdecimal():
            self.device = torch.device(f"cuda:{elegido}")
        else:
            self.device = torch.device(elegido)
        self.red = red.eval().requires_grad_(False).to(self.device)
        self.preparar = pesos.transforms()

    def vectorizar(self, recortes: list[np.ndarray]) -> list[Embedding]:
        embeddings = []
        for inicio in range(0, len(recortes), LOTE):
            tensores = [
                self.preparar(torch.from_numpy(recorte).permute(2, 0, 1))
                for recorte in recortes[inicio:inicio + LOTE]
            ]
            with torch.inference_mode():
                salida = self.red(torch.stack(tensores).to(self.device))
                unitarios = F.normalize(salida.float(), dim=1).cpu().numpy()
            embeddings.extend(Embedding(vector=vector) for vector in unitarios)
        return embeddings
