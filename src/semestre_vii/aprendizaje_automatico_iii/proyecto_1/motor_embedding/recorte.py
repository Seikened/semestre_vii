"""Aísla un pan con su polígono: fondo gris, margen y cuadrado, como en el experimento 02."""

import cv2
import numpy as np

GRIS = 128
MARGEN = 0.06
LADO_MINIMO = 12


def a_gris(imagen_bgr: np.ndarray) -> np.ndarray:
    """Escala de grises en 3 canales: Mexican Bread v3 viene así y portero y encoder deben ver igual."""
    gris = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gris, cv2.COLOR_GRAY2BGR)


def recortar(imagen_bgr: np.ndarray, poligono) -> np.ndarray | None:
    """Recorte RGB cuadrado del pan sobre fondo gris. None si es demasiado pequeño para compararlo."""
    puntos = np.asarray(poligono, dtype=np.float32)
    alto, ancho = imagen_bgr.shape[:2]
    x1, y1 = puntos.min(axis=0)
    x2, y2 = puntos.max(axis=0)
    margen = MARGEN * max(x2 - x1, y2 - y1)
    izquierda, arriba = max(0, int(x1 - margen)), max(0, int(y1 - margen))
    derecha, abajo = min(ancho, int(np.ceil(x2 + margen))), min(alto, int(np.ceil(y2 + margen)))
    if min(derecha - izquierda, abajo - arriba) < LADO_MINIMO:
        return None

    mascara = np.zeros((abajo - arriba, derecha - izquierda), dtype=np.uint8)
    contorno = np.round(puntos - (izquierda, arriba)).astype(np.int32)
    cv2.fillPoly(mascara, [contorno], 255)
    ventana = imagen_bgr[arriba:abajo, izquierda:derecha]
    aislado = np.where(mascara[..., None] > 0, ventana, np.uint8(GRIS))

    lado = max(aislado.shape[:2])
    relleno_alto, relleno_ancho = lado - aislado.shape[0], lado - aislado.shape[1]
    cuadrado = cv2.copyMakeBorder(
        aislado,
        relleno_alto // 2, relleno_alto - relleno_alto // 2,
        relleno_ancho // 2, relleno_ancho - relleno_ancho // 2,
        cv2.BORDER_CONSTANT, value=(GRIS, GRIS, GRIS),
    )
    return cv2.cvtColor(cuadrado, cv2.COLOR_BGR2RGB)
