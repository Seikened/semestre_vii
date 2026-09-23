"""Preparación local: cajas -> propuestas SAM, nunca cajas fingidas como máscaras."""

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import yaml

from ..configuracion import directorio, dispositivo
from .datos import cargar_dataset, leer_etiquetas


def preparar(origen: Path, destino: Path, con_sam: bool, device: str = "auto") -> Path:
    dataset = cargar_dataset(origen)
    destino = destino.expanduser().resolve()
    if destino.exists():
        raise FileExistsError(f"No se sobrescribe {destino}. Usa otro --destino.")
    hay_cajas = any(not e.segmentacion for m in dataset.muestras for e in m.etiquetas)
    if hay_cajas and not con_sam:
        raise ValueError("Hay cajas. Usa --con-sam para proponer máscaras y revísalas antes de entrenar.")
    sam = None
    if hay_cajas:
        from ultralytics import SAM

        pesos = directorio() / "pesos" / "sam2.1_t.pt"
        pesos.parent.mkdir(parents=True, exist_ok=True)
        sam = SAM(str(pesos))
        device = dispositivo(device)
    temporal = destino.with_name(f"{destino.name}.incompleto-{uuid4().hex[:8]}")
    temporal.mkdir(parents=True)
    try:
        for indice, muestra in enumerate(dataset.muestras, 1):
            relativa = muestra.imagen.relative_to(dataset.carpetas[muestra.split])
            imagen = temporal / muestra.split / "images" / relativa
            etiqueta = temporal / muestra.split / "labels" / relativa.with_suffix(".txt")
            imagen.parent.mkdir(parents=True, exist_ok=True)
            etiqueta.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(muestra.imagen, imagen)
            cajas = [e for e in muestra.etiquetas if not e.segmentacion]
            mascaras = iter(())
            if cajas:
                import cv2

                pixels = cv2.imread(str(muestra.imagen))
                if pixels is None:
                    raise ValueError(f"No se puede leer la imagen {muestra.imagen}")
                alto, ancho = pixels.shape[:2]
                prompts = []
                for e in cajas:
                    x, y, w, h = e.coordenadas
                    prompts.append([(x-w/2)*ancho, (y-h/2)*alto, (x+w/2)*ancho, (y+h/2)*alto])
                resultado = sam(pixels, bboxes=prompts, device=device, verbose=False)[0]
                if resultado.masks is None or len(resultado.masks) != len(cajas):
                    raise ValueError(f"SAM no devolvió una máscara por caja: {muestra.imagen}")
                mascaras = iter(resultado.masks.xyn)
            lineas = []
            for e in muestra.etiquetas:
                coords = e.coordenadas
                if not e.segmentacion:
                    poligono = next(mascaras)
                    if len(poligono) < 3:
                        raise ValueError(f"SAM produjo una máscara vacía: {muestra.imagen}")
                    coords = tuple(float(v) for v in poligono.clip(0, 1).reshape(-1))
                lineas.append(f"{e.clase} " + " ".join(f"{v:.8f}" for v in coords))
            etiqueta.write_text("\n".join(lineas) + ("\n" if lineas else ""), encoding="utf-8")
            leer_etiquetas(etiqueta, len(dataset.nombres))
            if indice % 25 == 0 or indice == len(dataset.muestras):
                print(f"Preparadas {indice}/{len(dataset.muestras)} imágenes", flush=True)
        contenido = {split: f"{split}/images" for split in dataset.carpetas}
        contenido.update(names=list(dataset.nombres), nc=len(dataset.nombres))
        (temporal / "data.yaml").write_text(yaml.safe_dump(contenido), encoding="utf-8")
        procedencia = {
            "fuente": str(dataset.yaml), "fecha": datetime.now(UTC).isoformat(),
            "pseudoetiquetas": hay_cajas or dataset.pseudoetiquetas,
            "generador": "sam2.1_t.pt" if hay_cajas else None,
            "advertencia": "Las propuestas SAM NO son ground truth humano. Revisar y corregir.",
        }
        (temporal / "procedencia.json").write_text(json.dumps(procedencia, indent=2), encoding="utf-8")
        cargar_dataset(temporal / "data.yaml")
        temporal.rename(destino)
    except BaseException:
        # Limpia únicamente el staging creado por esta ejecución, también ante Ctrl+C.
        shutil.rmtree(temporal)
        raise
    return destino / "data.yaml"
