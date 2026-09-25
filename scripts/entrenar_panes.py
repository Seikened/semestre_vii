import os
from pathlib import Path
from subprocess import run
from sys import argv

from ultralytics import YOLO

RAIZ = Path(__file__).resolve().parents[1]
DESCARGAS = Path.home() / "Descargas"
MODELOS = RAIZ / "models/aprendizaje_automatico_iii/proyecto_1"
ENTRENAMIENTOS = {
    f"yolo26{tamano}_{dataset}_{tarea}": (
        f"yolo26{tamano}{sufijo}.pt",
        DESCARGAS / carpeta / "data_local.yaml",
    )
    for dataset, (carpeta, tarea, sufijo) in {
        "bread-v2": ("bread-detector-v2-yolo26", "det", ""),
        "mexican-v3": ("mexican-bread-v3-yolo26", "seg", "-seg"),
    }.items()
    for tamano in "nsmlx"
}

if argv[1:] == ["--list"]:
    print("\n".join(ENTRENAMIENTOS))
    raise SystemExit

os.chdir(DESCARGAS)
for nombre in argv[1:] or ENTRENAMIENTOS:
    modelo, datos = ENTRENAMIENTOS[nombre]
    salida = MODELOS / nombre
    if not (salida / ".gitignore").is_file():
        if salida.exists():
            raise FileExistsError(salida)
        if not datos.is_file():
            raise FileNotFoundError(datos)
        YOLO(modelo).train(
            data=str(datos),
            project=str(MODELOS),
            name=nombre,
            epochs=100,
            patience=20,
            batch=0.7,
            device=0,
            workers=4,
            seed=42,
            save=True,
            plots=False,
        )
    run([str(RAIZ / "scripts/publicar_mejor_peso.sh"), nombre], check=True)
