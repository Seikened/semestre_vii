"""Primer paso de clase: pasabajas Butterworth sobre el cuadrado inferior del saco."""

from semestre_vii.vision_de_maquina.ejercicio_fourier.saco import cargar_saco_cuadrado
from semestre_vii.vision_de_maquina.vision_node import Grafica


def main(corte: float = 50, orden: int = 2) -> None:
    imagen = cargar_saco_cuadrado()
    lado = imagen.width
    fourier = imagen.fft()
    ft2 = fourier.pasabajas_butterworth(corte, orden=orden)
    filtrada = ft2.inversa(valor_absoluto=True, clip=True)
    (
        Grafica(f"Pasabajas Butterworth · saco LED · D0={corte:g} · n={orden}", columnas=3)
        .espectro(ft2, "FT2 · pasabajas Butterworth")
        .imagen(imagen, f"Original · cuadrado inferior {lado}×{lado}", rango="unidad")
        .imagen(filtrada, "Saco filtrado", rango="unidad")
        .mostrar()
    )


if __name__ == "__main__":
    main()
