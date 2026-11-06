"""Mapa 2D del embedding: dónde cae cada pan en vivo respecto a los clusters de la galería."""

import cv2
import numpy as np
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import make_pipeline

from ..esquemas.deteccion import Lectura
from ..esquemas.galeria import Galeria
from ..esquemas.reconocimiento import DESCONOCIDO
from .interfaz import color_clase, rotular

LADO = 520
LEYENDA = 180
MARGEN = 40
COMPONENTES_PCA = 50
FONDO = (24, 24, 24)
BLANCO = (255, 255, 255)


class MapaEmbedding:
    """Proyección de 2048-D a 2-D, orientativa: las líneas a los k vecinos sí son las del coseno real."""

    def __init__(self, galeria: Galeria):
        if len(galeria.manifiesto.clases) >= 3:
            # Sin PCA previa, LDA en 2048-D se sobreajusta y los panes nuevos caen fuera de su cluster.
            componentes = min(COMPONENTES_PCA, len(galeria.vectores) - 1)
            proyeccion = make_pipeline(
                PCA(n_components=componentes), LinearDiscriminantAnalysis(n_components=2),
            )
            self.proyeccion = proyeccion.fit(galeria.vectores, galeria.clases)
            self.metodo = "PCA+LDA"
        else:
            # LDA en 2-D exige al menos 3 clases.
            self.proyeccion = PCA(n_components=2).fit(galeria.vectores)
            self.metodo = "PCA"
        puntos = self.proyeccion.transform(galeria.vectores)
        self.minimo, self.maximo = np.percentile(puntos, (1, 99), axis=0)
        self.galeria_px, _ = self.a_pixeles(puntos)
        self.fondo = self.pintar_galeria(galeria)

    def dibujar(self, lectura: Lectura) -> np.ndarray:
        mapa = self.fondo.copy()
        for instancia in lectura.instancias:
            reconocimiento = instancia.reconocimiento
            if reconocimiento is None:
                continue
            pixeles, fuera = self.a_pixeles(self.proyeccion.transform(reconocimiento.consulta.vector[None]))
            x, y = (int(v) for v in pixeles[0])
            for vecino in reconocimiento.vecinos:
                destino = tuple(int(v) for v in self.galeria_px[vecino.indice])
                color = color_clase(vecino.clase)
                cv2.line(mapa, (x, y), destino, color, 1, cv2.LINE_AA)
                cv2.circle(mapa, destino, 5, color, 2, cv2.LINE_AA)
            cv2.circle(mapa, (x, y), 9, color_clase(instancia.clase), -1, cv2.LINE_AA)
            cv2.circle(mapa, (x, y), 9, BLANCO, 2, cv2.LINE_AA)

            etiqueta = f"{instancia.clase} cos {reconocimiento.similitud:.3f}"
            if fuera[0]:
                etiqueta += " (fuera del mapa)"  # Cae lejos de toda la galería; se dibuja en el borde.
            ancho = cv2.getTextSize(etiqueta, cv2.FONT_HERSHEY_SIMPLEX, .45, 1)[0][0]
            if x + 12 + ancho > LADO:
                texto_x = x - 12 - ancho  # A la izquierda del punto, para no salirse del mapa.
            else:
                texto_x = x + 12
            rotular(mapa, etiqueta, texto_x, max(y - 10, 18), escala=.45)
        return mapa

    def a_pixeles(self, puntos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Píxeles dentro del cuadro y, por punto, si cayó fuera del rango de la galería."""
        normalizados = (puntos - self.minimo) / (self.maximo - self.minimo)
        fuera = ((normalizados < 0) | (normalizados > 1)).any(axis=1)
        pixeles = MARGEN + np.clip(normalizados, 0, 1) * (LADO - 2 * MARGEN)
        return np.round(pixeles).astype(np.int32), fuera

    def pintar_galeria(self, galeria: Galeria) -> np.ndarray:
        fondo = np.full((LADO, LADO + LEYENDA, 3), FONDO, dtype=np.uint8)
        for (x, y), clase in zip(self.galeria_px, galeria.clases, strict=True):
            cv2.circle(fondo, (int(x), int(y)), 1, color_clase(str(clase)), -1)
        cv2.line(fondo, (LADO, 0), (LADO, LADO), (70, 70, 70), 1)

        renglones = [*galeria.manifiesto.instancias_por_clase.items(), (DESCONOCIDO, None)]
        for numero, (clase, cantidad) in enumerate(renglones):
            y = 56 + numero * 26
            cv2.rectangle(fondo, (LADO + 14, y - 11), (LADO + 26, y + 1), color_clase(clase), -1)
            if cantidad is None:
                texto = str(clase)
            else:
                texto = f"{clase} ({cantidad})"
            rotular(fondo, texto, LADO + 34, y, escala=.45)

        rotular(fondo, f"MAPA DEL EMBEDDING ({self.metodo} 2D, {len(galeria.clases)} panes)", 10, 22)
        rotular(fondo, "punto con borde: pan en vivo | lineas: sus k vecinos", 10, LADO - 12, escala=.42)
        return fondo
