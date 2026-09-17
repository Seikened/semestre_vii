"""Comparación directa entre GLPF y GHPF sobre el mismo chirp espacial."""

from semestre_vii.vision_de_maquina.vision_node import Grafica, VisionNode


def main(d0: float = 30, fila: int | None = None) -> None:
    imagen = VisionNode.chirp_espacial()
    espectro = imagen.fft()
    fila = imagen.alto // 2 if fila is None else fila

    filtro_pb = espectro.pasabajas_gaussiano(d0)
    filtro_pa = espectro.pasaaltas_gaussiano(d0)
    imagen_pb = filtro_pb.inversa()
    imagen_pa = filtro_pa.inversa()
    media_pa = imagen_pa.tensor.mean().item()

    (
        Grafica(f"Gauss · paso bajo vs paso alto · D0={d0:g}", columnas=3)
        .imagen(imagen, "IMG chirp")
        .senal(imagen, fila=fila, titulo=f"Original · fila {fila}")
        .espectro(espectro, "TF centrada")
        .mascara(filtro_pb, "H GLPF")
        .imagen(imagen_pb, "IMG_PB")
        .senales((imagen, "Original"), (imagen_pb, "Paso bajo"), fila=fila, titulo="Original vs paso bajo")
        .mascara(filtro_pa, "H GHPF")
        .imagen(imagen_pa, f"IMG_PA\nmedia≈{media_pa:.2e}", rango="simetrico")
        .senales(
            (imagen_pb, "Paso bajo"),
            (imagen_pa, "Paso alto"),
            fila=fila,
            titulo="Paso bajo vs paso alto",
            cero=True,
            ylabel="Valor",
        )
        .mostrar()
    )


if __name__ == "__main__":
    main()
