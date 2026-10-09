from dataclasses import dataclass

from semestre_vii.vision_de_maquina.vision_node import EspectroNode, VisionNode


@dataclass(frozen=True, slots=True)
class ResultadoRuido:
    limpia: VisionNode
    ruidosa: VisionNode
    espectro: EspectroNode
    filtrada: VisionNode
    con_umbral: VisionNode
    umbral: float


def filtrar_ruido(
    limpia: VisionNode,
    *,
    sigma: float = 10,
    corte: float = 50,
    umbral: float | None = None,
    seed: int = 7,
) -> ResultadoRuido:
    """Sigma y umbral usan tonos de gris; corte usa bins de la FFT centrada."""
    umbral = sigma if umbral is None else umbral
    ruidosa = limpia.ruido_gaussiano(sigma=sigma / 255, seed=seed)
    espectro = ruidosa.fft().pasabajas_gaussiano(corte)
    filtrada = espectro.inversa(valor_absoluto=True, clip=True)
    con_umbral = ruidosa.filtro_umbral(filtrada, umbral=umbral / 255)
    return ResultadoRuido(limpia, ruidosa, espectro, filtrada, con_umbral, umbral)
