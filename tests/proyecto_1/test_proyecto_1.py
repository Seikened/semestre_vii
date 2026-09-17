"""Pruebas offline: negocio real e integraciones externas simuladas explícitamente."""

import json
from pathlib import Path
import sys
from types import SimpleNamespace

import cv2
import numpy as np
import pytest
import yaml

from semestre_vii.aprendizaje_automatico_iii.proyecto_1 import aplicacion, entrenamiento
from semestre_vii.aprendizaje_automatico_iii.proyecto_1 import preparacion, vision
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.cobro import Estabilidad, calcular_ticket
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.datos import cargar_dataset, leer_etiquetas
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.interfaz import dibujar, guardar_captura, revisar
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.vision import Instancia, Lectura

POLIGONO = "0 0.1 0.1 0.8 0.1 0.8 0.8 0.1 0.8\n"
CAJA = "0 0.5 0.5 0.6 0.6\n"


@pytest.fixture
def dataset(tmp_path):
    raiz = tmp_path / "raw"
    for numero, split in enumerate(("train", "valid", "test"), 1):
        (raiz / split / "images").mkdir(parents=True)
        (raiz / split / "labels").mkdir()
        imagen = np.full((48, 64, 3), numero * 40, dtype=np.uint8)
        cv2.imwrite(str(raiz / split / "images" / "pan.png"), imagen)
        (raiz / split / "labels" / "pan.txt").write_text(POLIGONO)
    contenido = {"train": "../train/images", "val": "../valid/images", "test": "../test/images"}
    contenido.update(names=["Concha"], nc=1)
    ruta = raiz / "data.yaml"
    ruta.write_text(yaml.safe_dump(contenido))
    return ruta


def test_cobro_por_instancia_y_no_por_clase():
    ticket = calcular_ticket(["Concha", "Concha", "Bolillo", "Dona"])
    assert ticket.piezas == 4
    assert ticket.total_centavos == 4400
    assert next(r for r in ticket.renglones if r.clase == "Concha").cantidad == 2


def test_catalogo_normaliza_acentos_y_caso():
    assert calcular_ticket(["  pingüino  ", "CONCHA"]).total_centavos == 3000


def test_clase_desconocida_no_se_regala():
    ticket = calcular_ticket(["Concha", "Pan nuevo"])
    assert ticket.total_centavos is None
    assert ticket.subtotal_conocido_centavos == 1200
    assert ticket.piezas == 2
    assert not ticket.completo


def test_fotogramas_no_acumulan_y_vacio_limpia():
    for _ in range(20):
        assert calcular_ticket(["Concha"]).total_centavos == 1200
    assert calcular_ticket([]).total_centavos == 0


@pytest.mark.parametrize("precios", [{"A": -1}, {"A": 1.5}, {"A": True}, {"A": 1, "a": 2}, {"": 5}])
def test_rechaza_catalogos_invalidos(precios):
    with pytest.raises(ValueError):
        calcular_ticket([], precios)


def test_estabilidad_no_oculta_un_cambio():
    estado = Estabilidad(2)
    pan = calcular_ticket(["Concha"])
    assert not estado.actualizar(pan)
    assert estado.actualizar(pan)
    assert not estado.actualizar(calcular_ticket([]))
    assert not estado.actualizar(calcular_ticket(["sin precio"]))


def test_etiquetas_distinguen_caja_y_poligono(tmp_path):
    ruta = tmp_path / "pan.txt"
    ruta.write_text(CAJA + POLIGONO)
    etiquetas = leer_etiquetas(ruta, 1)
    assert not etiquetas[0].segmentacion
    assert etiquetas[1].segmentacion


@pytest.mark.parametrize("texto", [
    "0 nan 0.1 0.2 0.3", "0 0.5 0.5 0 0.1", "2 .5 .5 .2 .2", "0.5 .5 .5 .2 .2",
    "0 .1 .1 .2 .2 .3 .3", "0 .1 .1 .2", "0 -1 .2 .3 .4", "texto",
    "0 .1 .1 .2 .1 .2", "0 .1 .1 .8 .1 .8 1.2", "0 .1 .1 .8 .8", "0 inf .5 .2 .2",
])
def test_etiquetas_invalidas_fallan(tmp_path, texto):
    ruta = tmp_path / "pan.txt"
    ruta.write_text(texto)
    with pytest.raises(ValueError):
        leer_etiquetas(ruta, 1)


def test_negativo_explicito_y_etiqueta_ausente(tmp_path):
    ruta = tmp_path / "negativo.txt"
    with pytest.raises(ValueError, match="Falta"):
        leer_etiquetas(ruta, 1)
    ruta.touch()
    assert leer_etiquetas(ruta, 1) == ()


def test_auditoria_y_normalizacion_no_modifican_raw(dataset, tmp_path):
    original = dataset.read_bytes()
    datos = cargar_dataset(dataset, verificar_fugas=True)
    assert datos.nombres == ("Concha",)
    assert datos.resumen()["splits"]["train"]["poligonos"] == 1
    datos.exigir_segmentacion()
    normalizado = datos.guardar_yaml(tmp_path / "config" / "data.yaml")
    assert Path(yaml.safe_load(normalizado.read_text())["train"]).is_absolute()
    assert dataset.read_bytes() == original


def test_detecta_fuga_entre_splits(dataset):
    raiz = dataset.parent
    (raiz / "valid/images/pan.png").write_bytes((raiz / "train/images/pan.png").read_bytes())
    with pytest.raises(ValueError, match="duplicada"):
        cargar_dataset(dataset, verificar_fugas=True)


def test_no_entrena_segmentacion_con_cajas(dataset):
    (dataset.parent / "train/labels/pan.txt").write_text(CAJA)
    with pytest.raises(ValueError, match="cajas"):
        cargar_dataset(dataset).exigir_segmentacion()


def test_rechaza_names_inconsistentes(dataset):
    contenido = yaml.safe_load(dataset.read_text())
    contenido["nc"] = 2
    dataset.write_text(yaml.safe_dump(contenido))
    with pytest.raises(ValueError, match="nc"):
        cargar_dataset(dataset)


def test_preparar_conserva_poligonos_y_no_sobrescribe(dataset, tmp_path):
    destino = tmp_path / "segmentado"
    ruta = preparacion.preparar(dataset, destino, False)
    nuevo = cargar_dataset(ruta)
    assert not nuevo.pseudoetiquetas
    assert len(nuevo.muestras) == 3
    with pytest.raises(FileExistsError):
        preparacion.preparar(dataset, destino, False)
    assert dataset.is_file()


def test_preparar_cajas_exige_sam(dataset, tmp_path):
    (dataset.parent / "train/labels/pan.txt").write_text(CAJA)
    with pytest.raises(ValueError, match="con-sam"):
        preparacion.preparar(dataset, tmp_path / "out", False)


def test_preparar_sam_simulado_preserva_clases_y_advierte(dataset, tmp_path, monkeypatch):
    (dataset.parent / "train/labels/pan.txt").write_text(CAJA + CAJA)
    llamadas = []

    class SAMSimulado:
        def __init__(self, pesos):
            pass

        def __call__(self, imagen, bboxes, **kwargs):
            llamadas.append(bboxes)
            class Mascaras:
                xyn = [np.array([[.1, .1], [.8, .1], [.8, .8]]) for _ in bboxes]
                def __len__(self):
                    return len(self.xyn)
            return [SimpleNamespace(masks=Mascaras())]

    monkeypatch.setitem(sys.modules, "ultralytics", SimpleNamespace(SAM=SAMSimulado))
    monkeypatch.setattr(preparacion, "dispositivo", lambda valor: "cpu")
    monkeypatch.setattr(preparacion, "directorio", lambda: tmp_path / "runtime")
    ruta = preparacion.preparar(dataset, tmp_path / "segmentado", True)
    datos = cargar_dataset(ruta)
    assert len(llamadas[0]) == 2
    assert datos.resumen()["splits"]["train"]["poligonos"] == 2
    assert datos.pseudoetiquetas
    with pytest.raises(ValueError, match="pseudoetiquetas"):
        datos.exigir_segmentacion()
    datos.exigir_segmentacion(True)


class TensorSimulado:
    def __init__(self, valores):
        self.valores = valores
    def int(self):
        return self
    def cpu(self):
        return self
    def tolist(self):
        return self.valores


class CajasSimuladas:
    cls = TensorSimulado([0, 0])
    conf = TensorSimulado([.9, .8])
    def __len__(self):
        return 2


class MascarasSimuladas:
    xy = [np.array([[1, 1], [9, 1], [5, 9]])] * 2
    def __len__(self):
        return 2


def test_adaptador_no_agrupa_instancias_iguales():
    resultado = SimpleNamespace(boxes=CajasSimuladas(), masks=MascarasSimuladas(), names={0: "Concha"}, speed={"inference": 5})
    lectura = vision.traducir(resultado)
    assert len(lectura.instancias) == 2
    assert calcular_ticket(i.clase for i in lectura.instancias).total_centavos == 2400
    resultado.masks = None
    with pytest.raises(ValueError, match="máscaras"):
        vision.traducir(resultado)


def test_adaptador_sin_detecciones():
    lectura = vision.traducir(SimpleNamespace(boxes=[], masks=None, speed={}))
    assert lectura.instancias == ()


def test_render_y_ticket_json(tmp_path):
    lectura = Lectura((Instancia("Concha", .9, ((5, 5), (35, 5), (20, 35))),), 8)
    ticket = calcular_ticket(["Concha"])
    imagen = np.zeros((64, 64, 3), dtype=np.uint8)
    salida = dibujar(imagen, lectura, ticket, True, 10)
    assert salida.shape == (580, 424, 3)
    assert not imagen.any()
    ruta = guardar_captura(salida, ticket, tmp_path)
    assert ruta.with_suffix(".jpg").is_file()
    assert json.loads(ruta.read_text())["ticket"]["total_centavos"] == 1200


def test_revision_exporta_muestras(dataset, tmp_path):
    salida = revisar(dataset, "val", tmp_path / "revision", 2)
    assert len(list(salida.glob("*.jpg"))) == 1


def test_app_foto_integrada_con_modelo_simulado(dataset, tmp_path, monkeypatch):
    lectura = Lectura((Instancia("Concha", .9, ((5, 5), (35, 5), (20, 35))),), 5)
    monkeypatch.setattr(aplicacion, "Segmentador", lambda *args: SimpleNamespace(predecir=lambda imagen: lectura))
    monkeypatch.setattr(aplicacion, "pesos_entrenados", lambda ruta: tmp_path / "best.pt")
    monkeypatch.setattr(aplicacion, "directorio", lambda: tmp_path / "runtime")
    aplicacion.ejecutar(str(dataset.parent / "test/images/pan.png"), None, "cpu", .5, 640, True)
    ruta = next((tmp_path / "runtime/capturas").glob("*.json"))
    assert json.loads(ruta.read_text())["ticket"]["total_centavos"] == 1200


def test_camara_libera_recursos_y_recalcula(dataset, tmp_path, monkeypatch):
    tickets = []
    class Camara:
        liberada = False
        def isOpened(self):
            return True
        def read(self):
            return True, np.zeros((32, 32, 3), dtype=np.uint8)
        def release(self):
            self.liberada = True
    camara = Camara()
    lecturas = iter([Lectura((Instancia("Concha", .9, ((1, 1), (8, 1), (8, 8))),), 5), Lectura((), 5)])
    teclas = iter([0, ord("q")])
    monkeypatch.setattr(aplicacion, "Segmentador", lambda *args: SimpleNamespace(predecir=lambda imagen: next(lecturas)))
    monkeypatch.setattr(aplicacion, "pesos_entrenados", lambda ruta: tmp_path / "best.pt")
    monkeypatch.setattr(aplicacion.cv2, "VideoCapture", lambda fuente: camara)
    monkeypatch.setattr(aplicacion.cv2, "imshow", lambda *args: None)
    monkeypatch.setattr(aplicacion.cv2, "waitKey", lambda *args: next(teclas))
    monkeypatch.setattr(aplicacion.cv2, "getWindowProperty", lambda *args: 1)
    monkeypatch.setattr(aplicacion.cv2, "destroyAllWindows", lambda: None)
    def render(imagen, lectura, ticket, *args):
        tickets.append(ticket)
        return imagen
    monkeypatch.setattr(aplicacion, "dibujar", render)
    aplicacion.ejecutar("0", None, "cpu", .5, 640)
    assert [t.total_centavos for t in tickets] == [1200, 0]
    assert camara.liberada


def test_orquestacion_entrenamiento_simulada(dataset, tmp_path, monkeypatch):
    llamadas = []
    class YOLOSimulado:
        def __init__(self, pesos):
            assert str(pesos).endswith("yolo26n-seg.pt")
        def train(self, **kwargs):
            llamadas.append(kwargs)
            carpeta = Path(kwargs["project"]) / kwargs["name"]
            (carpeta / "weights").mkdir(parents=True)
            (carpeta / "weights/best.pt").write_text("PESOS SIMULADOS - NO USAR")
            self.trainer = SimpleNamespace(save_dir=carpeta)
    monkeypatch.setitem(sys.modules, "ultralytics", SimpleNamespace(YOLO=YOLOSimulado))
    monkeypatch.setattr(entrenamiento, "directorio", lambda: tmp_path / "runtime")
    monkeypatch.setattr(entrenamiento, "dispositivo", lambda valor: "cpu")
    monkeypatch.setattr(entrenamiento, "version", lambda paquete: "simulada")
    ruta = entrenamiento.entrenar(dataset, entrenamiento.Entrenamiento(epochs=1))
    assert ruta.is_file()
    assert llamadas[0]["workers"] == 0
    assert llamadas[0]["device"] == "cpu"
    assert (tmp_path / "runtime/ultimo_modelo.txt").read_text() == str(ruta)
    reporte = json.loads((ruta.parent.parent / "experimento.json").read_text())
    assert reporte["solo_prueba"]


@pytest.mark.parametrize("kwargs", [{"batch": 0}, {"epochs": 0}, {"fraction": 2}, {"imgsz": 641}])
def test_configuracion_entrenamiento_invalida(kwargs):
    with pytest.raises(ValueError):
        entrenamiento.Entrenamiento(**kwargs)


def test_evaluacion_integrada_calcula_error_de_negocio(dataset, tmp_path, monkeypatch):
    llamadas = []
    def validar(**kwargs):
        llamadas.append(kwargs)
        return SimpleNamespace(box=SimpleNamespace(map=.4), seg=SimpleNamespace(map=.3))
    instancia = Instancia("Concha", .9, ((1, 1), (8, 1), (8, 8)))
    modelo = SimpleNamespace(names={0: "Concha"}, val=validar)
    fake = SimpleNamespace(modelo=modelo, device="cpu", predecir=lambda imagen: Lectura((instancia, instancia), 5))
    monkeypatch.setattr(entrenamiento, "Segmentador", lambda *args: fake)
    monkeypatch.setattr(entrenamiento, "pesos_entrenados", lambda ruta: tmp_path / "best.pt")
    monkeypatch.setattr(entrenamiento, "directorio", lambda: tmp_path / "runtime")
    salida = entrenamiento.evaluar(dataset, None, "test", "cpu", .5)
    reporte = json.loads(salida.read_text())
    assert reporte["canastas_exactas"] == 0
    assert reporte["mae_total_mxn"] == 12
    assert reporte["mae_conteo_por_clase"] == 1
    assert llamadas[0]["split"] == "test"


def test_preparacion_fallida_limpia_solo_staging(dataset, tmp_path, monkeypatch):
    (dataset.parent / "train/labels/pan.txt").write_text(CAJA)
    class SAMFallido:
        def __init__(self, pesos):
            pass
        def __call__(self, *args, **kwargs):
            return [SimpleNamespace(masks=None)]
    monkeypatch.setitem(sys.modules, "ultralytics", SimpleNamespace(SAM=SAMFallido))
    monkeypatch.setattr(preparacion, "dispositivo", lambda valor: "cpu")
    monkeypatch.setattr(preparacion, "directorio", lambda: tmp_path / "runtime")
    with pytest.raises(ValueError, match="SAM"):
        preparacion.preparar(dataset, tmp_path / "out", True)
    assert not (tmp_path / "out").exists()
    assert not list(tmp_path.glob("out.incompleto-*"))
    assert dataset.is_file()
