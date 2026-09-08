# Semestre VII

Repositorio de código, actividades ejecutables y entregables del séptimo semestre.

La estructura separa deliberadamente **código**, **datos locales**, **archivos temporales** y **entregables finales** para evitar imports frágiles, rutas ambiguas y archivos gigantes versionados por accidente.

## Estructura

```text
semestre_vii/
├── src/semestre_vii/                 # código Python importable
│   └── <materia>/
│       └── actividades/
│           └── <actividad>/          # una actividad autocontenida
├── entregas/                         # PDFs y artefactos finales versionados
├── data/                             # datos por materia; se ignoran por defecto
├── tmp/                              # renders y archivos de trabajo; no se versiona
├── pyproject.toml                    # dependencias y entrypoints
└── AGENTS.md                         # reglas de trabajo del repositorio
```

`data/` se ignora por defecto, excepto los datasets académicos declarados explícitamente, como
`data/vision_de_maquina/`. `tmp/` siempre contiene archivos locales no versionados.

## Convención para materias y actividades

Los nombres de paquetes Python usan `snake_case`, sin espacios ni acentos. Cada materia vive en `src/semestre_vii/<materia>/` y cada ejercicio ejecutable en `actividades/<actividad>/`.

Una actividad debe exponer un `__main__.py` cuando tenga ejecución propia. Así puede ejecutarse desde cualquier punto del proyecto sin depender del directorio actual.

## Ejecución

Instalar o sincronizar el entorno:

```bash
uv sync
```

Ver los entrypoints disponibles:

```bash
uv run semestre-vii
```

ECOBICI, actividad entregada de Minería de Datos:

```bash
uv run ecobici --year 2025
```

También puede ejecutarse como módulo:

```bash
uv run python -m semestre_vii.mineria_de_datos.actividades.ecobici --year 2025
```

La actividad genera sus datos en `data/ecobici/`; la base DuckDB y los CSV descargados permanecen locales.

## Visión de máquina

`semestre_vii.vision_de_maquina.vision_node` contiene una API Fluent para experimentar con imágenes
como tensores PyTorch en layout `CHW`.

```python
from semestre_vii.vision_de_maquina import DATA_DIR
from semestre_vii.vision_de_maquina.vision_node import VisionNode

resultado = (
    VisionNode.desde_archivo(DATA_DIR / "golf.BMP")
    .escala_grises()
    .transformacion_gamma(0.8)
    .cuantizar(8)
    .guardar("tmp/vision/resultado.png")
)
```

Cada transformación devuelve un nodo nuevo. El módulo acepta tensores de uno o tres canales con
`torch.float32` o `torch.float64` y conserva `dtype`, `device` y autograd en las operaciones
diferenciables.

Las imágenes didácticas compartidas por la materia viven en `data/vision_de_maquina/` y se
versionan junto con el repositorio. `DATA_DIR` permite localizarlas sin depender del directorio de
ejecución.

## Nueva actividad

Al agregar una nueva actividad ejecutable, crearla bajo la materia correspondiente, darle un `__main__.py` pequeño y registrar un alias en `[project.scripts]` sólo cuando sea útil ejecutarla con frecuencia.

Los resultados finales que deban conservarse se guardan en `entregas/`. Los renders, previews, caches y archivos intermedios pertenecen a `tmp/` y nunca al historial de Git.
