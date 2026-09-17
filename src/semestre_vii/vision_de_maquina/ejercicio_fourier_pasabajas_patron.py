"""Ejercicio Fourier pasabajas: comparar ILPF, GLPF y BLPF sobre un patrón cuadrado."""

import matplotlib.pyplot as plt
import torch

from semestre_vii.vision_de_maquina.vision_node import VisionNode


def crear_patron(size: int = 500, ancho_barra: int = 25) -> VisionNode:
    """Patrón periódico cuadrado para que ambos ejes tengan la misma resolución frecuencial."""
    columnas = torch.arange(size)
    altas = ((columnas // ancho_barra) % 2 == 0).to(torch.float32)
    fila = altas * 0.8 + 0.2
    tensor = fila.repeat(size, 1).unsqueeze(0)
    return VisionNode(tensor, titulo="IMGC")


def _mostrar_resultado(ejes, filtrado, nombre: str) -> None:
    mascara = filtrado.mascara_imagen()
    espectro_filtrado = filtrado.magnitud()
    reconstruida = filtrado.inversa()

    ejes[0].imshow(mascara.to_numpy(), cmap="gray", vmin=0, vmax=1)
    ejes[0].set_title(f"H {nombre}")
    ejes[1].imshow(espectro_filtrado.to_numpy(), cmap="gray", vmin=0, vmax=1)
    ejes[1].set_title("TF · H")
    ejes[2].imshow(reconstruida.to_numpy(), cmap="gray", vmin=0, vmax=1)
    ejes[2].set_title(f"IMG {nombre}")
    for eje in ejes:
        eje.axis("off")


def main(d0: float = 30, orden_butterworth: int = 1, fila: int | None = None) -> None:
    imagen = crear_patron()
    espectro = imagen.fft()
    fila = imagen.alto // 2 if fila is None else fila

    ideal = espectro.pasabajas_ideal(d0)
    gaussiano = espectro.pasabajas_gaussiano(d0)
    butterworth = espectro.pasabajas_butterworth(d0, orden=orden_butterworth)

    figura = plt.figure(figsize=(14, 13), layout="constrained")
    rejilla = figura.add_gridspec(4, 3)

    eje_imagen = figura.add_subplot(rejilla[0, 0])
    eje_senal = figura.add_subplot(rejilla[0, 1])
    eje_tf = figura.add_subplot(rejilla[0, 2])

    datos = imagen.to_numpy()
    eje_imagen.imshow(datos, cmap="gray", vmin=0, vmax=1)
    eje_imagen.set_title("IMGC")
    eje_imagen.axis("off")

    eje_senal.plot(datos[fila])
    eje_senal.set_title(f"IMGC[{fila}, j]")
    eje_senal.set_xlabel("j")
    eje_senal.set_ylabel("Intensidad")
    eje_senal.grid(alpha=0.25)

    eje_tf.imshow(espectro.magnitud().to_numpy(), cmap="gray", vmin=0, vmax=1)
    eje_tf.set_title("TF centrada")
    eje_tf.axis("off")

    _mostrar_resultado([figura.add_subplot(rejilla[1, i]) for i in range(3)], ideal, "ILPF")
    _mostrar_resultado([figura.add_subplot(rejilla[2, i]) for i in range(3)], gaussiano, "GLPF")
    _mostrar_resultado(
        [figura.add_subplot(rejilla[3, i]) for i in range(3)],
        butterworth,
        f"BLPF · n={orden_butterworth}",
    )

    figura.suptitle(f"Fourier · filtros pasabajas · D0={d0:g}")
    plt.show()


if __name__ == "__main__":
    main()
