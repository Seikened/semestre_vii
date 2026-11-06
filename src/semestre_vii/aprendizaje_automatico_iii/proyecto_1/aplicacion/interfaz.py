"""Presentación OpenCV: vista de caja, vista del embedding, capturas y revisión visual."""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np

from ..entrenamiento.datos import cargar_dataset
from ..esquemas.deteccion import Instancia, Lectura
from ..esquemas.pan import ClasePan
from ..esquemas.reconocimiento import DESCONOCIDO
from .cobro import Estabilidad, Ticket, calcular_ticket, normalizar
from .precios import PRODUCTOS

# BGR, distinguibles entre sí y sin rojo: el rojo queda reservado para "desconocido".
PALETA_PAN = {
    ClasePan.BOLILLO: (180, 119, 31),     # azul
    ClasePan.CONCHA: (14, 127, 255),      # naranja
    ClasePan.CUERNITO: (44, 160, 44),     # verde
    ClasePan.DONA: (189, 103, 148),       # morado
    ClasePan.MANTECADA: (75, 86, 140),    # café
    ClasePan.OREJA: (194, 119, 227),      # rosa
    ClasePan.PINGUINO: (34, 189, 188),    # olivo
    ClasePan.REBANADA: (207, 190, 23),    # cian
    ClasePan.REJA: (190, 190, 190),       # gris claro
    ClasePan.TELERA: (232, 199, 174),     # azul cielo
    ClasePan.TORTA: (213, 176, 197),      # lavanda
}
ROJO = (40, 40, 230)
ANCHO_PANEL = 470
MAX_PANES_PANEL = 3


def color_clase(clase: str) -> tuple[int, int, int]:
    """El mismo color para una clase en el cuadro de la cámara y en el mapa del embedding."""
    if clase == DESCONOCIDO:
        return ROJO
    if clase in PALETA_PAN:
        return PALETA_PAN[clase]
    # Clases de otros modelos (modo caja con Bread Detector): color estable por nombre.
    semilla = sum(ord(c) for c in normalizar(clase))
    return tuple(70 + (semilla * factor) % 160 for factor in (3, 7, 11))


def dinero(centavos: int | None) -> str:
    if centavos is None:
        return "SIN PRECIO"
    return f"${centavos // 100:,}.{centavos % 100:02d}"


def rotular(imagen, texto, x, y, color=(255, 255, 255), escala=.5):
    """Texto sobre un recuadro negro; en OpenCV 5 un contorno grueso sale más ancho y se duplica."""
    (ancho, alto), base = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, escala, 1)
    x, y = int(x), int(y)
    cv2.rectangle(imagen, (x - 3, y - alto - 4), (x + ancho + 3, y + base), (0, 0, 0), -1)
    cv2.putText(imagen, texto, (x, y), cv2.FONT_HERSHEY_SIMPLEX, escala, color, 1, cv2.LINE_AA)


def puntaje(instancia: Instancia) -> str:
    """Similitud coseno si la clase vino de la galería; confianza de YOLO si no."""
    if instancia.clase == DESCONOCIDO and instancia.similitud is None:
        return "(muy pequeño para comparar)"  # El reconocedor no pudo recortarlo.
    if instancia.similitud is None:
        return f"{instancia.confianza:.0%}"
    return f"cos {instancia.similitud:.3f}"


class VistaCaja:
    """Cuadro con ticket estimado; recuerda los cuadros anteriores para la estabilidad del conteo."""

    def __init__(self):
        self.estabilidad = Estabilidad()

    def presentar(self, imagen, lectura: Lectura, fps: float) -> tuple[np.ndarray, dict]:
        ticket = calcular_ticket(i.clase for i in lectura.instancias)
        estable = self.estabilidad.actualizar(ticket)
        vista = dibujar(imagen, lectura, ticket, estable, fps)
        contexto = {"tipo": "estimacion_no_cobro", "moneda": "MXN", "precios": "ficticios",
                    "ticket": asdict(ticket), "estable": estable}
        return vista, contexto


class VistaEmbedding:
    """Cuadro con, por pan, la clase votada y su similitud contra cada clase de la galería."""

    def presentar(self, imagen, lectura: Lectura, fps: float) -> tuple[np.ndarray, dict]:
        alto, ancho = imagen.shape[:2]
        lienzo = np.zeros((max(alto, 580), ancho + ANCHO_PANEL, 3), dtype=np.uint8)
        lienzo[:alto, :ancho] = superponer(imagen, lectura)
        x = ancho + 18
        rotular(lienzo, "EMBEDDING | ResNet50 + k-NN coseno", x, 32, escala=.6)
        rotular(lienzo, f"Panes detectados por YOLO: {len(lectura.instancias)}", x, 60, escala=.45)

        y = 98
        for numero, instancia in enumerate(lectura.instancias[:MAX_PANES_PANEL], 1):
            y = dibujar_reconocimiento(lienzo, numero, instancia, x, y)
        restantes = len(lectura.instancias) - MAX_PANES_PANEL
        if restantes > 0:
            rotular(lienzo, f"... y {restantes} panes más (ver el mapa)", x, y, escala=.45)

        pie = lienzo.shape[0] - 46
        rotular(lienzo, f"{fps:.1f} FPS | inferencia {lectura.inferencia_ms:.0f} ms", x, pie, escala=.45)
        rotular(lienzo, "Espacio: pausa | S: guardar | Q: salir", x, pie + 24, escala=.42)
        return lienzo, {"tipo": "reconocimiento_embedding", "panes": resumir(lectura)}


def dibujar_reconocimiento(lienzo, numero: int, instancia: Instancia, x: int, y: int) -> int:
    """Encabezado del pan y una barra por clase; devuelve la y donde sigue el panel."""
    reconocimiento = instancia.reconocimiento
    if reconocimiento is None:
        rotular(lienzo, f"Pan {numero}: muy pequeño para comparar", x, y, ROJO, escala=.5)
        return y + 34

    k = len(reconocimiento.vecinos)
    encabezado = f"Pan {numero}: {reconocimiento.etiqueta}  ({reconocimiento.votos}/{k} vecinos)"
    rotular(lienzo, encabezado, x, y, color_clase(instancia.clase), escala=.55)
    y += 24
    ordenadas = sorted(reconocimiento.por_clase.items(), key=lambda par: par[1], reverse=True)
    for clase, similitud in ordenadas:
        largo = int(max(similitud, 0) * 250)
        cv2.rectangle(lienzo, (x + 92, y - 12), (x + 92 + largo, y), color_clase(clase), -1)
        rotular(lienzo, str(clase), x, y, escala=.42)
        rotular(lienzo, f"{similitud:.3f}", x + 92 + largo + 8, y, escala=.42)
        y += 21
    return y + 16


def resumir(lectura: Lectura) -> list[dict]:
    """Lo que se guarda en el JSON de una captura del modo embedding."""
    panes = []
    for instancia in lectura.instancias:
        reconocimiento = instancia.reconocimiento
        if reconocimiento is None:
            panes.append({"clase": instancia.clase, "comparado": False})
            continue
        panes.append({
            "clase": reconocimiento.etiqueta,
            "votos": reconocimiento.votos,
            "por_clase": {str(c): s for c, s in reconocimiento.por_clase.items()},
            "vecinos": [v.model_dump(mode="json") for v in reconocimiento.vecinos],
        })
    return panes


def superponer(imagen, lectura: Lectura) -> np.ndarray:
    """Siluetas coloreadas por clase y su etiqueta, sobre una copia del cuadro."""
    alto, ancho = imagen.shape[:2]
    original = imagen.copy()
    relleno = original.copy()
    for instancia in lectura.instancias:
        puntos = np.asarray(instancia.poligono, dtype=np.int32)
        cv2.fillPoly(relleno, [puntos], color_clase(instancia.clase))
    original = cv2.addWeighted(original, 0.65, relleno, 0.35, 0)
    for instancia in lectura.instancias:
        puntos = np.asarray(instancia.poligono, dtype=np.int32)
        x = int(np.clip(puntos[:, 0].min(), 0, max(ancho - 140, 0)))
        y = int(np.clip(puntos[:, 1].min() - 8, 20, alto - 1))
        cv2.polylines(original, [puntos], True, (240, 240, 240), 1, cv2.LINE_AA)
        producto = PRODUCTOS.get(instancia.clase)
        nombre = producto.nombre if producto else instancia.clase
        etiqueta = f"{normalizar(nombre)} {puntaje(instancia)}"
        rotular(original, etiqueta, x, y)
    return original


def dibujar(imagen, lectura: Lectura, ticket: Ticket, estable: bool, fps: float):
    alto, ancho = imagen.shape[:2]
    alto_panel = max(alto, 580, 260 + 28 * len(ticket.renglones))
    lienzo = np.zeros((alto_panel, ancho + ANCHO_PANEL, 3), dtype=np.uint8)
    lienzo[:alto, :ancho] = superponer(imagen, lectura)

    def texto(valor, y, escala=.55, color=(235, 235, 235)):
        cv2.putText(lienzo, valor, (ancho + 18, y), cv2.FONT_HERSHEY_SIMPLEX, escala, color, 1, cv2.LINE_AA)

    texto("PANADERIA | CAJA ASISTIDA", 32, .6)
    texto("ESTIMACION - precios ficticios MXN", 57, .45)
    texto("CLASE                 CANT.   UNIT.   SUBTOTAL", 91, .45)
    for indice, renglon in enumerate(ticket.renglones):
        y = 120 + indice * 28
        subtotal = dinero(renglon.subtotal_centavos) if renglon.subtotal_centavos is not None else "-"
        texto(
            f"{normalizar(renglon.clase)[:19]:19} {renglon.cantidad:>2} "
            f"{dinero(renglon.precio_centavos):>10} {subtotal:>9}",
            y,
            .45,
        )
    pie = lienzo.shape[0] - 115
    texto(f"PIEZAS: {ticket.piezas}", pie)
    total = dinero(ticket.total_centavos) if ticket.completo else "REVISAR PRECIOS"
    texto(f"TOTAL: {total}", pie + 31, .75)
    estado = "CONTEO ESTABLE" if estable else "VERIFICAR BANDEJA"
    texto(f"{estado} | {fps:.1f} FPS", pie + 58, .45)
    texto(f"Inferencia: {lectura.inferencia_ms:.1f} ms", pie + 77, .43)
    texto("Espacio: pausa | S: guardar | Q: salir", pie + 98, .42)
    return lienzo


def guardar_captura(imagen, destino: Path, mapa=None, **contexto) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    identidad = f"{datetime.now(UTC):%Y%m%d_%H%M%S}_{uuid4().hex[:6]}"
    ruta = destino / identidad
    if not cv2.imwrite(str(ruta.with_suffix(".jpg")), imagen):
        raise OSError("No se pudo guardar la captura.")
    if mapa is not None and not cv2.imwrite(str(destino / f"{identidad}_mapa.jpg"), mapa):
        raise OSError("No se pudo guardar el mapa del embedding.")
    documento = {"fecha": datetime.now(UTC).isoformat(), **contexto}
    ruta.with_suffix(".json").write_text(json.dumps(documento, indent=2, ensure_ascii=False), encoding="utf-8")
    return ruta.with_suffix(".json")


def revisar(data: Path, split: str, destino: Path, limite: int = 20) -> Path:
    """Exporta muestras equiespaciadas, no sólo las primeras; NO certifica las etiquetas."""
    dataset = cargar_dataset(data)
    muestras = [m for m in dataset.muestras if m.split == split]
    if not muestras or limite < 0:
        raise ValueError("Split inexistente o límite inválido; usa 0 para exportar todo.")
    indices = range(len(muestras)) if limite == 0 else np.linspace(0, len(muestras)-1, min(limite, len(muestras)), dtype=int)
    destino.mkdir(parents=True, exist_ok=True)
    for indice in indices:
        muestra = muestras[indice]
        imagen = cv2.imread(str(muestra.imagen))
        if imagen is None:
            raise ValueError(f"No se puede leer {muestra.imagen}")
        alto, ancho = imagen.shape[:2]
        instancias = []
        for e in muestra.etiquetas:
            coords = e.coordenadas
            if e.segmentacion:
                puntos = tuple((x*ancho, y*alto) for x, y in zip(coords[::2], coords[1::2]))
            else:
                x, y, w, h = coords
                puntos = ((x-w/2, y-h/2), (x+w/2, y-h/2), (x+w/2, y+h/2), (x-w/2, y+h/2))
                puntos = tuple((px*ancho, py*alto) for px, py in puntos)
            nombre = dataset.nombres[e.clase]
            instancias.append(Instancia(clase=nombre, confianza=1.0, poligono=puntos))
        ticket = calcular_ticket(i.clase for i in instancias)
        lectura = Lectura(instancias=tuple(instancias), inferencia_ms=0)
        vista = dibujar(imagen, lectura, ticket, False, 0)
        tiene_cajas = any(not e.segmentacion for e in muestra.etiquetas)
        aviso = "ANOTACIONES: CAJAS (NO MASCARAS)" if tiene_cajas else "ANOTACIONES: POLIGONOS - REVISAR"
        cv2.putText(vista, aviso, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 255), 2)
        archivo = destino / f"{int(indice):05d}_{muestra.imagen.stem}.jpg"
        if not cv2.imwrite(str(archivo), vista):
            raise OSError(f"No se pudo guardar {archivo}")
    return destino
