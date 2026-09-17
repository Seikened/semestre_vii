"""Aplicación High Boost: original + ganancia · paso alto."""

from semestre_vii.vision_de_maquina.vision_node import Grafica, VisionNode


def main(d0: float = 30, ganancia: float = 1.0, fila: int | None = None) -> None:
    if ganancia < 0:
        raise ValueError("ganancia debe ser mayor o igual que cero")

    # Fórmula de la imagen mostrada por el profesor:
    # IMG[i,j] = 127 + 30 cos[(2π/500)(2j/30)j]
    # VisionNode la normaliza internamente de 0..255 a 0..1.
    imagen = VisionNode.chirp_profesor()
    fila = imagen.alto // 2 if fila is None else fila

    # El desenfoque se modela como un paso bajo gaussiano.
    pasabajas = imagen.pasabajas_gaussiano(d0)

    # Unsharp mask / componente de alta frecuencia:
    # PA = IMG - PB
    pasaaltas = imagen - pasabajas

    # High Boost:
    # HB = IMG + k·PA = IMG + k(IMG - PB)
    high_boost = imagen + ganancia * pasaaltas

    media_pa = pasaaltas.tensor.mean().item()
    minimo_hb = high_boost.min()
    maximo_hb = high_boost.max()

    (
        Grafica(
            f"High Boost · D0={d0:g} · ganancia={ganancia:g}",
            columnas=3,
        )
        .imagen(imagen, "IMG original", rango="unidad")
        .senal(imagen, fila=fila, titulo=f"Original · fila {fila}")
        .espectro(imagen.fft(), "TF centrada")
        .imagen(pasabajas, "IMG_PB", rango="unidad")
        .imagen(
            pasaaltas,
            f"IMG_PA = IMG - IMG_PB\nmedia≈{media_pa:.2e}",
            rango="simetrico",
        )
        .imagen(
            high_boost,
            f"High Boost\nmin={minimo_hb:.3f}, max={maximo_hb:.3f}",
            rango="auto",
        )
        .senales(
            (imagen, "Original"),
            (pasabajas, "Paso bajo"),
            fila=fila,
            titulo="Original vs paso bajo",
        )
        .senales(
            (pasaaltas, "Paso alto"),
            fila=fila,
            titulo="Detalle de alta frecuencia",
            cero=True,
            ylabel="Detalle",
        )
        .senales(
            (imagen, "Original"),
            (high_boost, "High Boost"),
            fila=fila,
            titulo="Original vs High Boost",
        )
        .mostrar()
    )


if __name__ == "__main__":
    main()
