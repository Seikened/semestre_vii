"""Ejercicio 2: ILPF y GLPF sobre TEXTO.BMP con la API fluida de VisionNode."""

from pathlib import Path

import matplotlib.pyplot as plt

from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import VisionNode


def _mostrar_fila(ejes, imagen: VisionNode, espectro, filtrado, nombre: str, corte: float) -> None:
    paneles = (
        (imagen, "Original"),
        (espectro.magnitud(), "TF centrada"),
        (filtrado.mascara_imagen(), f"H {nombre} · D0={corte:g}"),
        (filtrado.magnitud(), "TF2 = TF · H"),
        (filtrado.inversa(valor_absoluto=True), "IFFT(TF2)"),
    )
    for eje, (resultado, titulo) in zip(ejes, paneles, strict=True):
        eje.imshow(resultado.to_numpy(), cmap="gray", vmin=0, vmax=1)
        eje.set_title(titulo)
        eje.axis("off")


def main(ruta: Path = DATA_DIR / "TEXTO.BMP", corte_ideal: float = 30, corte_gaussiano: float = 10) -> None:
    imagen = VisionNode.desde_archivo(ruta).escala_grises()
    espectro = imagen.fft()
    ideal = espectro.pasabajas_ideal(corte_ideal)
    gaussiano = espectro.pasabajas_gaussiano(corte_gaussiano)

    figura, ejes = plt.subplots(2, 5, figsize=(17, 7), layout="constrained")
    _mostrar_fila(ejes[0], imagen, espectro, ideal, "ILPF", corte_ideal)
    _mostrar_fila(ejes[1], imagen, espectro, gaussiano, "GLPF", corte_gaussiano)
    figura.suptitle("Ejercicio 2 · TEXTO.BMP · Filtrado pasabajas en Fourier")
    plt.show()


if __name__ == "__main__":
    main()
