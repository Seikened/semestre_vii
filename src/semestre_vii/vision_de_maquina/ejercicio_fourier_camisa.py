"""Transformada de Fourier de una camisa de rayas usando la API fluida."""

from pathlib import Path

import matplotlib.pyplot as plt

from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import VisionNode


def main(ruta: Path = DATA_DIR / "camisa.jpg") -> None:
    imagen = VisionNode.desde_archivo(ruta).escala_grises()
    imagen.senal_por_canal(block=False)

    espectro = imagen.fft(centrado=False)
    espectro_centrado = imagen.fft()
    corte = min(imagen.alto, imagen.ancho) / 8
    filtradas = (
        espectro_centrado.pasabajas_ideal(corte).inversa(),
        espectro_centrado.pasabajas_gaussiano(corte).inversa(),
        espectro_centrado.pasabajas_butterworth(corte).inversa(),
    )
    paneles = (
        (espectro.magnitud(logaritmica=False), "|FIMG|"),
        (espectro.magnitud(), "log(1 + |FIMG|)"),
        (espectro_centrado.magnitud(), "Espectro centrado"),
        *zip(filtradas, ("Ideal", "Gaussiano", "Butterworth"), strict=True),
    )

    _, ejes = plt.subplots(2, 3, figsize=(12, 7), layout="constrained")
    for eje, (resultado, titulo) in zip(ejes.flat, paneles, strict=True):
        eje.imshow(resultado.to_numpy(), cmap="gray", vmin=0, vmax=1)
        eje.set_title(titulo)
        eje.axis("off")
    plt.show()


if __name__ == "__main__":
    main()
