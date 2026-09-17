"""Ejercicio 2: ILPF y GLPF sobre TEXTO.BMP usando el compositor Grafica."""

from pathlib import Path

from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import Grafica, VisionNode


def main(ruta: Path = DATA_DIR / "TEXTO.BMP", corte_ideal: float = 30, corte_gaussiano: float = 10) -> None:
    imagen = VisionNode.desde_archivo(ruta).escala_grises()
    espectro = imagen.fft()
    filtros = (
        (espectro.pasabajas_ideal(corte_ideal), "ILPF", corte_ideal),
        (espectro.pasabajas_gaussiano(corte_gaussiano), "GLPF", corte_gaussiano),
    )

    grafica = Grafica(
        "Ejercicio 2 · TEXTO.BMP · Filtrado pasabajas en Fourier",
        columnas=5,
        ancho_panel=3.4,
        alto_panel=3.2,
    )
    for filtrado, nombre, corte in filtros:
        grafica.imagen(imagen, "Original")
        grafica.espectro(espectro, "TF centrada")
        grafica.mascara(filtrado, f"H {nombre} · D0={corte:g}")
        grafica.espectro(filtrado, "TF2 = TF · H")
        grafica.imagen(filtrado.inversa(valor_absoluto=True), "IFFT(TF2)", rango="unidad")
    grafica.mostrar()


if __name__ == "__main__":
    main()
