# Plan 2 · Bread Detector + YOLO26m-detect

## Nuevo objetivo

Primero resolver de forma robusta:

1. ¿Hay panes?
2. ¿Dónde está cada pieza?
3. ¿Qué tipo de pan es?
4. ¿Cuántas instancias hay por clase?

Para esto no necesitamos una máscara exacta. Object detection entrega una caja y una clase por instancia, suficiente para identificar y contar panes en un frame.

## Dataset

Fuente: Bread Detector v2 de Roboflow Universe  
https://universe.roboflow.com/breaddetector/bread-detector/dataset/2

Datos publicados para v2:

- 4,672 imágenes.
- 15 clases.
- 4,281 train.
- 208 validation.
- 183 test.
- Licencia CC BY 4.0.
- Tarea: Object Detection.
- Exportación disponible directamente en formato YOLO26.

Clases: croissant, baguette, binangkal, bonete, cornbread, ensaymada, flatbread, kalihim, monay, pandesal, sourdough, spanish-bread, wheat-bread, white-bread y whole-grain-bread.

### Limitaciones conocidas

No lo tratamos como dataset perfecto:

- La versión 2 fue preprocesada con stretch a 256×256.
- Tiene augmentations generadas por Roboflow.
- Validation y test son relativamente pequeños.
- No contiene nuestras clases mexicanas principales.
- Todavía necesitaremos pruebas externas y escenas negativas propias.

Su función es enseñarnos primero una representación más general de **tipos de pan en object detection**.

## Arquitectura del siguiente entrenamiento

Modelo inicial:

`yolo26m.pt`

Configuración preparada:

- Task: detect.
- Fine-tuning completo; `freeze=None`.
- 100 épocas máximas.
- Early stopping: 25 épocas sin mejora.
- `imgsz=640`.
- `batch=-1`: Ultralytics calcula el batch para ~60% de la VRAM en CUDA.
- `multi_scale=0.25`: con base 640 varía el tamaño de entrada por lote aproximadamente entre 480 y 800.
- Color: se conserva; no se fuerza grayscale.
- Checkpoint cada 10 épocas.
- Seed 42.
- Pesos iniciales preentrenados de YOLO26m.

La elección de YOLO26m busca más capacidad que el YOLO26s anterior sin saltar todavía a YOLO26x.

## Ejecución en la escuela

Desde la raíz del repo:

```bash
git pull
uv sync
```

### 1. Descargar e importar Bread Detector

```bash
uv run src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/utils/download_bread_detector.py
```

Se abrirá Roboflow en el navegador. Elegir **Download zip to computer**. El script detecta el ZIP, lo importa y valida las etiquetas.

El dataset queda localmente en:

```text
data/aprendizaje_automatico_iii/proyecto_1/datasets/bread_detector/
```

No se versiona en Git.

### 2. Entrenar

```bash
uv run src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/entrenamiento/train_detector.py
```

Los runs quedan en:

```text
data/aprendizaje_automatico_iii/proyecto_1/deteccion/runs/
```

El script conserva `best.pt`, `last.pt`, checkpoints periódicos, gráficas y `experimento_detector.json`.

## Cómo juzgaremos el resultado

No volveremos a declarar éxito sólo por una matriz de confusión bonita.

Después del entrenamiento se revisará:

- mAP/precision/recall en validation y test.
- Fotos de panes que no pertenecen al dataset.
- Cámara en vivo.
- Objetos que no sean pan.
- Diferentes fondos, escalas, distancias e iluminación.
- Conteo correcto de varias instancias en el mismo frame.

Si el detector generaliza bien, el siguiente paso será especializarlo con panes mexicanos y agregar negativos propios. Si hace falta máscara exacta, recuperaremos segmentación después de tener una representación de detección más robusta.
