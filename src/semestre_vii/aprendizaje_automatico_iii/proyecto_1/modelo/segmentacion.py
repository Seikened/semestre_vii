"""Frontera con Ultralytics: traduce sus tensores a instancias del proyecto."""

from dataclasses import dataclass

from ..aplicacion.cobro import catalogo, normalizar
from ..aplicacion.precios import PRECIOS
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


def traducir(resultado):
    cajas, mascaras = resultado.boxes, resultado.masks
    tiempo = float(resultado.speed.get("inference") or 0)
    if cajas is None or len(cajas) == 0:
        return Lectura((), tiempo)
    if mascaras is None or len(mascaras) != len(cajas):
        raise ValueError("Se esperaban máscaras de segmentación, no sólo cajas.")
    clases = cajas.cls.int().cpu().tolist()
    confianzas = cajas.conf.cpu().tolist()
    instancias = []
    for clase, confianza, poligono in zip(clases, confianzas, mascaras.xy, strict=True):
        if len(poligono) < 3:
            raise ValueError("El modelo devolvió una instancia sin un polígono válido.")
        puntos = tuple((float(x), float(y)) for x, y in poligono)
        instancias.append(Instancia(resultado.names[clase], float(confianza), puntos))
    return Lectura(tuple(instancias), tiempo)


class Segmentador:
    """Una sola carga de pesos por sesión; el cobro no depende de esta clase."""

    def __init__(self, pesos, device="auto", conf=0.5, imgsz=640):
        from ultralytics import YOLO

        if not pesos.is_file():
            raise FileNotFoundError(pesos)
        if not 0 < conf <= 1 or imgsz < 32 or imgsz % 32:
            raise ValueError("conf debe estar en (0,1] e imgsz debe ser múltiplo de 32.")
        self.modelo = YOLO(str(pesos))
        if self.modelo.task != "segment":
            raise ValueError("Usa best.pt entrenado con YOLO26-seg, no un modelo detect.")
        conocidos = catalogo(PRECIOS)
        desconocidos = [n for n in self.modelo.names.values() if normalizar(n) not in conocidos]
        if desconocidos:
            raise ValueError(f"Clases sin precio: {desconocidos}. Revisa pesos y precios.py; no uses COCO.")
        self.device, self.conf, self.imgsz = dispositivo(device), conf, imgsz

    def predecir(self, imagen):
        resultado = self.modelo.predict(
            imagen, device=self.device, conf=self.conf, imgsz=self.imgsz,
            retina_masks=True, max_det=100, verbose=False,
        )[0]
        return traducir(resultado)
