"""Ejercicio Fourier pasabajas sobre un chirp espacial cuadrado."""

from semestre_vii.vision_de_maquina.vision_node import Grafica, VisionNode


def main(d0: float = 30, orden_butterworth: int = 1, fila: int | None = None) -> None:
    imagen = VisionNode.chirp_espacial()
    espectro = imagen.fft()
    fila = imagen.alto // 2 if fila is None else fila

    ideal = espectro.pasabajas_ideal(d0)
    gaussiano = espectro.pasabajas_gaussiano(d0)
    butterworth = espectro.pasabajas_butterworth(d0, orden=orden_butterworth)

    (
        Grafica(f"Fourier · filtros pasabajas sobre chirp · D0={d0:g}", columnas=3)
        .imagen(imagen, "IMG chirp")
        .senal(imagen, fila=fila, titulo=f"IMG[{fila}, j]")
        .espectro(espectro, "TF centrada")
        .filtro(ideal, "ILPF")
        .filtro(gaussiano, "GLPF")
        .filtro(butterworth, f"BLPF · n={orden_butterworth}")
        .mostrar()
    )


if __name__ == "__main__":
    main()
