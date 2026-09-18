"""Fine-tuning de YOLO26 para detección de tipos de pan."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import sys
from uuid import uuid4

from ..configuracion import directorio, dispositivo
from .datos import cargar_dataset


@dataclass(frozen=True)
class EntrenamientoDetector:
    tamano: str = "m"
    epochs: int = 100
    batch: int | float = -1
    imgsz: int = 640
    device: str = "auto"
    patience: int = 25
    seed: int = 42
    multi_scale: float = 0.25

    def __post_init__(self) -> None:
        if self.tamano not in {"n", "s", "m", "l", "x"}:
            raise ValueError("Tamaño de YOLO26 inválido.")
        if self.epochs < 1 or self.patience < 1:
            raise ValueError("epochs y patience deben ser positivos.")
        if self.batch != -1 and self.batch <= 0:
            raise ValueError("batch debe ser -1 (auto) o un valor positivo.")
        if self.imgsz < 32 or self.imgsz % 32:
            raise ValueError("imgsz debe ser múltiplo de 32.")
        if not 0 <= self.multi_scale <= 0.5:
            raise ValueError("multi_scale debe estar entre 0 y 0.5.")


def entrenar_detector(data: Path, config: EntrenamientoDetector) -> Path:
    dataset = cargar_dataset(data, verificar_fugas=True)

    if any(
        etiqueta.segmentacion
        for muestra in dataset.muestras
        for etiqueta in muestra.etiquetas
    ):
        raise ValueError(
            "Este entrenamiento es de object detection y espera cajas YOLO, no polígonos."
        )

    from ultralytics import YOLO

    device_real = dispositivo(config.device)
    workers = 0 if device_real in {"cpu", "mps"} else 4
    identidad = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid4().hex[:6]}"
    base = directorio() / "deteccion"
    runs = base / "runs"
    runs.mkdir(parents=True, exist_ok=True)

    modelo = YOLO(f"yolo26{config.tamano}.pt")

    modelo.train(
        data=str(data.resolve()),
        epochs=config.epochs,
        batch=config.batch,
        imgsz=config.imgsz,
        device=device_real,
        patience=config.patience,
        seed=config.seed,
        multi_scale=config.multi_scale,
        pretrained=True,
        workers=workers,
        cache=False,
        deterministic=True,
        save_period=10,
        plots=True,
        project=str(runs),
        name=identidad,
        exist_ok=False,
    )

    salida = Path(modelo.trainer.save_dir).resolve()
    mejor = salida / "weights" / "best.pt"

    if not mejor.is_file():
        raise RuntimeError(f"El entrenamiento terminó sin best.pt; revisa {salida}.")

    manifiesto = {
        "fecha": datetime.now(timezone.utc).isoformat(),
        "objetivo": "deteccion_de_tipos_de_pan",
        "modelo_base": f"yolo26{config.tamano}.pt",
        "fine_tuning_completo": True,
        "configuracion": asdict(config),
        "device_real": device_real,
        "dataset": dataset.resumen(),
        "python": sys.version,
        "ultralytics": version("ultralytics"),
        "torch": version("torch"),
        "best_pt": str(mejor),
    }

    (salida / "experimento_detector.json").write_text(
        json.dumps(manifiesto, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    puntero = base / "ultimo_detector.txt"
    temporal = base / "ultimo_detector.tmp"
    temporal.write_text(str(mejor), encoding="utf-8")
    temporal.replace(puntero)

    return mejor
