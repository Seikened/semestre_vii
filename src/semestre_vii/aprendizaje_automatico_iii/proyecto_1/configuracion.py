"""Rutas del proyecto, ajustes de la demo y la precarga, y selección explícita del dispositivo."""

from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import MODEL_PATH, PROJECT_DATA_DIR
from .esquemas.pan import ClasePan

MODELO_CAJA = MODEL_PATH / "bread_detector_best.pt"
GALERIA_PANES = PROJECT_DATA_DIR / "galerias" / "resnet50_mexican-v3"
DATASET_MEXICAN = PROJECT_DATA_DIR / "mexican-v3"


class Tamaño(StrEnum):
    """Tamaños de la matriz YOLO26: n, s, m, l, x."""

    n = "n"
    s = "s"
    m = "m"
    l = "l"
    x = "x"


class AjustesPortero(BaseModel):
    """YOLO26-seg Mexican Bread: sólo decide si hay pan y dónde."""

    tamano: Tamaño = Tamaño.l  # En gris, l y x detectaron cosas distintas; ver el README.
    confianza: float = Field(0.35, gt=0, le=1)  # Más permisiva que YOLO solo: sólo filtra "hay pan".
    imgsz: int = Field(640, ge=32, multiple_of=32)

    @property
    def pesos(self) -> Path:
        return MODEL_PATH / f"yolo26{self.tamano}_mexican-v3_seg" / "weights" / "best.pt"


class AjustesConstruccion(BaseModel):
    """Con qué se construye la galería en la precarga."""

    dataset: Path = DATASET_MEXICAN
    clases: tuple[ClasePan, ...] | None = None  # None = todas las del dataset.
    gris: bool = True  # Mexican Bread v3 viene en gris; queda registrado en el manifiesto.


class Ajustes(BaseSettings):
    """Lo común a precarga y demo. Gana CLI, luego entorno, .env, la clase del script y estos defaults."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_nested_delimiter="__",
        # PORTERO__CONFIANZA cambia sólo ese campo; sin esto, borraría el tamaño fijado en app.py.
        nested_model_default_partial_update=True,
        extra="ignore",
    )

    dispositivo: str = "auto"
    galeria: Path = GALERIA_PANES


class AjustesDemo(Ajustes):
    """app.py, que también lee el CLI. El dominio (gris o color) lo dicta el manifiesto de la galería."""

    model_config = SettingsConfigDict(cli_prog_name="app.py")

    fuente: str = "0"  # Índice de cámara, foto o video.
    portero: AjustesPortero = Field(default_factory=AjustesPortero)
    umbral: float | None = Field(None, ge=-1, le=1)  # None = sin rechazo: YOLO ya dijo que es pan.


class AjustesPrecarga(Ajustes):
    """precargar.py. Nunca lee el CLI: por eso sólo aquí vive la clave y no queda en el historial."""

    roboflow_api_key: Annotated[SecretStr, Field(min_length=1)] | None = None
    construccion: AjustesConstruccion = Field(default_factory=AjustesConstruccion)


def directorio():
    return PROJECT_DATA_DIR


def dispositivo(valor="auto"):
    import torch

    if valor == "auto":
        if torch.cuda.is_available():
            return "0"
        return "mps" if torch.backends.mps.is_available() else "cpu"
    if valor == "mps" and not torch.backends.mps.is_available():
        raise ValueError("MPS no está disponible. Usa --device cpu.")
    if valor not in {"cpu", "mps"} and not valor.isdecimal():
        raise ValueError("Usa --device auto, cpu, mps o un índice CUDA como 0.")
    if valor.isdecimal() and int(valor) >= torch.cuda.device_count():
        raise ValueError(f"No existe el dispositivo CUDA {valor}.")
    return valor


def pesos_entrenados(ruta=None):
    if ruta is None:
        puntero = directorio() / "ultimo_modelo.txt"
        ruta = Path(puntero.read_text(encoding="utf-8").strip()) if puntero.is_file() else MODEL_PATH

    ruta = ruta.expanduser().resolve()
    if not ruta.is_file():
        raise FileNotFoundError(
            f"No existen los pesos: {ruta}. "
            "Usa el modelo oficial del repo o entrena uno nuevo."
        )
    return ruta
