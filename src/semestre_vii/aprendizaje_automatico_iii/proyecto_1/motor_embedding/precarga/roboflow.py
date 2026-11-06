"""Descarga Mexican Bread v3 con la API de Roboflow; la clave llega como SecretStr desde Ajustes."""

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import httpx
from pydantic import SecretStr

from ...entrenamiento.datos import eliminar_fugas_entre_splits
from ...utils.importacion import importar

API = "https://api.roboflow.com"
WORKSPACE, PROYECTO, VERSION = "jpia", "mexican-bread", 3
FORMATO = "yolov8"  # Esta exportación conserva los polígonos; el Colab 02 lo auditó.

# httpx registra en INFO la URL completa, y la de Roboflow lleva la clave en la query.
logging.getLogger("httpx").setLevel(logging.WARNING)


def descargar_mexican_bread(destino: Path, clave: SecretStr | None) -> Path:
    """Devuelve el data.yaml local; sólo usa la red, y la clave, si el dataset no existe."""
    data_yaml = destino / "data.yaml"
    if not data_yaml.is_file():
        data_yaml = importar_desde_roboflow(destino, clave)
    # Idempotente: también cubre una corrida anterior que falló antes de limpiar.
    eliminadas = eliminar_fugas_entre_splits(data_yaml, raiz_permitida=destino)
    print(f"Dataset listo en {destino}. Duplicados retirados entre splits: {eliminadas or 'ninguno'}")
    return data_yaml


def importar_desde_roboflow(destino: Path, clave: SecretStr | None) -> Path:
    if clave is None:
        raise RuntimeError(
            "Falta ROBOFLOW_API_KEY. Copia proyecto_1/.env.example como proyecto_1/.env "
            "y pega tu clave."
        )
    enlace = enlace_exportacion(clave)
    destino.parent.mkdir(parents=True, exist_ok=True)
    print("Descargando Mexican Bread v3 desde Roboflow...")
    with NamedTemporaryFile(suffix=".zip", dir=destino.parent) as zip_temporal:
        try:
            with httpx.stream("GET", enlace, follow_redirects=True, timeout=120) as respuesta:
                if respuesta.status_code != 200:
                    raise RuntimeError(f"Roboflow no entregó el ZIP (HTTP {respuesta.status_code}).")
                for bloque in respuesta.iter_bytes():
                    zip_temporal.write(bloque)
        except (httpx.HTTPError, httpx.InvalidURL):
            # El mensaje de httpx incluye la URL firmada; no se muestra.
            raise RuntimeError("Falló la descarga del ZIP de Roboflow. Revisa tu conexión.") from None
        zip_temporal.flush()
        return importar(Path(zip_temporal.name), destino)


def enlace_exportacion(clave: SecretStr) -> str:
    url = f"{API}/{WORKSPACE}/{PROYECTO}/{VERSION}/{FORMATO}"
    try:
        respuesta = httpx.get(url, params={"api_key": clave.get_secret_value()}, timeout=60)
    except httpx.HTTPError:
        # La URL de la petición lleva la clave en la query; nunca se imprime.
        raise RuntimeError("No se pudo contactar a Roboflow. Revisa tu conexión.") from None
    if respuesta.status_code in (401, 403):
        raise RuntimeError("Roboflow rechazó ROBOFLOW_API_KEY.")
    if respuesta.status_code != 200:
        raise RuntimeError(f"Roboflow respondió HTTP {respuesta.status_code}.")
    exportacion = respuesta.json().get("export") or {}
    enlace = exportacion.get("link")
    if not enlace:
        raise RuntimeError("Roboflow aún no tiene lista la exportación; reintenta en un minuto.")
    return enlace
