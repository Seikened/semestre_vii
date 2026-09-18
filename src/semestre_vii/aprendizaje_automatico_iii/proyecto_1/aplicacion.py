"""Orquesta una lectura por imagen: fuente -> segmentación -> ticket -> interfaz."""

from pathlib import Path
from time import perf_counter

import cv2

from .cobro import Estabilidad, calcular_ticket
from .configuracion import directorio, pesos_entrenados
from .datos import EXTENSIONES
from .interfaz import dibujar, guardar_captura
from .vision import Segmentador


def ejecutar(source: str | Path, model: Path | None, device: str, conf: float, imgsz: int,
             sin_ventana: bool = False) -> None:
    source_text = str(source)
    archivo = Path(source).expanduser()
    es_camara = source_text.isdecimal()
    es_imagen = not es_camara and archivo.suffix.lower() in EXTENSIONES
    if not es_camara and not archivo.is_file():
        raise FileNotFoundError(f"No existe la imagen o el video: {archivo}")
    if sin_ventana and not es_imagen:
        raise ValueError("--sin-ventana admite una foto; cámara/video requieren interfaz interactiva.")
    pesos = pesos_entrenados(model)
    segmentador = Segmentador(pesos, device, conf, imgsz)
    destino = directorio() / "capturas"
    if es_imagen:
        imagen = cv2.imread(str(archivo))
        if imagen is None:
            raise ValueError(f"No se puede leer {archivo}")
        lectura = segmentador.predecir(imagen)
        ticket = calcular_ticket(i.clase for i in lectura.instancias)
        vista = dibujar(imagen, lectura, ticket, False, 0)
        print(guardar_captura(vista, ticket, destino, modelo=str(pesos), fuente=str(archivo)))
        if not sin_ventana:
            try:
                cv2.imshow("Panaderia - estimacion", vista)
                cv2.waitKey(0)
            finally:
                cv2.destroyAllWindows()
        return
    fuente = int(source_text) if es_camara else str(archivo)
    captura = cv2.VideoCapture(fuente)
    try:
        if not captura.isOpened():
            raise RuntimeError("No se pudo abrir la cámara/video. Revisa permisos y --source 0/1.")
        estabilidad = Estabilidad()
        pausado, vista, cuadros = False, None, 0
        anterior, fps = perf_counter(), 0.0
        while True:
            if not pausado:
                ok, imagen = captura.read()
                if not ok:
                    if es_camara or cuadros == 0:
                        raise RuntimeError("La cámara/video no entregó un fotograma.")
                    break
                lectura = segmentador.predecir(imagen)
                ticket = calcular_ticket(i.clase for i in lectura.instancias)
                estable = estabilidad.actualizar(ticket)
                ahora = perf_counter()
                instantaneo = 1 / max(ahora - anterior, 1e-6)
                fps = instantaneo if cuadros == 0 else .85 * fps + .15 * instantaneo
                anterior = ahora
                vista = dibujar(imagen, lectura, ticket, estable, fps)
                cuadros += 1
            cv2.imshow("Panaderia - estimacion", vista)
            tecla = cv2.waitKey(20 if pausado else 1) & 0xFF
            if tecla in (ord("q"), 27):
                break
            if tecla == ord(" "):
                pausado = not pausado
                anterior = perf_counter()
            if tecla == ord("s"):
                print(guardar_captura(vista, ticket, destino, modelo=str(pesos), cuadro=cuadros, estable=estable))
            if cv2.getWindowProperty("Panaderia - estimacion", cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        captura.release()
        cv2.destroyAllWindows()
