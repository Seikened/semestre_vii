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
├── data/                             # datos por materia
├── tmp/                              # renders y archivos de trabajo; no se versiona
├── pyproject.toml                    # dependencias y entrypoints
└── AGENTS.md                         # reglas de trabajo del repositorio
```

Cada materia usa `data/<materia>/`, con el mismo nombre que su paquete en `src/semestre_vii/`.
Las imágenes didácticas de Visión de Máquina y algunos CSV de Minería de Datos ya están
versionados. Los CSV grandes del examen se conservan con Git LFS. Los datos operativos de
Desarrollo de Aplicaciones y los artefactos temporales de Aprendizaje Automático III permanecen
locales. Los nuevos mejores pesos de panadería se publican en `models/` con Git LFS.
`tmp/` siempre contiene archivos locales no versionados.

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

La actividad genera sus datos en `data/mineria_de_datos/ecobici/`; la base DuckDB y los CSV descargados permanecen locales.

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

Para visualización externa, `to_numpy()` marca explícitamente la frontera hacia NumPy. Los módulos internos (`pixels/` y `signals/`) implementan la matemática, pero los ejercicios y consumidores normales deben preferir la API fluida.

El notch ideal rechaza círculos alrededor de frecuencias seleccionadas para eliminar componentes
periódicas. Los centros se expresan como `(desplazamiento_fila, desplazamiento_columna)` respecto
a DC, en bins de la FFT centrada, y cada centro incluye automáticamente su pareja conjugada:

```python
espectro = imagen.fft()
rechazado = espectro.notch_ideal(centros=[(0, 50)], radio=15)
filtrada = rechazado.inversa()
rechazado.mascara_imagen().mostrar()
```

En una matriz de 256 por 256, `(0, 50)` coloca los círculos en `(128, 178)` y `(128, 78)`.
Si se parte de una coordenada absoluta `(i0, j0)`, restar `(alto // 2, ancho // 2)` para
obtener el desplazamiento. Se pueden dar varios centros y coordenadas fraccionarias.
La máscara vale 0 cuando la distancia al centro es menor que `radio` y 1 fuera del círculo,
con el mismo radio para todos los pares. El radio también se mide en bins.
Los círculos continúan por el borde opuesto al cruzar el límite periódico de la DFT.
Un círculo que alcance DC también elimina la media, por lo que conviene elegir centros y radio
que excluyan esa componente cuando se quiera conservar el brillo promedio.
La operación mantiene el espectro original y requiere `fft()` centrada.
Con `centros=()`, la máscara conserva todos los valores en 1: es un filtro pasa todo.
Al encadenar filtros, el espectro conserva la máscara acumulada de todas las operaciones.

El ejercicio `ejercicio_fourier/notch.py` aplica esta API a `data/vision_de_maquina/Camisa.jpg`
en escala de grises: primero H = 1, después cuatro círculos de valor 0 con radios por componente,
y finalmente FT2 = FT · H (multiplicación elemento a elemento).
La imagen mide 570 por 568, con DC en `(285, 284)`. El centro absoluto `(285, 358)` de la foto
equivale al desplazamiento `(0, 74)`; su pareja simétrica es `(285, 210)`.
Para cualquier centro absoluto `(icc, jcc)`, la pareja es `(2*ic - icc, 2*jc - jcc)`,
con `ic = alto // 2` y `jc = ancho // 2`, considerando los índices periódicos de la DFT.
El demo muestra tres paneles: Fourier filtrado con los círculos del notch, camisa original
y camisa filtrada.
El par `(0, 74)`, sobre el eje X de Fourier, atenúa las franjas verticales con `radio_x=30`.
El par `(71, 0)`, sobre el eje Y, atenúa las franjas horizontales con `radio_y=20`.
Cada centro incluye automáticamente su pareja conjugada.
Los centros corresponden a esta imagen; al usar otra, elegirlos a partir de su propio espectro.

```bash
uv run python -m semestre_vii.vision_de_maquina.ejercicio_fourier.notch
```

Los radios se ajustan de forma independiente desde los parámetros de `main`:

```python
from semestre_vii.vision_de_maquina.ejercicio_fourier.notch import main

main(radio_x=30, radio_y=15)
```

El segundo demo, `ejercicio_fourier/notch_sacos.py`, usa únicamente la foto
`data/vision_de_maquina/saco_paneles_led_cortada.bmp` que proporcionó Fernando.
Mide 1637 por 2056 píxeles (ancho por alto). Antes de calcular Fourier, se toma el cuadrado
inferior de 1637 por 1637: filas `[419:2056]` y todas las columnas, sin redimensionar.
La foto del disco se conserva completa. Los tres paneles muestran Fourier con el notch,
el recorte original y el recorte filtrado en escala de grises.

Los centros corresponden a la FFT del recorte cuadrado:

| Grupo | Centros (fila, columna) relativos a DC |
| --- | --- |
| X | `(-1, 84)`, `(-2, 157)` |
| Y | `(84, 1)`, `(106, 1)` |
| Diagonales | `(73, 85)`, `(75, -79)` |

Los radios por grupo son independientes: X = 30, Y = 20 y diagonales = 25 bins.
El rechazo atenúa parte del tejido; su borde ideal también produce oscilaciones junto a bordes
de alto contraste. Los centros y radios son un punto de partida para experimentar.

```bash
uv run python -m semestre_vii.vision_de_maquina.ejercicio_fourier.notch_sacos
```

```python
from semestre_vii.vision_de_maquina.ejercicio_fourier.notch_sacos import main

main(radio_x=30, radio_y=15, radio_diagonal=25)
```

El laboratorio web `ejercicio_fourier/notch_web` permite diseñar el filtro sobre ese mismo
cuadrado inferior. Corre localmente con las dependencias existentes y abre el navegador:

```bash
uv run python -m semestre_vii.vision_de_maquina.ejercicio_fourier.notch_web
```

La dirección inicial es `http://127.0.0.1:8768`. Se puede cambiar con `--port 8770` o evitar
abrir otra pestaña con `--no-browser`. `Ctrl+C` cierra el servidor.

- Un clic en Fourier agrega un centro y su conjugado automáticamente. Agregar otros pares
  permite bloquear la fundamental y sus armónicos, elegidos sobre el espectro.
- Cada par tiene radio independiente, activación y eliminación. «Deshacer» recupera el cambio
  anterior. Al seleccionar un centro, las flechas lo mueven un bin y `Shift` con flecha, cinco.
- Zoom, rueda y arrastre permiten inspeccionar Fourier. La vista conserva el espectro filtrado
  como fondo; «Ver Fourier original» ayuda a ubicar los siguientes picos.
- Original y filtrada comparten zoom y desplazamiento para comparar tejido y letras.
- «Guardar puntos» exporta un JSON y «Cargar puntos» recupera sus coordenadas, radios y activación.
  «Copiar filtro» entrega las llamadas a `notch_ideal`; «Descargar PNG» guarda la imagen resultante.

Las coordenadas manuales son `(fila Y, columna X)` relativas a DC `(818, 818)` y los radios se
miden en bins. La máscara mantiene la simetría y continuidad periódica de la DFT. Se reconstruye
con `clip(abs(IFFT(FT · H)), 0, 1)`. Sin puntos activos se muestra la imagen original.
El porcentaje indica los bins rechazados; no mide la calidad del resultado. La web avisa si
un círculo bloquea DC. No modifica la foto fuente ni guarda archivos en el servidor.

El ejercicio `ejercicio_fourier/pasabajas_saco.py` reproduce el primer paso con Butterworth:
aplica únicamente un pasabajas al mismo cuadrado inferior del saco LED, antes de construir
una banda. Usa `H = 1 / (1 + (D / corte) ** (2 * orden))`, con DC en `(818, 818)`.
Muestra Fourier filtrado, recorte original y recorte filtrado, sin gráficas de señales.
Se calcula `FT2 = FT · H` elemento a elemento y `IMG2 = clip(abs(IFFT(FT2)), 0, 1)`.
El clip usa el rango normalizado de los tensores de imagen.
El corte inicial de 50 bins y el orden 2 son valores para experimentar; no identifican por sí
solos la fundamental ni sus armónicos. El pasabajas también suaviza letras y bordes.

```bash
uv run python -m semestre_vii.vision_de_maquina.ejercicio_fourier.pasabajas_saco
```

```python
from semestre_vii.vision_de_maquina.ejercicio_fourier.pasabajas_saco import main

main(corte=80, orden=2)
```

El ejercicio `ejercicio_fourier/rechazabanda_saco.py` continúa con la suma de máscaras de clase:
`HPB = BLPF(60, 5)`, `HPA = 1 - BLPF(150, 5)` y `HRB = HPB + HPA`.
La librería expone `espectro.rechazabanda_butterworth(corte_bajo, corte_alto, orden_bajo, orden_alto)`.
Los cortes deben cumplir `0 < corte_bajo < corte_alto` y se miden en bins de la FFT centrada.
Se suma H antes de calcular `FT2 = FT · HRB`, y se reconstruye con valor absoluto y clip.
La banda radial se atenúa con transiciones suaves; los armónicos exteriores siguen pasando.
Para rechazar otros anillos se pueden encadenar llamadas con otros pares de cortes.

Usa los últimos valores dictados (60, 150 y órdenes 5/5). La foto muestra una prueba anterior
con 70, 140 y órdenes 5/7, que también se puede reproducir con los parámetros de `main`.
Los tres demos del saco comparten el mismo recorte inferior mediante `ejercicio_fourier/saco.py`.
El nuevo demo muestra Fourier filtrado, original y filtrada, sin gráficas de señales.

```bash
uv run python -m semestre_vii.vision_de_maquina.ejercicio_fourier.rechazabanda_saco
```

```python
from semestre_vii.vision_de_maquina.ejercicio_fourier.rechazabanda_saco import main

main(corte_bajo=70, corte_alto=140, orden_bajo=5, orden_alto=7)
```

### Ruido gaussiano y filtrado

La actividad `actividades/ruido_filtrado` reproduce la clase con una imagen uniforme
de 256×256 a 127 y con `golf.BMP`. Compara la referencia limpia, la entrada con ruido,
el pasabajas gaussiano y la selección por umbral. Incluye histogramas, corte de la fila 100,
Fourier, máscara H, diferencias centradas en 127 y RMSE frente a la referencia limpia.

```bash
uv run python -m semestre_vii.vision_de_maquina.actividades.ruido_filtrado
```

Los parámetros del ejercicio usan tonos de gris para sigma y umbral, y bins para el corte:

```python
from semestre_vii.vision_de_maquina.actividades.ruido_filtrado.__main__ import main

main(sigma=10, corte=30, umbral=20, seed=7)
```

La librería trabaja con intensidades normalizadas. `ruido_gaussiano` suma una muestra normal
independiente por píxel y canal, admite sigma cero y recorta a `[0, 1]`. Una semilla fija permite
comparar cortes sobre el mismo ruido sin cambiar el generador global:

```python
ruidosa = limpia.ruido_gaussiano(sigma=10 / 255, media=0, seed=7)
filtrada = ruidosa.fft().pasabajas_gaussiano(50).inversa(valor_absoluto=True, clip=True)
con_umbral = ruidosa.filtro_umbral(filtrada, umbral=10 / 255)
```

`filtro_umbral` elige la filtrada si `abs(entrada - filtrada) < umbral`; en caso contrario,
conserva la entrada con ruido. Se corrigió la selección invertida que tenía esta función.
Es una heurística espacial no lineal: puede conservar ruido intenso y no garantiza conservar
todos los bordes. No equivale a multiplicar Fourier por una máscara H fija. La mediana también
es no lineal; los filtros de mediana existentes siguen disponibles para sal y pimienta.

La resta `entrada - filtrada + 127/255` muestra tanto ruido como información atenuada. Por eso
el ejercicio conserva además una referencia limpia y muestra `limpia - GLPF(limpia) + 127/255`.
El RMSE se calcula antes de desplazar o recortar las diferencias. Bajar el corte atenúa más
frecuencias altas y aumenta el desenfoque; un RMSE menor en la imagen uniforme no garantiza
un RMSE menor en una escena real.

Normal y uniforme son distribuciones distintas. Para una normal, aproximadamente 99.73% de
las muestras están en `media ± 3σ`. Cerca de 0 y 255, el clip altera esa distribución.
La actividad también simula nueve tomas independientes de la escena uniforme fija:
`std(toma1 - toma2)/√2` estima sigma y el promedio de N tomas reduce sigma a aproximadamente
`σ/√N`. Esto supone escena e iluminación estables, ruido independiente y sin saturación relevante.

El pasabajas en Fourier equivale a una convolución circular espacial con la IFFT de H.
Una convolución con bordes reflejados no es idéntica en los límites. La FFT usa sumas discretas;
la conveniencia frente a convolución directa depende del tamaño de la imagen y del kernel.

El kit está separado por responsabilidad:

| Módulo | Responsabilidad | Base principal |
| --- | --- | --- |
| `node.py` | Fachada Fluent de imágenes y operadores aritméticos | PyTorch |
| `visualizacion_node.py` | Métodos de presentación de VisionNode, conservando la API fluida | Matplotlib |
| `espectro.py` | Fachada Fluent del dominio de Fourier | PyTorch |
| `io.py` | Carga y guardado | Torchvision y Pillow |
| `pixels/transformaciones.py` | Color, intensidad, umbrales e histogramas | Kornia y PyTorch |
| `pixels/convoluciones.py` | Convolución, suavizado, ruido y derivadas | Kornia, SciPy y PyTorch |
| `pixels/visualizacion.py` | Imagen, histogramas y reportes | Matplotlib |
| `signals/espectros.py` | Transformada 2D, máscaras y filtros espectrales | PyTorch y Kornia |
| `signals/frecuencias.py` | FFT y detección de picos | PyTorch y scikit-image |
| `signals/graficas.py` | Señales y espectros interactivos | Matplotlib |
| `optica.py` | Focal, FOV, cámara y tablas comparativas | Polars |

Además de las transformaciones básicas, están disponibles los ajustes lineales por canal, ecualización, filtros box, piramidal, gaussiano y mediana, selección por umbral, ruido gaussiano, uniforme y sal y pimienta, Laplaciano, FFT 1D y 2D, análisis de picos espectrales y cálculos de óptica.

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
