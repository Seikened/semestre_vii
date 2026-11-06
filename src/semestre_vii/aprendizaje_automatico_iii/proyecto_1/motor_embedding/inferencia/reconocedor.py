"""Por fotograma: portero YOLO → recorte → encoder → galería."""

from time import perf_counter

import numpy as np

from ...esquemas.deteccion import Lectura
from ...esquemas.galeria import Galeria
from ...esquemas.reconocimiento import DESCONOCIDO
from ...modelo.yolo import ModeloYOLO, Tarea
from ..encoder import NOMBRE, Encoder
from ..recorte import GRIS, a_gris, recortar
from ..vecinos import reconocer


class Reconocedor:
    """YOLO sólo decide si hay pan y dónde; la clase la pone la galería de embeddings."""

    def __init__(
        self, portero: ModeloYOLO, encoder: Encoder, galeria: Galeria, umbral: float | None = None,
    ):
        if portero.tarea is not Tarea.SEGMENTACION:
            raise ValueError("El portero debe segmentar: la galería se construyó con siluetas.")
        if galeria.manifiesto.encoder != NOMBRE:
            raise ValueError(
                f"La galería se construyó con {galeria.manifiesto.encoder}, no con {NOMBRE}. "
                "Vuelve a precargarla."
            )
        self.portero, self.encoder, self.galeria = portero, encoder, galeria
        if umbral is None:
            self.umbral = -1.0  # Sin rechazo: el portero ya decidió que hay pan; gana la más votada.
        else:
            self.umbral = umbral  # Rechazo opcional; el calibrado de la precarga está en el manifiesto.
        self.gris = galeria.manifiesto.gris  # El dominio lo dicta la galería, no un ajuste aparte.

    def precalentar(self) -> float:
        """Una pasada en vacío para que el primer cuadro en vivo no sea lento. Devuelve ms."""
        inicio = perf_counter()
        # 16:9 como las webcams: tras el letterbox, la misma forma que los cuadros reales.
        self.portero.predecir(np.zeros((720, 1280, 3), dtype=np.uint8))
        self.encoder.vectorizar([np.full((224, 224, 3), GRIS, dtype=np.uint8)])
        return (perf_counter() - inicio) * 1000

    def leer(self, imagen) -> Lectura:
        inicio = perf_counter()
        if self.gris:
            entrada = a_gris(imagen)  # Como la galería: el usuario ve color, el motor ve gris.
        else:
            entrada = imagen  # Sólo para comparar contra una galería a color.
        deteccion = self.portero.predecir(entrada)
        recortes = [recortar(entrada, instancia.poligono) for instancia in deteccion.instancias]
        validos = [indice for indice, recorte in enumerate(recortes) if recorte is not None]
        vectorizados = self.encoder.vectorizar([recortes[indice] for indice in validos])
        embeddings = dict(zip(validos, vectorizados, strict=True))

        instancias = []
        for indice, instancia in enumerate(deteccion.instancias):
            embedding = embeddings.get(indice)
            if embedding is None:
                # Demasiado pequeño para compararlo: se cuenta, pero invalida el total.
                instancias.append(instancia.model_copy(update={"clase": DESCONOCIDO}))
                continue
            reconocimiento = reconocer(self.galeria, embedding, self.umbral)
            cambios = {"clase": reconocimiento.etiqueta, "reconocimiento": reconocimiento}
            instancias.append(instancia.model_copy(update=cambios))

        transcurrido = (perf_counter() - inicio) * 1000
        return Lectura(instancias=tuple(instancias), inferencia_ms=transcurrido)
