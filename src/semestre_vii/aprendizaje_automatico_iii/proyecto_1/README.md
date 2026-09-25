# Proyecto 1 · Caja asistida de panadería

**Aprendizaje Automático III, Semestre VII.** Detectar o segmentar cada pan de una bandeja, identificar su clase, contar las instancias visibles y estimar un ticket cuando existan precios. No procesa pagos ni es una caja autónoma certificada.

La red aprende **dónde está cada pan y qué clase es**. `precios.py` decide su precio; `cobro.py` calcula `cantidad × precio`. Cambiar un precio no requiere reentrenar. Los precios son ficticios y usan centavos enteros: dos conchas de $12, un bolillo de $5 y una dona de $15 suman **$44 MXN**.

## Estado experimental actual

El primer experimento con **YOLO26s-seg + Mexican Bread** se conserva como referencia, pero las pruebas externas mostraron problemas claros de generalización en color, escala y clasificación.

El segundo experimento usa **YOLO26m-detect + Bread Detector v2**. Su `best.pt` está publicado en `models/` y es el modelo predeterminado para la caja. Detecta 15 clases. `aplicacion/precios.py` relaciona cada etiqueta del detector con un nombre en español y un precio ficticio en centavos, además de conservar las 11 clases del experimento anterior. Por ejemplo, `wheat-bread` se muestra como "Pan de trigo" con un precio de demostración de $15 MXN. Una clase desconocida se cuenta, pero invalida el total.

Documentación:

- [Experimento 1: qué funcionó y qué falló](docs/01_experimento_segmentacion_mexican_bread.md)
- [Plan 2: entrenamiento de detección](docs/02_plan_detector_pan.md)
- [Índice de documentación](docs/README.md)

Runners directos del nuevo experimento:

```text
utils/download_bread_detector.py
entrenamiento/train_detector.py
```

## Modelo entrenado incluido

Los checkpoints publicados incluyen:

```text
models/aprendizaje_automatico_iii/proyecto_1/bread_detector_best.pt
models/aprendizaje_automatico_iii/proyecto_1/yolo26s_mexican_bread_seg_best.pt
models/aprendizaje_automatico_iii/proyecto_1/yolo26n_bread-v2_det/weights/best.pt
```

El primero es **YOLO26m-detect**, con 15 clases de Bread Detector v2. El segundo es **YOLO26s-seg**, con 11 clases de Mexican Bread. Cada `best.pt` contiene el modelo entrenado completo: para inferencia se carga directamente, sin combinarlo con los pesos base. En las corridas nuevas, los checkpoints temporales, incluido `last.pt`, quedan fuera de Git dentro de la carpeta de cada entrenamiento en `models/aprendizaje_automatico_iii/proyecto_1/`.

Para probarlo rápidamente con la primera cámara:

```bash
uv run src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/app.py
```

`app.py` usa por defecto el detector mediano previo y conserva el color de la imagen. Su diccionario `MODELOS` descubre automáticamente los nuevos `best.pt` cuando llegan al equipo. Para elegir uno:

```bash
uv run src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/app.py yolo26n_bread-v2_det
```

El modelo elegido debe existir localmente. Para usar el segmentador anterior desde la CLI:

```bash
uv run python -m semestre_vii.aprendizaje_automatico_iii.proyecto_1 caja --source data/aprendizaje_automatico_iii/proyecto_1/concha.jpg --model models/aprendizaje_automatico_iii/proyecto_1/yolo26s_mexican_bread_seg_best.pt --grayscale --sin-ventana
```

## Ejecución local, sin credenciales

**No se usa el SDK de Roboflow ni API keys.** Las utilidades de descarga sólo abren la página pública en el navegador, esperan el ZIP descargado a tu PC y después lo importan localmente. El entrenamiento y la inferencia siguen siendo locales.

El dataset sigue siendo una entrada necesaria para entrenar: un enlace no contiene los archivos en tu disco. Obtén una exportación ZIP con imágenes y etiquetas YOLO y guárdala en tu PC una vez. Si ya tienes una carpeta exportada, úsala directamente. **Los datasets y archivos intermedios no están incluidos en Git; sólo se publican los mejores pesos en `models/`.**

Esto no promete una instalación completamente desconectada: `uv` necesita obtener las dependencias, y Ultralytics puede descargar los pesos iniciales de YOLO/SAM cuando faltan. Esas descargas no son inferencia remota ni requieren la API key eliminada. La cámara, las imágenes y el entrenamiento del proyecto no se envían al servicio Roboflow.

## Arquitectura

```text
proyecto_1/
├── app.py                  # Punto de entrada: esto es lo que se ejecuta
├── __main__.py             # CLI opcional
├── configuracion.py        # Rutas y selección CPU / MPS / CUDA
├── aplicacion/
│   ├── runtime.py          # Flujo cámara/foto/video → modelo → resultado
│   ├── interfaz.py         # Visualización y capturas
│   ├── cobro.py            # Conteo, ticket y estabilidad
│   └── precios.py          # Precios ficticios
├── modelo/
│   └── yolo.py             # Traducción de cajas o máscaras a instancias
├── entrenamiento/
│   ├── datos.py            # Lectura/auditoría de datasets YOLO
│   ├── preparacion.py      # Preparación de segmentación
│   ├── segmentacion.py     # Entrenamiento/evaluación del experimento 1
│   ├── detector.py         # Entrenamiento del experimento 2
│   ├── prepare_segmentacion.py
│   ├── train_segmentacion.py
│   └── train_detector.py
├── utils/
│   ├── descargas.py        # Navegador + detección de ZIP descargado
│   ├── importacion.py      # ZIP/carpeta → dataset local
│   └── download_bread_detector.py
├── diagnostico/
│   ├── modelo.py           # Diagnóstico del checkpoint
│   └── gpu.py              # Diagnóstico CUDA/MPS
└── docs/
    ├── 01_experimento_segmentacion_mexican_bread.md
    ├── 02_plan_detector_pan.md
    └── 03_datasets_candidatos.md
```
Los datos originales, derivados y capturas van a `data/aprendizaje_automatico_iii/proyecto_1/`, fuera de `src` y excluidos de Git. Las corridas nuevas dejan sus archivos intermedios locales en `models/`; sólo se publican sus mejores pesos. No hay base de datos ni API web.

## Instalación

Desde la raíz de `semestre_vii`, sólo si aún no instalaste las dependencias:

```bash
uv add ultralytics opencv-python pyyaml
uv sync
```

Si esos comandos ya terminaron correctamente, no necesitas reinstalar nada. Se conservan el Python y las dependencias fijadas por el repositorio; `uv add` actualiza el lockfile localmente. Para la cámara usa OpenCV con interfaz, no la variante headless.

Para abreviar los comandos de esta guía, define un alias en la terminal actual:

```bash
alias pan='uv run python -m semestre_vii.aprendizaje_automatico_iii.proyecto_1'
pan --help
pan precios
```

El alias es opcional. Su equivalente completo es `uv run python -m semestre_vii.aprendizaje_automatico_iii.proyecto_1`. Si una terminal anterior sigue esperando la clave, cancela esa ejecución con **Ctrl+C** antes de actualizar el código.

## Importar un dataset de tu PC

Con el ZIP local, sustituyendo el nombre por el archivo real:

```bash
pan importar "$HOME/Downloads/mexican-bread.zip"
pan inspeccionar --verificar-fugas
```

También admite una carpeta o su YAML:

```bash
pan importar "$HOME/Downloads/mexican-bread"
pan importar "$HOME/Downloads/mexican-bread/data.yaml"
```

Son **alternativas**, no tres pasos consecutivos. El importador copia las imágenes y etiquetas, conserva los README/licencias de la raíz y `procedencia.json`, y deja intacto el origen. Detecta un `data.yaml` anidado dentro del ZIP; si hay varios, indica el YAML exacto desde una carpeta ya extraída. No descarga nada, no pide claves, no sobrescribe un destino existente y limpia sus archivos temporales si falla.

La copia queda preparada en:

```text
data/aprendizaje_automatico_iii/proyecto_1/dataset/
├── data.yaml
├── train/images/ + train/labels/
├── val/images/   + val/labels/
└── test/images/  + test/labels/  # cuando el dataset incluye test
```

El YAML generado usa rutas relativas, así que la copia no depende del ZIP ni de carpetas temporales. Las clases mantienen su orden original. Las importaciones exigen un dataset autocontenido: rechazan archivos externos, rutas inseguras, enlaces de ZIP, nombres duplicados y ZIPs de más de 20 GiB o 100,000 entradas.

**No necesitas copiar el dataset al repositorio** si prefieres dejarlo en otra ubicación. Puedes omitir `importar` y pasar el YAML local:

```bash
pan inspeccionar --data "$HOME/Downloads/mexican-bread/data.yaml" --verificar-fugas
pan preparar --data "$HOME/Downloads/mexican-bread/data.yaml" --con-sam --device mps
```

`--data` admite la estructura YOLO con carpetas `images` y `labels`, no COCO JSON ni listas de imágenes. `--destino` permite importar a otra carpeta; usa después el `--data` que imprime el comando.

La ruta antigua `data/aprendizaje_automatico_iii/proyecto_1/roboflow/data.yaml` se sigue reconociendo si ya existe y no hay un `dataset/data.yaml` nuevo. Ese nombre es sólo compatibilidad de archivos, no una conexión al servicio. Si existe `segmentado/data.yaml`, inspección, revisión, entrenamiento y evaluación lo prefieren por defecto. **Para comparar varios datasets o evitar seleccionar una preparación anterior, indica `--data` explícitamente.**

## Antes de entrenar: cajas no son máscaras

Fuente de referencia: [Mexican Bread de JPIA](https://universe.roboflow.com/jpia/mexican-bread), versión 3. No deduzcas el tipo de anotación sólo de la vista previa del sitio: **`inspeccionar` lee las etiquetas reales** y reporta imágenes, cajas, polígonos y cantidades por clase.

```text
0 0.50 0.50 0.20 0.30                      # caja: clase + centro/ancho/alto
0 0.10 0.10 0.80 0.10 0.80 0.80 0.10 0.80 # polígono: clase + puntos
```

YOLO26-seg requiere polígonos por instancia. Un exportador llamado `yolov8` describe el formato de etiquetas; no obliga a utilizar YOLOv8 ni transforma cajas en máscaras. El código lee los IDs y nombres desde el YAML, sin asumir el orden del diccionario de precios.

La auditoría rechaza clases inválidas, coordenadas no finitas, polígonos degenerados y etiquetas faltantes. Los negativos deben tener un `.txt` vacío explícito. `--verificar-fugas` detecta imágenes idénticas entre splits; no detecta por sí solo fotos casi iguales o sesiones de captura compartidas.

## Preparar y revisar las máscaras

Cuando las etiquetas ya contienen polígonos:

```bash
pan preparar
```

Cuando contienen cajas:

```bash
pan preparar --con-sam --device mps
```

La segunda alternativa utiliza cada caja como prompt de **SAM 2.1 Tiny local**, conserva la clase y produce propuestas de máscaras. No convierte las cuatro esquinas de una caja en ground truth. Procesa la exportación completa y conserva la separación train/val/test. No se activa sin `--con-sam` ni sobrescribe `segmentado`; para otro experimento usa otro `--destino`.

Las propuestas pueden incluir fondo, unir panes o cortar bordes. Quedan identificadas en `procedencia.json`; usarlas requiere `--aceptar-pseudoetiquetas`. Ese flag reconoce su procedencia, **no certifica su calidad**. Revisa y corrige las máscaras con una herramienta de anotación antes de evaluar resultados como si fueran etiquetas humanas.

```bash
pan revisar --split train --destino data/aprendizaje_automatico_iii/proyecto_1/revision/train
pan revisar --split val --destino data/aprendizaje_automatico_iii/proyecto_1/revision/val
pan revisar --split test --destino data/aprendizaje_automatico_iii/proyecto_1/revision/test
```

Cada comando exporta 20 ejemplos distribuidos por el split. `--limite 0` exporta todos. Son anotaciones superpuestas, **no predicciones de YOLO**; revisar veinte ejemplos no equivale a revisar todo el dataset. Omite test si tu exportación no lo incluye.

## Entrenar y publicar desde el servidor

Con los datasets en `~/Descargas/` y sus archivos `data_local.yaml`, `ENTRENAMIENTOS` en
`scripts/entrenar_panes.py` define las diez combinaciones. El script recorre los nombres indicados;
Ultralytics guarda `best.pt` y, al terminar cada corrida, publica sólo ese peso en `main` mediante Git LFS:

```bash
.venv/bin/python scripts/entrenar_panes.py yolo26s_bread-v2_det yolo26m_mexican-v3_seg
```

El wrapper `scripts/entrenar_y_publicar.sh` sigue disponible para la cola ya iniciada en Linux.
Cada combinación tiene una carpeta con versión, tamaño, dataset y tarea. `last.pt` y las salidas
temporales permanecen locales. Si el entrenamiento o el push falla, el script termina con error y
conserva la corrida para diagnóstico.

## Experimento 1: entrenar YOLO26-seg en tu equipo

Primero una prueba del recorrido, no un modelo confiable para cobrar:

```bash
pan entrenar --device mps --epochs 1 --batch 2 --fraction 0.02 --aceptar-pseudoetiquetas
```

Después, un primer experimento completo:

```bash
pan entrenar --device mps --epochs 30 --batch 4 --tamano n --aceptar-pseudoetiquetas
```

Omite `--aceptar-pseudoetiquetas` si no utilizaste SAM. Se rechaza entrenar segmentación con cajas. Empieza con `yolo26n-seg.pt`; puedes comparar `--tamano s` después de obtener una línea base. Los pesos preentrenados no reconocen automáticamente las clases mexicanas: se adaptan durante el entrenamiento.

`--device auto` selecciona CUDA, MPS o CPU según disponibilidad. En el Mac usa `mps`; ante falta de memoria reduce `--batch 2` o `--batch 1`. `--device cpu` es otra opción. Se usa `workers=0`, `cache=False` y semilla 42; la semilla no garantiza igualdad bit a bit entre dispositivos o versiones.

Cada ejecución crea un directorio propio en `runs/` con pérdidas, métricas y `weights/best.pt` / `weights/last.pt`. `experimento.json` registra configuración, procedencia y versiones. `ultimo_modelo.txt` apunta al último `best.pt` generado correctamente, incluso si era una prueba: **no significa que ese checkpoint sea bueno**. Usa `--model` para elegir otro.

## Abrir la caja local

```bash
pan caja --source 0 --device mps
```

También admite foto o video:

```bash
pan caja --source /ruta/bandeja.jpg --device mps
pan caja --source /ruta/video.mp4 --device mps
pan caja --source /ruta/bandeja.jpg --sin-ventana
```

Se muestran cajas o máscaras según el checkpoint, clase, confianza, piezas, subtotales disponibles, FPS e inferencia en milisegundos. **Espacio** pausa; **S** guarda una estimación JPG + JSON; **Q** o Escape cierra. Las fotos se guardan automáticamente. `--source 1` selecciona otra cámara y `--conf 0.65` cambia el umbral. En macOS concede permiso de cámara a la terminal/IDE que lance Python.

Se cuenta sólo el fotograma actual, sin acumular observaciones entre frames. La misma concha durante diez segundos sigue siendo una concha; al vaciar la bandeja, el total vuelve a cero. La estabilidad indica que el conteo se repitió cinco frames, **no que sea correcto**. No hay tracking acumulativo ni procesamiento de pagos.

Una clase sin precio no vale cero: invalida el total. Las 15 clases del detector tienen nombres en español y precios de demostración editables en `aplicacion/precios.py`. El importe depende de las detecciones del modelo y puede ser erróneo si clasifica o cuenta mal. El límite actual es 100 instancias por imagen.

## Evaluar el experimento 1 de segmentación

`pan evaluar` sólo acepta el dataset y el checkpoint del experimento de segmentación. La evaluación del detector nuevo con Bread Detector v2 todavía no está integrada a este comando.

Mientras eliges parámetros, utiliza validación:

```bash
pan evaluar --split val --device mps --aceptar-pseudoetiquetas
```

Cuando fijes el modelo y umbral, utiliza test como evaluación final:

```bash
pan evaluar --split test --device mps --aceptar-pseudoetiquetas
```

El reporte incluye mAP50–95 de cajas/máscaras, proporción de canastas con todas las cantidades por clase correctas, error absoluto de conteo por clase y error absoluto medio del importe en MXN, además del detalle por imagen. El mAP usa la evaluación estándar de Ultralytics; las métricas de negocio usan `--conf`, 0.50 por defecto. Un total coincidente no garantiza clases correctas: dos panes del mismo precio podrían intercambiarse.

Si val/test contienen máscaras SAM, el mAP de máscaras mide concordancia con **pseudoetiquetas**, no con segmentación humana independiente; el reporte lo identifica. Las clases y cantidades anotadas también deben auditarse.

Como objetivo experimental propuesto, no resultado obtenido, se puede exigir 95% de canastas exactas y error medio de importe menor a $1 MXN en bandejas nuevas. Ajusta esos criterios al riesgo tolerable. Incluye bandejas vacías, objetos ajenos, iluminación distinta y panes parcialmente tapados. Divide nuevas capturas por sesión/bandeja **antes** de aumentar datos: frames vecinos en train y test pueden falsear la evaluación. Un pan completamente oculto no es observable; confianza del modelo no equivale a probabilidad calibrada de cobro correcto.

## Límites de verificación

La importación y la inferencia deben revisarse con el dataset local, pesos reales, imágenes propias y cámara cuando corresponda. El repositorio incluye los dos `best.pt` finales publicados para inferencia; no inventa métricas ni incluye todos los checkpoints de entrenamiento.

## Fuentes y atribución

Dataset **Mexican Bread**, JPIA, Roboflow Universe, 2024, [versión 3](https://universe.roboflow.com/jpia/mexican-bread/dataset/3), licencia publicada **CC BY 4.0**. Conservar atribución a JPIA al reutilizar los datos. Eliminar el SDK no elimina la atribución a la fuente. Las máscaras generadas con SAM son una transformación derivada, no etiquetas publicadas por JPIA.

Documentación primaria: [segmentación YOLO26](https://docs.ultralytics.com/tasks/segment/), [formato de etiquetas](https://docs.ultralytics.com/datasets/segment/), [entrenamiento y MPS](https://docs.ultralytics.com/modes/train/) y [SAM 2](https://docs.ultralytics.com/models/sam-2/). Consulta las licencias de dependencias y pesos antes de convertir el prototipo académico en un producto comercial.
