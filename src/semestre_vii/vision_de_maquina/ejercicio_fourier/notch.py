"""Notch circular sobre las frecuencias de las rayas de Camisa.jpg."""

from pathlib import Path

from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import Grafica, VisionNode


def main(
    ruta: Path = DATA_DIR / "Camisa.jpg",
    radio_x: float = 30,
    radio_y: float = 20,
) -> None:
    imagen = VisionNode.desde_archivo(ruta).escala_grises()
    fourier = imagen.fft()
    notch_x = fourier.notch_ideal(centros=[(0, 74)], radio=radio_x)
    notch = notch_x.notch_ideal(centros=[(71, 0)], radio=radio_y)
    filtrada = notch.inversa()

    (
        Grafica(f"Notch ideal · {ruta.name} · Rx={radio_x:g} · Ry={radio_y:g}", columnas=3)
        .espectro(notch, "Fourier · notch simétrico")
        .imagen(imagen, "Camisa original", rango="unidad")
        .imagen(filtrada, "Camisa filtrada", rango="unidad")
        .mostrar()
    )


if __name__ == "__main__":
    main()
