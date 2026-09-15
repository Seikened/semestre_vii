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

`semestre_vii.vision_de_maquina.vision_node` contiene una API Fluent e inmutable para experimentar con imágenes como tensores PyTorch en layout `CHW`. La superficie pública sigue una filosofía parecida a Polars: se encadenan operaciones sobre objetos de dominio y se cruza a NumPy o PyTorch sólo de forma explícita cuando hace falta.

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

Cada transformación devuelve un nodo nuevo. El módulo acepta tensores de uno o tres canales con `torch.float32` o `torch.float64` y conserva `dtype`, `device` y autograd en las operaciones diferenciables.

Fourier tiene su propio objeto de dominio. `VisionNode.fft()` produce un `EspectroNode`; los filtros operan sobre ese espectro y `inversa()` regresa a `VisionNode`:

```python
imagen = VisionNode.desde_archivo(DATA_DIR / "TEXTO.BMP").escala_grises()

filtrada = (
    imagen
    .fft()
    .pasabajas_butterworth(30, orden=2)
    .inversa(valor_absoluto=True)
)
```

Para visualización externa, `to_numpy()` marca explícitamente la frontera hacia NumPy. Los módulos internos (`pixels/` y `signals/`) implementan la matemática y pueden probarse directamente, pero los ejercicios y consumidores normales deben preferir la API fluida.

El kit está separado por responsabilidad:

| Módulo | Responsabilidad | Base principal |
| --- | --- | --- |
| `node.py` | Fachada Fluent de imágenes y operadores aritméticos | PyTorch |
| `espectro.py` | Fachada Fluent del dominio de Fourier | PyTorch |
| `io.py` | Carga y guardado | Torchvision y Pillow |
| `pixels/transformaciones.py` | Color, intensidad, umbrales e histogramas | Kornia y PyTorch |
| `pixels/convoluciones.py` | Convolución, suavizado, ruido y derivadas | Kornia, SciPy y PyTorch |
| `pixels/visualizacion.py` | Imagen, histogramas y reportes | Matplotlib |
| `signals/espectros.py` | Transformada 2D, máscaras y filtros espectrales | PyTorch y Kornia |
| `signals/frecuencias.py` | FFT y detección de picos | PyTorch y scikit-image |
| `signals/graficas.py` | Señales y espectros interactivos | Matplotlib |
| `optica.py` | Focal, FOV, cámara y tablas comparativas | Polars |

Además de las transformaciones básicas, están disponibles los ajustes lineales por canal, ecualización, filtros box, piramidal, gaussiano y mediana, ruido uniforme y sal y pimienta, Laplaciano, FFT 1D y 2D, análisis de picos espectrales y cálculos de óptica.

```python
from semestre_vii.vision_de_maquina.vision_node import Camara, Escena, evaluar_focales

camara = Camara(ancho_px=2448, alto_px=2048, pixel_size_um=3.45)
escena = Escena(fov_ancho_mm=550, fov_alto_mm=350, do_mm=550)
tabla = evaluar_focales(camara, escena, [6, 8, 12, 25, 35, 50])
```

Las imágenes didácticas compartidas por la materia viven en `data/vision_de_maquina/` y se versionan junto con el repositorio. `DATA_DIR` permite localizarlas sin depender del directorio de ejecución.

## Nueva actividad

Al agregar una nueva actividad ejecutable, crearla bajo la materia correspondiente, darle un `__main__.py` pequeño y registrar un alias en `[project.scripts]` sólo cuando sea útil ejecutarla con frecuencia.

Los resultados finales que deban conservarse se guardan en `entregas/`. Los renders, previews, caches y archivos intermedios pertenecen a `tmp/` y nunca al historial de Git.
