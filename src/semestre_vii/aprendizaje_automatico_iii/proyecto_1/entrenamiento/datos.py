"""Lectura y auditoría del formato YOLO, sin modificar la exportación original."""

import json
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from pathlib import Path

import yaml

EXTENSIONES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


@dataclass(frozen=True)
class Etiqueta:
    clase: int
    coordenadas: tuple[float, ...]

    @property
    def segmentacion(self) -> bool:
        return len(self.coordenadas) >= 6


def leer_etiquetas(ruta: Path, clases: int) -> tuple[Etiqueta, ...]:
    if not ruta.is_file():
        raise ValueError(f"Falta {ruta}. Para imágenes negativas crea un .txt vacío explícito.")
    etiquetas = []
    for numero, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        if not linea.strip():
            continue
        try:
            valores = [float(v) for v in linea.split()]
        except ValueError as exc:
            raise ValueError(f"{ruta}:{numero}: anotación no numérica.") from exc
        if not all(isfinite(v) for v in valores):
            raise ValueError(f"{ruta}:{numero}: NaN o infinito en anotación.")
        clase, *coords = valores
        if not clase.is_integer() or not 0 <= clase < clases:
            raise ValueError(f"{ruta}:{numero}: clase fuera del catálogo.")
        if len(coords) != 4 and (len(coords) < 6 or len(coords) % 2):
            raise ValueError(f"{ruta}:{numero}: se esperaba caja YOLO o polígono de >=3 puntos.")
        if any(not 0 <= v <= 1 for v in coords):
            raise ValueError(f"{ruta}:{numero}: coordenadas fuera de [0, 1].")
        if len(coords) == 4:
            x, y, ancho, alto = coords
            if ancho <= 0 or alto <= 0:
                raise ValueError(f"{ruta}:{numero}: caja sin área.")
            if min(x - ancho / 2, y - alto / 2) < -0.001:
                raise ValueError(f"{ruta}:{numero}: caja fuera de la imagen.")
            if max(x + ancho / 2, y + alto / 2) > 1.001:
                raise ValueError(f"{ruta}:{numero}: caja fuera de la imagen.")
        else:
            puntos = list(zip(coords[::2], coords[1::2]))
            siguientes = puntos[1:] + puntos[:1]
            area = sum(x * v - u * y for (x, y), (u, v) in zip(puntos, siguientes))
            if abs(area) < 1e-10:
                raise ValueError(f"{ruta}:{numero}: polígono degenerado.")
        etiquetas.append(Etiqueta(int(clase), tuple(coords)))
    return tuple(etiquetas)


@dataclass(frozen=True)
class Muestra:
    split: str
    imagen: Path
    etiquetas: tuple[Etiqueta, ...]


@dataclass(frozen=True)
class Dataset:
    yaml: Path
    nombres: tuple[str, ...]
    carpetas: dict[str, Path]
    muestras: tuple[Muestra, ...]
    pseudoetiquetas: bool

    def resumen(self) -> dict:
        splits = {}
        for split in self.carpetas:
            muestras = [m for m in self.muestras if m.split == split]
            conteos = Counter(self.nombres[e.clase] for m in muestras for e in m.etiquetas)
            cajas = sum(not e.segmentacion for m in muestras for e in m.etiquetas)
            mascaras = sum(e.segmentacion for m in muestras for e in m.etiquetas)
            splits[split] = {"imagenes": len(muestras), "cajas": cajas, "poligonos": mascaras}
            splits[split]["instancias_por_clase"] = dict(conteos)
        return {"yaml": str(self.yaml), "pseudoetiquetas": self.pseudoetiquetas, "splits": splits}

    def exigir_segmentacion(self, aceptar_pseudo: bool = False) -> None:
        if any(not e.segmentacion for m in self.muestras for e in m.etiquetas):
            raise ValueError("Hay cajas, no sólo máscaras. Ejecuta preparar --con-sam y revisa el resultado.")
        if self.pseudoetiquetas and not aceptar_pseudo:
            raise ValueError("Revisa las máscaras generadas antes de usar --aceptar-pseudoetiquetas.")

    def guardar_yaml(self, ruta: Path) -> Path:
        contenido = {split: str(carpeta) for split, carpeta in self.carpetas.items()}
        contenido.update(names=list(self.nombres), nc=len(self.nombres))
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(yaml.safe_dump(contenido, allow_unicode=True), encoding="utf-8")
        return ruta


def eliminar_fugas_entre_splits(
    ruta: Path,
    *,
    raiz_permitida: Path | None = None,
) -> dict[str, int]:
    """Elimina copias idénticas entre splits, conservando train > val > test."""
    dataset = cargar_dataset(
        ruta,
        verificar_fugas=False,
        raiz_permitida=raiz_permitida,
    )
    hashes: dict[str, str] = {}
    eliminadas = Counter()

    for split in ("train", "val", "test"):
        carpeta = dataset.carpetas.get(split)
        if carpeta is None:
            continue

        for muestra in (m for m in dataset.muestras if m.split == split):
            huella = sha256(muestra.imagen.read_bytes()).hexdigest()
            anterior = hashes.get(huella)

            if anterior is None:
                hashes[huella] = split
                continue
            if anterior == split:
                continue

            relativa = muestra.imagen.relative_to(carpeta)
            etiqueta = carpeta.parent / "labels" / relativa.with_suffix(".txt")
            muestra.imagen.unlink()
            etiqueta.unlink()
            eliminadas[split] += 1

    return dict(eliminadas)


def cargar_dataset(ruta: Path, verificar_fugas: bool = False, *, raiz_permitida: Path | None = None) -> Dataset:
    ruta = ruta.expanduser().resolve()
    if not ruta.is_file():
        raise FileNotFoundError(
            f"No existe {ruta}. Usa importar /ruta/dataset.zip o --data /ruta/data.yaml. "
            "Las imágenes y etiquetas deben estar en tu PC; no se solicita ninguna API key."
        )
    if raiz_permitida is not None:
        raiz_permitida = raiz_permitida.resolve()
        if not ruta.is_relative_to(raiz_permitida):
            raise ValueError("El YAML debe estar dentro del dataset local.")
    try:
        contenido = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError("El archivo data.yaml no contiene YAML válido.") from exc
    if not isinstance(contenido, dict):
        raise ValueError("data.yaml debe contener un mapa con names, train y val.")
    nombres = contenido.get("names")
    if isinstance(nombres, dict):
        if set(nombres) != set(range(len(nombres))):
            raise ValueError("Los IDs de names deben ser enteros consecutivos desde cero.")
        nombres = [nombres[i] for i in range(len(nombres))]
    if not isinstance(nombres, list) or not nombres or not all(isinstance(n, str) and n for n in nombres):
        raise ValueError("Falta un catálogo válido names en data.yaml.")
    if len(set(nombres)) != len(nombres):
        raise ValueError("El catálogo contiene nombres de clase duplicados.")
    if "nc" in contenido and contenido["nc"] != len(nombres):
        raise ValueError("nc no coincide con names.")
    path = contenido.get("path", ".")
    if not isinstance(path, str):
        raise ValueError("path debe ser una ruta de texto.")
    base = (ruta.parent / path).resolve()
    carpetas, muestras, hashes = {}, [], {}
    for split in ("train", "val", "test"):
        valor = contenido.get(split)
        if not valor:
            if split != "test":
                raise ValueError(f"Falta el split obligatorio {split}.")
            continue
        if not isinstance(valor, str):
            raise ValueError("Este proyecto espera una carpeta images por split, no listas ni URLs.")
        carpeta = (base / valor).resolve()
        # Roboflow exporta a veces ../train/images respecto del YAML situado en la raíz.
        fuera = raiz_permitida is not None and not carpeta.is_relative_to(raiz_permitida)
        if (not carpeta.is_dir() or fuera) and valor.startswith("../"):
            carpeta = (ruta.parent / valor.removeprefix("../")).resolve()
        if raiz_permitida is not None and not carpeta.is_relative_to(raiz_permitida):
            raise ValueError(f"El split {split} apunta fuera del dataset local.")
        if not carpeta.is_dir() or carpeta.name != "images":
            raise ValueError(f"No existe una carpeta images válida para {split}: {carpeta}")
        if carpeta in carpetas.values():
            raise ValueError("Dos splits apuntan a la misma carpeta.")
        carpetas[split] = carpeta
        imagenes = sorted(p for p in carpeta.rglob("*") if p.suffix.lower() in EXTENSIONES)
        if not imagenes:
            raise ValueError(f"El split {split} no contiene imágenes.")
        rutas_etiquetas = set()
        for imagen in imagenes:
            relativa = imagen.relative_to(carpeta).with_suffix(".txt")
            etiqueta = carpeta.parent / "labels" / relativa
            if raiz_permitida is not None:
                if any(not p.resolve().is_relative_to(raiz_permitida) for p in (imagen, etiqueta)):
                    raise ValueError("Una imagen o etiqueta apunta fuera del dataset local.")
            if etiqueta in rutas_etiquetas:
                raise ValueError(f"Varias imágenes comparten una etiqueta: {etiqueta}")
            rutas_etiquetas.add(etiqueta)
            etiquetas = leer_etiquetas(etiqueta, len(nombres))
            muestras.append(Muestra(split, imagen, etiquetas))
            if verificar_fugas:
                huella = sha256(imagen.read_bytes()).hexdigest()
                if huella in hashes and hashes[huella] != split:
                    raise ValueError(f"Imagen duplicada entre {hashes[huella]} y {split}: {imagen}")
                hashes[huella] = split
    for split in ("train", "val"):
        if not any(m.etiquetas for m in muestras if m.split == split):
            raise ValueError(f"El split {split} no contiene instancias anotadas.")
    manifiesto = ruta.parent / "procedencia.json"
    pseudo = False
    if manifiesto.is_file():
        if raiz_permitida is not None and not manifiesto.resolve().is_relative_to(raiz_permitida):
            raise ValueError("La procedencia apunta fuera del dataset local.")
        pseudo = bool(json.loads(manifiesto.read_text(encoding="utf-8")).get("pseudoetiquetas"))
    return Dataset(ruta, tuple(nombres), carpetas, tuple(muestras), pseudo)
