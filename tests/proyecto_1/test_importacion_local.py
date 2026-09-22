"""Importación y CLI reales, sin red, credenciales, YOLO ni SAM."""

import ast
import builtins
import getpass
import json
from pathlib import Path
import shutil
import socket
import stat
import sys
from zipfile import ZipFile, ZipInfo

import cv2
import numpy as np
import pytest
import yaml

from semestre_vii.aprendizaje_automatico_iii.proyecto_1 import __main__ as cli
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.entrenamiento import preparacion
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.utils import importacion
from semestre_vii.aprendizaje_automatico_iii.proyecto_1.entrenamiento.datos import (
    cargar_dataset,
    eliminar_fugas_entre_splits,
)

POLIGONO = "0 0.1 0.1 0.8 0.1 0.8 0.8 0.1 0.8\n"
CAJA = "0 0.5 0.5 0.6 0.6\n"


@pytest.fixture(autouse=True)
def sin_red_ni_credenciales(monkeypatch):
    def prohibido(*args, **kwargs):
        raise AssertionError("La importación local no puede usar red ni pedir credenciales.")
    monkeypatch.setattr(socket.socket, "connect", prohibido)
    monkeypatch.setattr(socket, "getaddrinfo", prohibido)
    monkeypatch.setattr(builtins, "input", prohibido)
    monkeypatch.setattr(getpass, "getpass", prohibido)


@pytest.fixture
def dataset_local(tmp_path):
    raiz = tmp_path / "exportacion"
    for indice, split in enumerate(("train", "valid", "test"), 1):
        (raiz / split / "images").mkdir(parents=True)
        (raiz / split / "labels").mkdir()
        imagen = np.full((12, 12, 3), indice * 40, dtype=np.uint8)
        assert cv2.imwrite(str(raiz / split / "images/pan.png"), imagen)
        (raiz / split / "labels/pan.txt").write_text(POLIGONO)
    config = {"train": "../train/images", "val": "../valid/images", "test": "../test/images"}
    config.update(names=["Concha"], nc=1)
    (raiz / "data.yaml").write_text(yaml.safe_dump(config))
    (raiz / "README.dataset.txt").write_text("Dataset de prueba local. Conservar atribución.")
    return raiz


def crear_zip(carpeta, ruta, prefijo=""):
    with ZipFile(ruta, "w") as archivo:
        for fuente in carpeta.rglob("*"):
            if fuente.is_file():
                archivo.write(fuente, str(Path(prefijo) / fuente.relative_to(carpeta)))
    return ruta


@pytest.mark.parametrize("tipo", ["carpeta", "yaml", "zip", "zip_anidado"])
def test_importa_datos_reales_sin_red(dataset_local, tmp_path, tipo):
    original = {p.relative_to(dataset_local): p.read_bytes() for p in dataset_local.rglob("*") if p.is_file()}
    origen = dataset_local / "data.yaml" if tipo == "yaml" else dataset_local
    if tipo.startswith("zip"):
        prefijo = "Mexican Bread/export" if tipo == "zip_anidado" else ""
        origen = crear_zip(dataset_local, tmp_path / "panes.zip", prefijo)
    salida = importacion.importar(origen, tmp_path / "dataset")
    datos = cargar_dataset(salida, verificar_fugas=True)
    assert len(datos.muestras) == 3
    assert datos.nombres == ("Concha",)
    assert (salida.parent / "val/labels/pan.txt").read_text() == POLIGONO
    assert (salida.parent / "README.dataset.txt").read_bytes() == original[Path("README.dataset.txt")]
    assert all((dataset_local / ruta).read_bytes() == contenido for ruta, contenido in original.items())
    assert not list(tmp_path.glob(".importacion-*"))
    shutil.rmtree(dataset_local)
    assert len(cargar_dataset(salida).muestras) == 3  # No depende del ZIP, temporal ni origen.


def test_limpia_fugas_entre_splits_sin_tocar_origen(dataset_local, tmp_path):
    valido = dataset_local / "valid"
    shutil.copy2(valido / "images/pan.png", valido / "images/unico.png")
    shutil.copy2(valido / "labels/pan.txt", valido / "labels/unico.txt")
    shutil.copy2(dataset_local / "train/images/pan.png", valido / "images/pan.png")

    salida = importacion.importar(dataset_local, tmp_path / "dataset")

    with pytest.raises(ValueError, match="Imagen duplicada entre train y val"):
        cargar_dataset(salida, verificar_fugas=True)

    eliminadas = eliminar_fugas_entre_splits(salida, raiz_permitida=salida.parent)

    assert eliminadas == {"val": 1}
    assert not (salida.parent / "val/images/pan.png").exists()
    assert not (salida.parent / "val/labels/pan.txt").exists()
    assert (salida.parent / "val/images/unico.png").is_file()
    assert (dataset_local / "valid/images/pan.png").is_file()
    assert len(cargar_dataset(salida, verificar_fugas=True).muestras) == 3


def test_conserva_cajas_y_negativos(dataset_local, tmp_path):
    (dataset_local / "train/labels/pan.txt").write_text(CAJA)
    shutil.copy2(dataset_local / "train/images/pan.png", dataset_local / "train/images/vacio.png")
    (dataset_local / "train/labels/vacio.txt").touch()
    salida = importacion.importar(dataset_local, tmp_path / "dataset")
    assert (salida.parent / "train/labels/pan.txt").read_text() == CAJA
    assert (salida.parent / "train/labels/vacio.txt").read_text() == ""
    with pytest.raises(ValueError, match="cajas"):
        cargar_dataset(salida).exigir_segmentacion()


def test_conserva_procedencia_de_mascaras(dataset_local, tmp_path):
    (dataset_local / "procedencia.json").write_text(json.dumps({"pseudoetiquetas": True}))
    salida = importacion.importar(dataset_local, tmp_path / "dataset")
    with pytest.raises(ValueError, match="pseudoetiquetas"):
        cargar_dataset(salida).exigir_segmentacion()


def test_no_sobrescribe_destino(dataset_local, tmp_path):
    destino = tmp_path / "dataset"
    destino.mkdir()
    (destino / "existente.txt").write_text("NO BORRAR")
    with pytest.raises(FileExistsError):
        importacion.importar(dataset_local, destino)
    assert (destino / "existente.txt").read_text() == "NO BORRAR"


def test_no_modifica_origen_con_destino_anidado(dataset_local):
    with pytest.raises(ValueError, match="fuera"):
        importacion.importar(dataset_local, dataset_local / "copia")
    assert not (dataset_local / "copia").exists()


def test_rechaza_etiquetas_ausentes_y_limpia(dataset_local, tmp_path):
    (dataset_local / "train/labels/pan.txt").unlink()
    destino = tmp_path / "dataset"
    with pytest.raises(ValueError, match="Falta"):
        importacion.importar(dataset_local, destino)
    assert not destino.exists()
    assert not list(tmp_path.glob(".importacion-*"))


@pytest.mark.parametrize("nombre", ["../fuera.txt", "/fuera.txt", "C:/fuera.txt", "..\\fuera.txt"])
def test_zip_no_escribe_fuera_del_temporal(tmp_path, nombre):
    ruta = tmp_path / "malicioso.zip"
    with ZipFile(ruta, "w") as archivo:
        archivo.writestr(nombre, "NO EXTRAER")
    with pytest.raises(ValueError, match="insegura"):
        importacion.importar(ruta, tmp_path / "dataset")
    assert not (tmp_path / "fuera.txt").exists()
    assert not (tmp_path / "dataset").exists()
    assert not list(tmp_path.glob(".importacion-*"))


def test_zip_rechaza_enlaces(tmp_path):
    ruta = tmp_path / "enlace.zip"
    info = ZipInfo("enlace")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with ZipFile(ruta, "w") as archivo:
        archivo.writestr(info, "/etc/passwd")
    with pytest.raises(ValueError, match="enlaces"):
        importacion.importar(ruta, tmp_path / "dataset")


def test_zip_rechaza_colision_de_nombres_macos(tmp_path):
    ruta = tmp_path / "duplicado.zip"
    with ZipFile(ruta, "w") as archivo:
        archivo.writestr("Train/a.txt", "uno")
        archivo.writestr("train/A.txt", "dos")
    with pytest.raises(ValueError, match="duplicada"):
        importacion.importar(ruta, tmp_path / "dataset")


def test_zip_corrupto_falla_sin_dejar_dataset(tmp_path):
    ruta = tmp_path / "dañado.zip"
    ruta.write_text("Esto no es un ZIP.")
    with pytest.raises(ValueError, match="ZIP válido"):
        importacion.importar(ruta, tmp_path / "dataset")
    assert not (tmp_path / "dataset").exists()


def test_zip_respeta_limite_de_tamano(dataset_local, tmp_path, monkeypatch):
    ruta = crear_zip(dataset_local, tmp_path / "pan.zip")
    monkeypatch.setattr(importacion, "MAX_BYTES", 1)
    with pytest.raises(ValueError, match="grande"):
        importacion.importar(ruta, tmp_path / "dataset")


def test_yaml_no_puede_apuntar_a_datos_externos(dataset_local, tmp_path):
    externo = tmp_path / "externo"
    shutil.copytree(dataset_local / "train", externo)
    archivo = dataset_local / "data.yaml"
    contenido = yaml.safe_load(archivo.read_text())
    contenido["train"] = str(externo / "images")
    archivo.write_text(yaml.safe_dump(contenido))
    with pytest.raises(ValueError, match="fuera del dataset"):
        importacion.importar(dataset_local, tmp_path / "dataset")
    assert (externo / "labels/pan.txt").read_text() == POLIGONO


def test_enlace_en_etiqueta_no_lee_fuera(dataset_local, tmp_path):
    externo = tmp_path / "etiqueta.txt"
    externo.write_text(POLIGONO)
    etiqueta = dataset_local / "train/labels/pan.txt"
    etiqueta.unlink()
    etiqueta.symlink_to(externo)
    with pytest.raises(ValueError, match="fuera del dataset"):
        importacion.importar(dataset_local, tmp_path / "dataset")


def test_fallback_exportacion_no_elige_carpeta_ajena(dataset_local, tmp_path):
    # ../train/images existe fuera, pero la exportación contiene train/images propio.
    externo = tmp_path / "train"
    shutil.copytree(dataset_local / "train", externo)
    (externo / "labels/pan.txt").write_text(CAJA)
    salida = importacion.importar(dataset_local, tmp_path / "dataset")
    assert (salida.parent / "train/labels/pan.txt").read_text() == POLIGONO


def test_multiples_yaml_no_se_eligen_al_azar(dataset_local, tmp_path):
    (dataset_local / "otra").mkdir()
    (dataset_local / "otra/data.yaml").write_text("names: []")
    with pytest.raises(ValueError, match="único"):
        importacion.importar(dataset_local, tmp_path / "dataset")
    salida = importacion.importar(dataset_local / "data.yaml", tmp_path / "dataset")
    assert salida.is_file()


def test_yaml_malformado_tiene_error_claro(dataset_local, tmp_path):
    (dataset_local / "data.yaml").write_text("train: [")
    with pytest.raises(ValueError, match="YAML válido"):
        importacion.importar(dataset_local, tmp_path / "dataset")


def test_preparacion_local_conserva_poligonos(dataset_local, tmp_path):
    salida = preparacion.preparar(dataset_local / "data.yaml", tmp_path / "segmentado", False)
    datos = cargar_dataset(salida)
    datos.exigir_segmentacion()
    assert len(datos.muestras) == 3


def test_cli_importa_e_inspecciona_dataset(dataset_local, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "directorio", lambda: tmp_path / "runtime")
    monkeypatch.setattr(sys, "argv", ["pan", "importar", str(dataset_local)])
    cli.main()
    assert "Dataset local importado" in capsys.readouterr().out
    monkeypatch.setattr(sys, "argv", ["pan", "inspeccionar", "--verificar-fugas"])
    cli.main()
    reporte = json.loads(capsys.readouterr().out)
    assert reporte["splits"]["train"]["poligonos"] == 1


def test_cli_sin_datos_falla_sin_pedir_clave(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "directorio", lambda: tmp_path)
    monkeypatch.setattr(sys, "argv", ["pan", "inspeccionar"])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2
    assert "importar /ruta/dataset.zip" in capsys.readouterr().err


def test_cli_elimina_descargar(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["pan", "descargar"])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2
    assert "invalid choice" in capsys.readouterr().err
    assert not hasattr(preparacion, "descargar")


def test_cli_cancelacion_limpia(dataset_local, tmp_path, monkeypatch, capsys):
    def cancelar(*args):
        raise KeyboardInterrupt
    monkeypatch.setattr(cli, "directorio", lambda: tmp_path / "runtime")
    monkeypatch.setattr(importacion, "importar", cancelar)
    monkeypatch.setattr(sys, "argv", ["pan", "importar", str(dataset_local)])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 130
    assert "cancelada" in capsys.readouterr().err


def test_cli_respeta_dataset_anterior_y_prefiere_nuevo(tmp_path, monkeypatch):
    anterior = tmp_path / "roboflow/data.yaml"
    anterior.parent.mkdir()
    anterior.touch()
    monkeypatch.setattr(cli, "directorio", lambda: tmp_path)
    assert cli.construir_parser().parse_args(["inspeccionar"]).data == anterior
    nuevo = tmp_path / "dataset/data.yaml"
    nuevo.parent.mkdir()
    nuevo.touch()
    assert cli.construir_parser().parse_args(["inspeccionar"]).data == nuevo


def test_no_hay_imports_de_sdk_ni_de_credenciales():
    for modulo in (cli, importacion, preparacion):
        arbol = ast.parse(Path(modulo.__file__).read_text())
        nombres = set()
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                nombres.update(n.name.split(".")[0] for n in nodo.names)
            elif isinstance(nodo, ast.ImportFrom):
                nombres.add((nodo.module or "").split(".")[0])
        assert nombres.isdisjoint({"roboflow", "getpass", "requests", "httpx"})
