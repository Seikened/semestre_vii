"""Transformada de Fourier de una camisa de rayas.

Mathcad: FIMG = cfft(IMG), MF = |FIMG| y MF2 = 255(MF - min)/(max - min).
Usamos FFT 1D en un renglón y FFT 2D en la imagen; para verla: log(1 + |F|) y min-max.
El centrado usa (-1)^(x+y). Si IMG es real, F(-w) = conj(F(w)); al rotarla, F gira igual.
"""

from pathlib import Path

import matplotlib.pyplot as plt

from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import VisionNode
from semestre_vii.vision_de_maquina.vision_node.signals.espectros import (
    magnitud_visual,
    transformada_2d,
)


def main(ruta: Path = DATA_DIR / "camisa.jpg") -> None:
    imagen = VisionNode.desde_archivo(ruta).escala_grises()
    imagen.senal_por_canal(block=False)
    matriz = imagen.tensor[0]
    alto, ancho = matriz.shape
    fimg = transformada_2d(matriz)
    fimg_centrada = transformada_2d(matriz, centrada=True)
    corte = min(alto, ancho) / 8
    filtradas = (
        imagen.pasabajas_ideal(corte).tensor[0],
        imagen.pasabajas_gaussiano(corte).tensor[0],
        imagen.pasabajas_butterworth(corte).tensor[0],
    )
    paneles = (
        (magnitud_visual(fimg, logaritmica=False), "|FIMG|"),
        (magnitud_visual(fimg), "log(1 + |FIMG|)"),
        (magnitud_visual(fimg_centrada), "Espectro centrado"),
        *zip(filtradas, ("Ideal", "Gaussiano", "Butterworth"), strict=True),
    )
    _, ejes = plt.subplots(2, 3, figsize=(12, 7), layout="constrained")
    for eje, (resultado, titulo) in zip(ejes.flat, paneles, strict=True):
        eje.imshow(resultado.clamp(0, 1), cmap="gray")
        eje.set_title(titulo)
        eje.axis("off")
    plt.show()


if __name__ == "__main__":
    main()
