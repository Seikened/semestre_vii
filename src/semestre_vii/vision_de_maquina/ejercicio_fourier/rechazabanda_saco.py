"""Rechazabanda del profesor: suma de paso bajo y paso alto Butterworth."""

from semestre_vii.vision_de_maquina.ejercicio_fourier.saco import cargar_saco_cuadrado
from semestre_vii.vision_de_maquina.vision_node import Grafica


def main(
    corte_bajo: float = 60,
    corte_alto: float = 150,
    orden_bajo: int = 5,
    orden_alto: int = 5,
) -> None:
    imagen = cargar_saco_cuadrado()
    fourier = imagen.fft()
    ft2 = fourier.rechazabanda_butterworth(corte_bajo, corte_alto, orden_bajo, orden_alto)
    filtrada = ft2.inversa(valor_absoluto=True, clip=True)
    (
        Grafica(
            f"Rechazabanda Butterworth · {corte_bajo:g} a {corte_alto:g} · "
            f"n bajo={orden_bajo} · n alto={orden_alto}",
            columnas=3,
        )
        .espectro(ft2, "FT2 · rechazabanda Butterworth")
        .imagen(imagen, f"Original · cuadrado inferior {imagen.width}×{imagen.height}", rango="unidad")
        .imagen(filtrada, "Saco filtrado", rango="unidad")
        .mostrar()
    )


if __name__ == "__main__":
    main()
