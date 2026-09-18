"""Rutas del proyecto y selección explícita del dispositivo."""

from pathlib import Path

from . import MODEL_PATH, PROJECT_DATA_DIR


def directorio() -> Path:
    return PROJECT_DATA_DIR


def dispositivo(valor: str = "auto") -> str:
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


def pesos_entrenados(ruta: Path | None = None) -> Path:
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
