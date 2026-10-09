"""Recorte del saco compartido por los ejercicios de filtrado frecuencial."""

from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import VisionNode


def cargar_saco_cuadrado() -> VisionNode:
    """Carga el cuadrado inferior de la foto del saco LED."""
    original = VisionNode.desde_archivo(DATA_DIR / "saco_paneles_led_cortada.bmp").escala_grises()
    lado = min(original.height, original.width)
    fila = original.height - lado
    columna = (original.width - lado) // 2
    return VisionNode(
        original.tensor[:, fila:fila + lado, columna:columna + lado],
        titulo=f"Saco · cuadrado inferior {lado}×{lado}",
    )
