# Proyecto 1 · Caja asistida de panadería

**Aprendizaje Automático III — Semestre VII.** Segmentar cada pan de una bandeja, clasificarlo, contar las instancias visibles y estimar un ticket en MXN. No procesa pagos ni es una caja autónoma certificada.

La red aprende **dónde está cada pan y qué clase es**. `precios.py` decide su precio; `cobro.py` calcula `cantidad × precio`. Cambiar un precio no requiere reentrenar. Los precios son ficticios y usan centavos enteros: dos conchas de $12, un bolillo de $5 y una dona de $15 suman **$44 MXN**.

## Modelo entrenado incluido

El modelo final de referencia está versionado en:

```text
models/aprendizaje_automatico_iii/proyecto_1/yolo26s_mexican_bread_seg_best.pt
```

Ese archivo es el **`best.pt`** del fine-tuning de YOLO26s-seg con Mexican Bread. Los checkpoints temporales de entrenamiento, incluido `last.pt`, permanecen fuera de Git dentro de `data/aprendizaje_automatico_iii/`.

Para probarlo rápidamente con la primera cámara:

```bash
uv run src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/run_model.py
```

`run_model.py` carga explícitamente el modelo oficial anterior; no depende de `ultimo_modelo.txt` ni de la máquina donde se entrenó.

## Ejecución local, sin credenciales

**Se eliminó el descargador y su solicitud de API key.** No existe el comando `descargar`, no se importa el SDK `roboflow` y no hay que instalarlo ni configurar una cuenta dentro del programa. La importación, preparación, entrenamiento e inferencia trabajan con archivos en tu PC; no se utilizan endpoints de predicción o entrenamiento de Roboflow.

El dataset sigue siendo una entrada necesaria: un enlace no contiene los archivos en tu disco. Obtén una exportación ZIP con imágenes y etiquetas YOLO del dataset de referencia y guárdala en tu PC una vez. Si ya tienes una carpeta exportada, úsala directamente. **Los datasets y artefactos de entrenamiento no están incluidos en Git; el único checkpoint versionado es el modelo final `best.pt` publicado en `models/`.**

Esto no promete una instalación completamente desconectada: `uv` necesita obtener las dependencias, y Ultralytics puede descargar los pesos iniciales de YOLO/SAM cuando faltan. Esas descargas no son inferencia remota ni requieren la API key eliminada. La cámara, las imágenes y el entrenamiento del proyecto no se envían al servicio Roboflow.

## Arquitectura

```text
proyecto_1/
├── __main__.py       # CLI por etapas, sin ejecutar nada al importar
├── configuracion.py  # Rutas y selección CPU / MPS / CUDA
├── importacion.py    # ZIP, carpeta o YAML local; sin red ni credenciales
├── datos.py          # YAML, anotaciones, conteos y auditoría
├── preparacion.py    # Propuestas SAM locales sólo cuando hay cajas
├── entrenamiento.py # Fine-tuning y evaluación técnica + de negocio
├── vision.py         # Adaptador de Ultralytics a instancias explícitas
├── precios.py        # Única fuente de verdad de precios ficticios
├── cobro.py          # Ticket y estabilidad, sin dependencias de visión
├── interfaz.py       # Máscaras, desglose y capturas JPG + JSON
└── aplicacion.py     # Foto, video o cámara; orquestación del recorrido
```

Los datos originales, derivados, pesos, configuraciones, experimentos y capturas van a `data/aprendizaje_automatico_iii/proyecto_1/`, fuera de `src` y excluidos de Git. Las pruebas están en `tests/proyecto_1/`. No hay base de datos, API web, servicios vacíos ni jerarquías de clases innecesarias.

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

## Entrenar YOLO26-seg en tu equipo

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

Se muestran máscaras, clase, confianza, piezas, subtotales, total, FPS e inferencia en milisegundos. **Espacio** pausa; **S** guarda una estimación JPG + JSON; **Q** o Escape cierra. Las fotos se guardan automáticamente. `--source 1` selecciona otra cámara y `--conf 0.65` cambia el umbral. En macOS concede permiso de cámara a la terminal/IDE que lance Python.

Se cuenta sólo el fotograma actual, sin acumular observaciones entre frames. La misma concha durante diez segundos sigue siendo una concha; al vaciar la bandeja, el total vuelve a cero. La estabilidad indica que el conteo se repitió cinco frames, **no que sea correcto**. No hay tracking acumulativo ni procesamiento de pagos.

Una clase sin precio no vale cero: invalida el total y exige corregir el catálogo/modelo. Un checkpoint COCO genérico no se acepta como si estuviera entrenado para esta panadería. El límite actual es 100 instancias por imagen.

## Evaluar la problemática

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

## Pruebas y límites de verificación

```bash
uv run pytest tests/proyecto_1 -q
```

`test_importacion_local.py` prueba ZIPs, carpetas, validación, preservación del origen, compatibilidad de rutas y CLI. Bloquea conexiones de red y solicitudes de entrada/credenciales durante las pruebas. Esos casos no requieren YOLO ni SAM.

Las pruebas originales de integración con YOLO, SAM y cámara usan simulaciones explícitas. No sustituyen una ejecución con pesos reales, tus imágenes y tu cámara. El repositorio incluye el `best.pt` final publicado para inferencia; no inventa métricas ni incluye todos los checkpoints de entrenamiento.

## Fuentes y atribución

Dataset **Mexican Bread**, JPIA, Roboflow Universe, 2024, [versión 3](https://universe.roboflow.com/jpia/mexican-bread/dataset/3), licencia publicada **CC BY 4.0**. Conservar atribución a JPIA al reutilizar los datos. Eliminar el SDK no elimina la atribución a la fuente. Las máscaras generadas con SAM son una transformación derivada, no etiquetas publicadas por JPIA.

Documentación primaria: [segmentación YOLO26](https://docs.ultralytics.com/tasks/segment/), [formato de etiquetas](https://docs.ultralytics.com/datasets/segment/), [entrenamiento y MPS](https://docs.ultralytics.com/modes/train/) y [SAM 2](https://docs.ultralytics.com/models/sam-2/). Consulta las licencias de dependencias y pesos antes de convertir el prototipo académico en un producto comercial.
