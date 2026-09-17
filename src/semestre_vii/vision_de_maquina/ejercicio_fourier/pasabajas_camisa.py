"""Filtros pasabajas sobre una camisa de rayas."""

from pathlib import Path

from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import Grafica, VisionNode


def main(ruta: Path = DATA_DIR / "camisa.jpg") -> None:
    imagen = VisionNode.desde_archivo(ruta).escala_grises()
    imagen.senal_por_canal(block=False)

    espectro = imagen.fft(centrado=False)
    espectro_centrado = imagen.fft()
    corte = min(imagen.alto, imagen.ancho) / 8

    ideal = espectro_centrado.pasabajas_ideal(corte).inversa()
    gaussiano = espectro_centrado.pasabajas_gaussiano(corte).inversa()
    butterworth = espectro_centrado.pasabajas_butterworth(corte).inversa()

    (
        Grafica(
            "Fourier · camisa · filtros pasabajas",
            columnas=3,
            ancho_panel=4.2,
            alto_panel=3.5,
        )
        .espectro(espectro, "|FIMG|", logaritmica=False)
        .espectro(espectro, "log(1 + |FIMG|)")
        .espectro(espectro_centrado, "Espectro centrado")
        .imagen(ideal, "Ideal")
        .imagen(gaussiano, "Gaussiano")
        .imagen(butterworth, "Butterworth")
        .mostrar()
    )


if __name__ == "__main__":
    main()
