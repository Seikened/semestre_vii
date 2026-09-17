import matplotlib.pyplot as plt

from semestre_vii.vision_de_maquina.vision_node import Grafica, VisionNode


def test_grafica_compone_paneles_de_imagen_senal_espectro_y_filtro() -> None:
    imagen = VisionNode.chirp_espacial(size=32, frecuencia_final=8)
    espectro = imagen.fft()
    filtrado = espectro.pasaaltas_gaussiano(4)

    grafica = (
        Grafica("Prueba", columnas=3)
        .imagen(imagen, "Imagen")
        .senal(imagen, fila=16, titulo="Señal")
        .espectro(espectro, "Espectro")
        .filtro(filtrado, "GHPF")
    )
    figura = grafica.mostrar(block=False)

    assert len(grafica) == 6
    assert len(figura.axes) == 6
    assert [eje.get_title() for eje in figura.axes[:3]] == ["Imagen", "Señal", "Espectro"]
    norma = figura.axes[5].images[0].norm
    assert norma.vmin < 0 < norma.vmax
    assert abs(norma.vmin) == norma.vmax
    plt.close(figura)


def test_grafica_superpone_senales_sin_tocar_los_nodos() -> None:
    imagen = VisionNode.chirp_espacial(size=32, frecuencia_final=8)
    pasabajas = imagen.pasabajas_gaussiano(4)
    original = imagen.tensor.clone()

    figura = (
        Grafica(columnas=1)
        .senales(
            (imagen, "Original"),
            (pasabajas, "Paso bajo"),
            fila=16,
            titulo="Comparación",
            cero=True,
        )
        .mostrar(block=False)
    )

    assert len(figura.axes[0].lines) == 3
    assert imagen.tensor.equal(original)
    plt.close(figura)
