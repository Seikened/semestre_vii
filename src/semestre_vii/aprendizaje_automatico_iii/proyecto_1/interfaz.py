"""Presentación OpenCV y revisión visual; sin reglas de precios duplicadas."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np

from .cobro import Ticket, calcular_ticket, normalizar
from .datos import cargar_dataset
from .vision import Instancia, Lectura


def dinero(centavos: int | None) -> str:
    if centavos is None:
        return "SIN PRECIO"
    return f"${centavos // 100:,}.{centavos % 100:02d}"


def dibujar(imagen, lectura: Lectura, ticket: Ticket, estable: bool, fps: float):
    alto, ancho = imagen.shape[:2]
    lienzo = np.zeros((max(alto, 580), ancho + 360, 3), dtype=np.uint8)
    original = imagen.copy()
    relleno = original.copy()
    for instancia in lectura.instancias:
        puntos = np.asarray(instancia.poligono, dtype=np.int32)
        semilla = sum(ord(c) for c in normalizar(instancia.clase))
        color = tuple(70 + (semilla * factor) % 160 for factor in (3, 7, 11))
        cv2.fillPoly(relleno, [puntos], color)
    original = cv2.addWeighted(original, 0.65, relleno, 0.35, 0)
    for instancia in lectura.instancias:
        puntos = np.asarray(instancia.poligono, dtype=np.int32)
        x = int(np.clip(puntos[:, 0].min(), 0, max(ancho - 140, 0)))
        y = int(np.clip(puntos[:, 1].min() - 8, 20, alto - 1))
        cv2.polylines(original, [puntos], True, (240, 240, 240), 1, cv2.LINE_AA)
        etiqueta = f"{normalizar(instancia.clase)} {instancia.confianza:.0%}"
        cv2.putText(original, etiqueta, (x, y), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 3)
        cv2.putText(original, etiqueta, (x, y), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1)
    lienzo[:alto, :ancho] = original

    def texto(valor, y, escala=.55, color=(235, 235, 235)):
        cv2.putText(lienzo, valor, (ancho + 18, y), cv2.FONT_HERSHEY_SIMPLEX, escala, color, 1, cv2.LINE_AA)

    texto("PANADERIA | CAJA ASISTIDA", 32, .6)
    texto("ESTIMACION - precios ficticios MXN", 57, .45)
    texto("CLASE         CANT.    SUBTOTAL", 91, .45)
    for indice, renglon in enumerate(ticket.renglones):
        y = 120 + indice * 28
        texto(f"{normalizar(renglon.clase)[:13]:13} {renglon.cantidad:>2}   {dinero(renglon.subtotal_centavos)}", y, .5)
    pie = lienzo.shape[0] - 115
    texto(f"PIEZAS: {ticket.piezas}", pie)
    total = dinero(ticket.total_centavos) if ticket.completo else "REVISAR PRECIOS"
    texto(f"TOTAL: {total}", pie + 31, .75)
    estado = "CONTEO ESTABLE" if estable else "VERIFICAR BANDEJA"
    texto(f"{estado} | {fps:.1f} FPS", pie + 58, .45)
    texto(f"Inferencia: {lectura.inferencia_ms:.1f} ms", pie + 77, .43)
    texto("Espacio: pausa | S: guardar | Q: salir", pie + 98, .42)
    return lienzo


def guardar_captura(imagen, ticket: Ticket, destino: Path, **contexto) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    identidad = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid4().hex[:6]}"
    ruta = destino / identidad
    if not cv2.imwrite(str(ruta.with_suffix(".jpg")), imagen):
        raise OSError("No se pudo guardar la captura.")
    documento = {"tipo": "estimacion_no_cobro", "moneda": "MXN", "precios": "ficticios",
                 "fecha": datetime.now(timezone.utc).isoformat(), "ticket": asdict(ticket), **contexto}
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
            instancias.append(Instancia(nombre, 1.0, puntos))
        ticket = calcular_ticket(i.clase for i in instancias)
        vista = dibujar(imagen, Lectura(tuple(instancias), 0), ticket, False, 0)
        tiene_cajas = any(not e.segmentacion for e in muestra.etiquetas)
        aviso = "ANOTACIONES: CAJAS (NO MASCARAS)" if tiene_cajas else "ANOTACIONES: POLIGONOS - REVISAR"
        cv2.putText(vista, aviso, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 255), 2)
        archivo = destino / f"{int(indice):05d}_{muestra.imagen.stem}.jpg"
        if not cv2.imwrite(str(archivo), vista):
            raise OSError(f"No se pudo guardar {archivo}")
    return destino
