"""Importa datasets YOLO desde disco. No usa red, SDKs ni credenciales."""

from pathlib import Path, PurePosixPath
import shutil
import stat
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile

import yaml

from .datos import cargar_dataset

MAX_ARCHIVOS = 100_000
MAX_BYTES = 20 * 1024**3


def localizar_yaml(origen: Path) -> Path:
    if origen.is_file() and origen.suffix.lower() in {".yaml", ".yml"}:
        return origen
    if not origen.is_dir():
        raise ValueError("Indica un ZIP, una carpeta YOLO o un archivo data.yaml local.")
    candidatos = sorted(p for p in origen.rglob("data.yaml") if "__MACOSX" not in p.parts)
    if len(candidatos) != 1:
        raise ValueError("La carpeta debe contener un único data.yaml; indica su ruta exacta.")
    return candidatos[0]


def extraer_zip(origen: Path, destino: Path) -> None:
    """Rechaza rutas externas, enlaces y ZIPs excesivos antes de extraer archivos."""
    try:
        with ZipFile(origen) as archivo:
            entradas = archivo.infolist()
            if len(entradas) > MAX_ARCHIVOS or sum(e.file_size for e in entradas) > MAX_BYTES:
                raise ValueError("ZIP demasiado grande. Usa una carpeta local ya extraída.")
            nombres = set()
            for entrada in entradas:
                ruta = PurePosixPath(entrada.filename)
                tipo = stat.S_IFMT(entrada.external_attr >> 16)
                if ruta.is_absolute() or ".." in ruta.parts or "\\" in entrada.filename or ":" in entrada.filename:
                    raise ValueError(f"Ruta insegura dentro del ZIP: {entrada.filename}")
                if not ruta.parts or tipo not in {0, stat.S_IFREG, stat.S_IFDIR}:
                    raise ValueError("El ZIP contiene enlaces o tipos de archivo no admitidos.")
                clave = str(ruta).casefold()
                if clave in nombres:
                    raise ValueError(f"Ruta duplicada dentro del ZIP: {entrada.filename}")
                nombres.add(clave)
            for entrada in entradas:
                ruta = PurePosixPath(entrada.filename)
                if "__MACOSX" in ruta.parts or entrada.is_dir():
                    continue
                salida = destino.joinpath(*ruta.parts)
                salida.parent.mkdir(parents=True, exist_ok=True)
                with archivo.open(entrada) as fuente, salida.open("xb") as copia:
                    shutil.copyfileobj(fuente, copia)
    except BadZipFile as exc:
        raise ValueError("El archivo no es un ZIP válido o está dañado.") from exc


def importar(origen: Path, destino: Path) -> Path:
    """Copia sólo imágenes, etiquetas y atribución; conserva intacto el origen."""
    origen = origen.expanduser().resolve()
    destino = destino.expanduser().absolute()
    if not origen.exists():
        raise FileNotFoundError(f"No existe el dataset local: {origen}")
    if destino.exists() or destino.is_symlink():
        raise FileExistsError(f"No se sobrescribe {destino}. Usa --data para leerlo o elige otro --destino.")
    destino = destino.resolve()
    es_zip = origen.is_file() and origen.suffix.lower() == ".zip"
    ruta = None if es_zip else localizar_yaml(origen)
    if ruta is not None and destino.is_relative_to(ruta.parent):
        raise ValueError("El destino debe estar fuera del dataset original.")
    destino.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".importacion-", dir=destino.parent) as temporal:
        trabajo = Path(temporal)
        if es_zip:
            entrada = trabajo / "entrada"
            entrada.mkdir()
            extraer_zip(origen, entrada)
            ruta = localizar_yaml(entrada)
        datos = cargar_dataset(ruta, raiz_permitida=ruta.parent)
        listo = trabajo / "listo"
        for muestra in datos.muestras:
            carpeta = datos.carpetas[muestra.split]
            relativa = muestra.imagen.relative_to(carpeta)
            imagen = listo / muestra.split / "images" / relativa
            etiqueta = listo / muestra.split / "labels" / relativa.with_suffix(".txt")
            imagen.parent.mkdir(parents=True, exist_ok=True)
            etiqueta.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(muestra.imagen, imagen)
            shutil.copy2(carpeta.parent / "labels" / relativa.with_suffix(".txt"), etiqueta)
        for patron in ("README*", "LICENSE*", "procedencia.json"):
            for archivo in ruta.parent.glob(patron):
                if archivo.is_file() and archivo.resolve().is_relative_to(ruta.parent.resolve()):
                    shutil.copy2(archivo, listo / archivo.name)
        contenido = {split: f"{split}/images" for split in datos.carpetas}
        contenido.update(names=list(datos.nombres), nc=len(datos.nombres))
        (listo / "data.yaml").write_text(yaml.safe_dump(contenido, allow_unicode=True), encoding="utf-8")
        cargar_dataset(listo / "data.yaml", raiz_permitida=listo)
        if destino.exists() or destino.is_symlink():
            raise FileExistsError(f"El destino apareció durante la importación: {destino}")
        listo.rename(destino)
    return destino / "data.yaml"
