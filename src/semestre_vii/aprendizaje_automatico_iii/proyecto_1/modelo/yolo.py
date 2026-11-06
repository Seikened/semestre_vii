"""Frontera con Ultralytics: traduce sus tensores a instancias del proyecto."""

from enum import StrEnum

from ..configuracion import dispositivo
from ..esquemas.deteccion import Instancia, Lectura


class Tarea(StrEnum):
    """Lo que entrega un checkpoint de Ultralytics en `modelo.task`."""

    DETECCION = "detect"
    SEGMENTACION = "segment"


def traducir(resultado, tarea: Tarea):
    cajas, mascaras = resultado.boxes, resultado.masks
    tiempo = float(resultado.speed.get("inference") or 0)
    if cajas is None or len(cajas) == 0:
        return Lectura(instancias=(), inferencia_ms=tiempo)
    if tarea is Tarea.SEGMENTACION:
        if mascaras is None or len(mascaras) != len(cajas):
            raise ValueError("Faltan máscaras en el resultado de segmentación.")
        poligonos = mascaras.xy
    else:
        poligonos = [
            ((x1, y1), (x2, y1), (x2, y2), (x1, y2))
            for x1, y1, x2, y2 in cajas.xyxy.cpu().tolist()
        ]
    clases = cajas.cls.int().cpu().tolist()
    confianzas = cajas.conf.cpu().tolist()
    instancias = tuple(
        Instancia(
            clase=resultado.names[clase],
            confianza=float(confianza),
            poligono=tuple((float(x), float(y)) for x, y in poligono),
        )
        for clase, confianza, poligono in zip(clases, confianzas, poligonos, strict=True)
        if len(poligono) >= 3  # Ultralytics entrega máscaras de 1 o 2 píxeles sin contorno.
    )
    return Lectura(instancias=instancias, inferencia_ms=tiempo)


class ModeloYOLO:
    """Una sola carga de pesos por sesión; el cobro no depende de esta clase.

    `agnostico=True` fusiona detecciones solapadas de clases distintas en un solo pan:
    así trabaja el portero, que sólo responde si hay pan y dónde.
    """

    def __init__(self, pesos, device="auto", conf=0.5, imgsz=640, agnostico=False):
        from ultralytics import YOLO

        if not pesos.is_file():
            raise FileNotFoundError(pesos)
        if not 0 < conf <= 1 or imgsz < 32 or imgsz % 32:
            raise ValueError("conf debe estar en (0,1] e imgsz debe ser múltiplo de 32.")
        self.modelo = YOLO(str(pesos))
        self.tarea = Tarea(self.modelo.task)  # ValueError si no es detección ni segmentación.
        self.device, self.conf, self.imgsz = dispositivo(device), conf, imgsz
        self.agnostico = agnostico

    def predecir(self, imagen):
        resultado = self.modelo.predict(
            imagen, device=self.device, conf=self.conf, imgsz=self.imgsz,
            retina_masks=True, max_det=100, agnostic_nms=self.agnostico, verbose=False,
        )[0]
        return traducir(resultado, self.tarea)
