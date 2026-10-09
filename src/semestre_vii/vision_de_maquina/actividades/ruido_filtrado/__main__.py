from pathlib import Path

import torch
from matplotlib.figure import Figure

from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import VisionNode

from . import graficas
from .experimento import ResultadoRuido, filtrar_ruido


def main(
    sigma: float = 10,
    corte: float = 50,
    umbral: float | None = None,
    fila: int = 100,
    seed: int = 7,
    archivo: str | Path = DATA_DIR / "golf.BMP",
    *,
    block: bool = True,
) -> tuple[Figure, Figure, Figure]:
    plana = VisionNode(torch.full((1, 256, 256), 127 / 255), titulo="Uniforme 127")
    uniforme = filtrar_ruido(plana, sigma=sigma, corte=corte, umbral=umbral, seed=seed)
    limpia = VisionNode.desde_archivo(archivo).escala_grises()
    real = filtrar_ruido(limpia, sigma=sigma, corte=corte, umbral=umbral, seed=seed)
    _reportar(uniforme)
    _reportar(real)
    _comparar_tomas(plana, sigma, seed)
    return (
        graficas.uniforme(uniforme, fila),
        graficas.imagen_real(real, corte),
        graficas.diagnostico(real, fila, block=block),
    )


def _reportar(resultado: ResultadoRuido) -> None:
    print(f"\n{resultado.limpia.titulo}, error respecto a la referencia limpia:")
    for nombre, imagen in (
        ("Con ruido", resultado.ruidosa),
        ("GLPF", resultado.filtrada),
        ("Con umbral", resultado.con_umbral),
    ):
        rmse = (imagen.tensor - resultado.limpia.tensor).square().mean().sqrt().item() * 255
        print(f"  {nombre}: RMSE = {rmse:.3f} tonos de gris")


def _comparar_tomas(plana: VisionNode, sigma: float, seed: int) -> None:
    tomas = [plana.ruido_gaussiano(sigma / 255, seed=seed + indice) for indice in range(9)]
    diferencia = tomas[0] - tomas[1]
    sigma_estimada = diferencia.tensor.std(correction=0).item() * 255 / (2 ** 0.5)
    promedio = tomas[0].promediar(tomas[1:])
    sigma_promedio = (promedio - plana).tensor.std(correction=0).item() * 255
    print(f"\nEscena uniforme fija, nueve tomas independientes: σ objetivo = {sigma:g}")
    print(f"  std(toma1 - toma2) / √2 = {sigma_estimada:.3f}")
    print(f"  σ residual del promedio de 9 = {sigma_promedio:.3f}, teórica ≈ {sigma / 3:.3f}")


if __name__ == "__main__":
    main()
