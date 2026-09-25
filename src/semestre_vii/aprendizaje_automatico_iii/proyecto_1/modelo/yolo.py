"""Frontera con Ultralytics: traduce sus tensores a instancias del proyecto."""

from dataclasses import dataclass

from ..configuracion import dispositivo


@dataclass(frozen=True)
class Instancia:
    clase: str
    confianza: float
    poligono: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class Lectura:
    instancias: tuple[Instancia, ...]
    inferencia_ms: float


def traducir(resultado, tarea):
    cajas, mascaras = resultado.boxes, resultado.masks
    tiempo = float(resultado.speed.get("inference") or 0)
    if cajas is None or len(cajas) == 0:
        return Lectura((), tiempo)
    if tarea == "segment":
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
    instancias = []
    for clase, confianza, poligono in zip(clases, confianzas, poligonos, strict=True):
        if len(poligono) < 3:
            raise ValueError("El modelo devolvió una instancia sin un polígono válido.")
        puntos = tuple((float(x), float(y)) for x, y in poligono)
        instancias.append(Instancia(resultado.names[clase], float(confianza), puntos))
    return Lectura(tuple(instancias), tiempo)


class ModeloYOLO:
    """Una sola carga de pesos por sesión; el cobro no depende de esta clase."""

    def __init__(self, pesos, device="auto", conf=0.5, imgsz=640):
        from ultralytics import YOLO

        if not pesos.is_file():
            raise FileNotFoundError(pesos)
        if not 0 < conf <= 1 or imgsz < 32 or imgsz % 32:
            raise ValueError("conf debe estar en (0,1] e imgsz debe ser múltiplo de 32.")
        self.modelo = YOLO(str(pesos))
        if self.modelo.task not in {"detect", "segment"}:
            raise ValueError("Se requiere un checkpoint de detección o segmentación.")
        self.device, self.conf, self.imgsz = dispositivo(device), conf, imgsz

    def predecir(self, imagen):
        resultado = self.modelo.predict(
            imagen, device=self.device, conf=self.conf, imgsz=self.imgsz,
            retina_masks=True, max_det=100, verbose=False,
        )[0]
        return traducir(resultado, self.modelo.task)
