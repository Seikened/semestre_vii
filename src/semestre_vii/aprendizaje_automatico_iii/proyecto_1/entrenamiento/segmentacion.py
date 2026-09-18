"""Fine-tuning y evaluación; artefactos separados de los datos originales."""

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import sys
from uuid import uuid4

from ..aplicacion.cobro import calcular_ticket, normalizar
from ..configuracion import directorio, dispositivo, pesos_entrenados
from .datos import cargar_dataset
from ..modelo.segmentacion import Segmentador


@dataclass(frozen=True)
class Entrenamiento:
    tamano: str = "n"
    epochs: int = 30
    batch: int = 4
    imgsz: int = 640
    device: str = "auto"
    fraction: float = 1.0
    seed: int = 42

    def __post_init__(self):
        if self.tamano not in {"n", "s", "m", "l", "x"}:
            raise ValueError("Tamaño de YOLO26 inválido.")
        if self.epochs < 1 or self.batch < 1 or not 0 < self.fraction <= 1:
            raise ValueError("epochs y batch deben ser positivos; fraction debe estar en (0,1].")
        if self.imgsz < 32 or self.imgsz % 32:
            raise ValueError("imgsz debe ser múltiplo de 32.")


def entrenar(data: Path, config: Entrenamiento, aceptar_pseudo: bool = False) -> Path:
    dataset = cargar_dataset(data, verificar_fugas=True)
    dataset.exigir_segmentacion(aceptar_pseudo)
    if not calcular_ticket(dataset.nombres).completo:
        raise ValueError("Faltan precios para algunas clases. Actualiza precios.py.")
    from ultralytics import YOLO

    dispositivo_real = dispositivo(config.device)
    nombre = f"yolo26{config.tamano}-seg.pt"
    base = directorio()
    (base / "pesos").mkdir(parents=True, exist_ok=True)
    identidad = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid4().hex[:6]}"
    yaml_normalizado = dataset.guardar_yaml(base / "configuraciones" / f"{identidad}.yaml")
    modelo = YOLO(str(base / "pesos" / nombre))
    modelo.train(
        data=str(yaml_normalizado), epochs=config.epochs, batch=config.batch,
        imgsz=config.imgsz, device=dispositivo_real, fraction=config.fraction,
        seed=config.seed, workers=0, cache=False, patience=10, deterministic=True,
        project=str(base / "runs"), name=identidad, exist_ok=False,
    )
    salida = Path(modelo.trainer.save_dir).resolve()
    mejor = salida / "weights" / "best.pt"
    if not mejor.is_file():
        raise RuntimeError(f"El entrenamiento terminó sin best.pt; revisa {salida}.")
    manifiesto = {
        "fecha": datetime.now(timezone.utc).isoformat(), "configuracion": asdict(config),
        "device_real": dispositivo_real, "dataset": dataset.resumen(),
        "python": sys.version, "ultralytics": version("ultralytics"), "torch": version("torch"),
        "pesos": str(mejor), "solo_prueba": config.epochs == 1 or config.fraction < 1,
    }
    (salida / "experimento.json").write_text(json.dumps(manifiesto, indent=2), encoding="utf-8")
    puntero = base / "ultimo_modelo.txt"
    provisional = base / "ultimo_modelo.tmp"
    provisional.write_text(str(mejor), encoding="utf-8")
    provisional.replace(puntero)
    return mejor


def evaluar(data: Path, pesos: Path | None, split: str, device: str, conf: float,
            aceptar_pseudo: bool = False) -> Path:
    import cv2

    dataset = cargar_dataset(data, verificar_fugas=True)
    dataset.exigir_segmentacion(aceptar_pseudo)
    if split not in dataset.carpetas:
        raise ValueError(f"El dataset no tiene split {split}.")
    pesos = pesos_entrenados(pesos)
    segmentador = Segmentador(pesos, device, conf)
    if set(map(normalizar, dataset.nombres)) != set(map(normalizar, segmentador.modelo.names.values())):
        raise ValueError("Las clases del checkpoint no coinciden con las del dataset.")
    if tuple(dataset.nombres) != tuple(segmentador.modelo.names[i] for i in range(len(dataset.nombres))):
        raise ValueError("El orden de clases difiere: la evaluación por IDs sería incorrecta.")
    salida = directorio() / "evaluaciones" / uuid4().hex[:10]
    salida.mkdir(parents=True)
    yaml_normalizado = dataset.guardar_yaml(salida / "data.yaml")
    metricas = segmentador.modelo.val(
        data=str(yaml_normalizado), split=split, device=segmentador.device,
        batch=4, workers=0, project=str(salida), name="metricas", verbose=False,
    )
    filas, exactas, error_piezas, error_dinero = [], 0, 0, 0
    for muestra in (m for m in dataset.muestras if m.split == split):
        imagen = cv2.imread(str(muestra.imagen))
        if imagen is None:
            raise ValueError(f"No se puede leer {muestra.imagen}")
        lectura = segmentador.predecir(imagen)
        esperado = Counter(dataset.nombres[e.clase] for e in muestra.etiquetas)
        predicho = Counter(i.clase for i in lectura.instancias)
        real = calcular_ticket(esperado.elements())
        estimado = calcular_ticket(predicho.elements())
        error = abs(estimado.total_centavos - real.total_centavos)
        error_conteo = sum(abs(esperado[c] - predicho[c]) for c in esperado.keys() | predicho.keys())
        exactas += esperado == predicho
        error_dinero += error
        error_piezas += error_conteo
        filas.append({"imagen": str(muestra.imagen), "real": dict(esperado), "predicho": dict(predicho),
                      "error_centavos": error, "error_conteo": error_conteo})
    n = len(filas)
    reporte = {
        "split": split, "imagenes": n, "conf_caja": conf, "pesos": str(pesos),
        "map50_95_cajas": float(metricas.box.map), "map50_95_mascaras": float(metricas.seg.map),
        "mascaras_son_pseudoetiquetas": dataset.pseudoetiquetas,
        "canastas_exactas": exactas / n, "mae_conteo_por_clase": error_piezas / n,
        "mae_total_mxn": error_dinero / n / 100, "detalle": filas,
    }
    ruta = salida / "reporte.json"
    ruta.write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in reporte.items() if k != "detalle"}, indent=2))
    return ruta
