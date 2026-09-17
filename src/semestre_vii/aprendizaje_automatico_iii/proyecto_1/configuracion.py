"""Rutas del repositorio y selección explícita del dispositivo."""

from pathlib import Path


def raiz() -> Path:
    for padre in Path(__file__).resolve().parents:
        if (padre / "pyproject.toml").is_file():
            return padre
    raise RuntimeError("Ejecuta este proyecto desde el checkout de semestre_vii.")


def directorio() -> Path:
    return raiz() / "data" / "aprendizaje_automatico_iii" / "proyecto_1"


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
        if not puntero.is_file():
            raise ValueError("Primero ejecuta entrenar o proporciona --model /ruta/a/best.pt.")
        ruta = Path(puntero.read_text(encoding="utf-8").strip())
    ruta = ruta.expanduser().resolve()
    if not ruta.is_file():
        raise FileNotFoundError(f"No existen los pesos: {ruta}")
    return ruta
