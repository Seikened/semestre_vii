"""Orquesta una lectura por imagen: fuente, modelo, vista y, si hay, mapa del embedding."""

from pathlib import Path
from time import perf_counter

import cv2

from ..configuracion import directorio
from ..entrenamiento.datos import EXTENSIONES
from ..motor_embedding.recorte import a_gris
from .interfaz import guardar_captura

VENTANA = "Panaderia"
VENTANA_MAPA = "Mapa del embedding"


def preprocesar(imagen, grayscale=False):
    if not grayscale:
        return imagen

    return a_gris(imagen)


def ejecutar(source, leer, presentacion, modelo, sin_ventana=False, grayscale=False, mapa=None):
    """`leer` convierte un fotograma BGR en Lectura: YOLO directo o el motor de embedding.

    `presentacion` (VistaCaja o VistaEmbedding) arma lo que se ve; `mapa` (MapaEmbedding)
    abre una segunda ventana con dónde cae cada pan en la galería.
    """
    source_text = str(source)
    archivo = Path(source).expanduser()
    es_camara = source_text.isdecimal()
    es_imagen = not es_camara and archivo.suffix.lower() in EXTENSIONES

    if not es_camara and not archivo.is_file():
        raise FileNotFoundError(f"No existe la imagen o el video: {archivo}")
    if sin_ventana and not es_imagen:
        raise ValueError("Sin ventana sólo se admite una foto; cámara y video requieren la interfaz.")

    destino = directorio() / "capturas"

    if es_imagen:
        imagen = cv2.imread(str(archivo))
        if imagen is None:
            raise ValueError(f"No se puede leer {archivo}")

        imagen = preprocesar(imagen, grayscale)
        lectura = leer(imagen)
        vista, contexto = presentacion.presentar(imagen, lectura, 0)
        vista_mapa = None if mapa is None else mapa.dibujar(lectura)

        print(guardar_captura(vista, destino, vista_mapa, modelo=modelo, fuente=str(archivo), **contexto))

        if not sin_ventana:
            try:
                cv2.imshow(VENTANA, vista)
                if vista_mapa is not None:
                    cv2.imshow(VENTANA_MAPA, vista_mapa)
                cv2.waitKey(0)
            finally:
                cv2.destroyAllWindows()
        return

    fuente = int(source_text) if es_camara else str(archivo)
    captura = cv2.VideoCapture(fuente)

    try:
        if not captura.isOpened():
            raise RuntimeError("No se pudo abrir la cámara/video. Revisa permisos y el índice de cámara.")

        pausado, vista, vista_mapa, cuadros = False, None, None, 0
        anterior, fps = perf_counter(), 0.0

        while True:
            if not pausado:
                ok, imagen = captura.read()
                if not ok:
                    if es_camara or cuadros == 0:
                        raise RuntimeError("La cámara/video no entregó un fotograma.")
                    break

                imagen = preprocesar(imagen, grayscale)
                lectura = leer(imagen)

                ahora = perf_counter()
                instantaneo = 1 / max(ahora - anterior, 1e-6)
                fps = instantaneo if cuadros == 0 else .85 * fps + .15 * instantaneo
                anterior = ahora

                vista, contexto = presentacion.presentar(imagen, lectura, fps)
                if mapa is not None:
                    vista_mapa = mapa.dibujar(lectura)
                cuadros += 1

            cv2.imshow(VENTANA, vista)
            if vista_mapa is not None:
                cv2.imshow(VENTANA_MAPA, vista_mapa)
            tecla = cv2.waitKey(20 if pausado else 1) & 0xFF

            if tecla in (ord("q"), 27):
                break
            if tecla == ord(" "):
                pausado = not pausado
                anterior = perf_counter()
            if tecla == ord("s"):
                print(guardar_captura(vista, destino, vista_mapa, modelo=modelo, cuadro=cuadros, **contexto))
            if cv2.getWindowProperty(VENTANA, cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        captura.release()
        cv2.destroyAllWindows()
