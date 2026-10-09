"""Notch ideal sobre el cuadrado inferior del saco iluminado con paneles LED."""

from semestre_vii.vision_de_maquina.ejercicio_fourier.saco import cargar_saco_cuadrado
from semestre_vii.vision_de_maquina.vision_node import Grafica


def main(
    radio_x: float = 30,
    radio_y: float = 20,
    radio_diagonal: float = 25,
) -> None:
    imagen = cargar_saco_cuadrado()
    lado = imagen.width
    fourier = imagen.fft()
    notch = (
        fourier
        .notch_ideal(centros=[(-1, 84), (-2, 157)], radio=radio_x)
        .notch_ideal(centros=[(84, 1), (106, 1)], radio=radio_y)
        .notch_ideal(centros=[(73, 85), (75, -79)], radio=radio_diagonal)
    )
    filtrada = notch.inversa()
    (
        Grafica(
            f"Notch ideal · saco LED · Rx={radio_x:g} · Ry={radio_y:g} · Rd={radio_diagonal:g}",
            columnas=3,
        )
        .espectro(notch, "Fourier y notch")
        .imagen(imagen, f"Original · cuadrado inferior {lado}×{lado}", rango="unidad")
        .imagen(filtrada, "Saco filtrado", rango="unidad")
        .mostrar()
    )


if __name__ == "__main__":
    main()
