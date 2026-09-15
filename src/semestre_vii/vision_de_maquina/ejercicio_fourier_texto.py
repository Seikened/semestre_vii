"""Ejercicio 2: filtros pasabajas en frecuencia sobre TEXTO.BMP.

Replica el procedimiento de Mathcad del profesor:
1. TF = FFT2(imagen) y centrado del espectro.
2. Construcción de H con la distancia D al centro de frecuencia.
3. TF2 = TF * H.
4. Antitransformada para reconstruir la imagen filtrada.

Se muestran los dos filtros de la clase:
- ILPF con D0=30: H(u,v)=1 si D<D0, 0 en otro caso.
- GLPF con D0=10: H(u,v)=exp(-D^2/(2 D0^2)).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import torch

from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import VisionNode
from semestre_vii.vision_de_maquina.vision_node.signals.espectros import (
    magnitud_visual,
    mascara_pasabajas_gaussiano,
    mascara_pasabajas_ideal,
    transformada_2d,
)


def _filtrar(espectro: torch.Tensor, mascara: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    espectro_filtrado = espectro * mascara
    reconstruida = torch.fft.ifft2(torch.fft.ifftshift(espectro_filtrado, dim=(-2, -1))).real
    return espectro_filtrado, reconstruida.clamp(0, 1)


def _mostrar_fila(ejes, imagen, espectro, mascara, espectro_filtrado, reconstruida, nombre: str, corte: float) -> None:
    paneles = (
        (imagen, "Original"),
        (magnitud_visual(espectro), "TF centrada"),
        (mascara, f"H {nombre} · D0={corte:g}"),
        (magnitud_visual(espectro_filtrado), "TF2 = TF · H"),
        (reconstruida, "IFFT(TF2)"),
    )
    for eje, (resultado, titulo) in zip(ejes, paneles, strict=True):
        eje.imshow(resultado.detach().cpu().clamp(0, 1), cmap="gray", vmin=0, vmax=1)
        eje.set_title(titulo)
        eje.axis("off")


def main(ruta: Path = DATA_DIR / "TEXTO.BMP", corte_ideal: float = 30, corte_gaussiano: float = 10) -> None:
    imagen = VisionNode.desde_archivo(ruta).escala_grises().tensor[0]
    espectro = torch.fft.fftshift(transformada_2d(imagen), dim=(-2, -1))

    h_ideal = mascara_pasabajas_ideal(imagen, corte_ideal)
    h_gaussiano = mascara_pasabajas_gaussiano(imagen, corte_gaussiano)
    tf_ideal, imagen_ideal = _filtrar(espectro, h_ideal)
    tf_gaussiano, imagen_gaussiana = _filtrar(espectro, h_gaussiano)

    figura, ejes = plt.subplots(2, 5, figsize=(17, 7), layout="constrained")
    _mostrar_fila(ejes[0], imagen, espectro, h_ideal, tf_ideal, imagen_ideal, "ILPF", corte_ideal)
    _mostrar_fila(ejes[1], imagen, espectro, h_gaussiano, tf_gaussiano, imagen_gaussiana, "GLPF", corte_gaussiano)
    figura.suptitle("Ejercicio 2 · TEXTO.BMP · Filtrado pasabajas en el dominio de Fourier")
    plt.show()


if __name__ == "__main__":
    main()
