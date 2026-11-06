"""Demo en vivo: YOLO detecta el pan y la galería de embeddings dice cuál es."""

from pathlib import Path
from time import perf_counter

from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion.interfaz import VistaEmbedding
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion.mapa import MapaEmbedding
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.aplicacion.runtime import ejecutar
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.configuracion import (
    GALERIA_PANES,
    AjustesDemo,
    AjustesPortero,
    Tamaño,
)
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.esquemas.galeria import (
    ARCHIVO_MANIFIESTO,
    Galeria,
)
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.modelo.yolo import ModeloYOLO
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.motor_embedding.encoder import Encoder
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.motor_embedding.inferencia.reconocedor import (
    Reconocedor,
)


class AjustesApp(AjustesDemo):
    """Parámetros de la demo. Sobrescriben configuracion.py; entorno, .env y CLI aún los ajustan."""

    dispositivo: str = "auto"
    fuente: str = "0"  # Índice de cámara, foto o video.
    galeria: Path = GALERIA_PANES  # Su manifiesto dicta si portero y encoder ven en gris.
    portero: AjustesPortero = AjustesPortero(  # Siempre YOLO26-seg Mexican Bread v3.
        tamano=Tamaño.l,  # En gris, l y x detectaron fotos distintas; ver el README.
        confianza=0.35,
        imgsz=640,
    )
    umbral: float | None = None  # None = sin rechazo. Con un número, abajo de él sale desconocido.


def main():
    try:
        demo(AjustesApp(_cli_parse_args=True))
    except (ValueError, OSError, RuntimeError) as error:
        # Frontera con la terminal: ajuste inválido, archivo faltante o cámara sin permiso.
        raise SystemExit(f"Error: {error}") from None


def demo(ajustes: AjustesDemo):
    pesos = ajustes.portero.pesos
    if not pesos.is_file():
        raise SystemExit(f"No se encontró el peso: {pesos}")
    if not (ajustes.galeria / ARCHIVO_MANIFIESTO).is_file():
        raise SystemExit(f"No hay galería en {ajustes.galeria}. Ejecuta primero precargar.py.")

    galeria = Galeria.cargar(ajustes.galeria)
    manifiesto = galeria.manifiesto
    if manifiesto.gris:
        dominio = "en gris (la vista sigue a color)"
    else:
        dominio = "a color"
    print(f"Portero: {pesos.parent.parent.name}")
    print(f"Galería: {manifiesto.total} panes, {len(manifiesto.clases)} clases, "
          f"exactitud k-NN en validación {manifiesto.exactitud_validacion:.1%} (sin umbral)")
    print(f"El motor ve el cuadro {dominio}, como se construyó la galería.")

    portero = ModeloYOLO(
        pesos, ajustes.dispositivo, ajustes.portero.confianza, ajustes.portero.imgsz,
        agnostico=True,
    )
    reconocedor = Reconocedor(portero, Encoder(ajustes.dispositivo), galeria, ajustes.umbral)
    if ajustes.umbral is None:
        print(f"Sin rechazo por umbral (el calibrado en la precarga es {manifiesto.umbral:.3f}).")
    else:
        print(f"Umbral de desconocido: {reconocedor.umbral:.3f}")
    inicio = perf_counter()
    reconocedor.precalentar()
    mapa = MapaEmbedding(galeria)
    print(f"Precalentado (YOLO, ResNet y mapa {mapa.metodo}) en {perf_counter() - inicio:.1f} s")

    ejecutar(ajustes.fuente, reconocedor.leer, VistaEmbedding(), str(pesos), mapa=mapa)


if __name__ == "__main__":
    main()
