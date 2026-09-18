# Datasets candidatos · decisión experimental

No existe un único dataset que cubra perfectamente nuestro objetivo. La estrategia es usar cada fuente para lo que aporta y evaluar generalización con imágenes externas.

## Prioridad actual

### 1. Bread Detector v2 — siguiente experimento

**Uso:** base de object detection para aprender tipos de pan más variados.

- Tarea: Object Detection.
- Versión 2: 4,672 imágenes.
- 15 clases de pan.
- Tiene un modelo YOLOv8s publicado con mAP@50 de 92.2%, útil como señal de que la taxonomía es aprendible.
- Licencia: CC BY 4.0.
- Fuente: https://universe.roboflow.com/breaddetector/bread-detector

**Por qué va primero:** coincide con la pregunta que queremos resolver ahora: dónde está cada pan, qué tipo es y cuántos hay.

**Riesgos:** sus clases no son mexicanas y el dataset tampoco garantiza generalización al entorno final. Por eso se probará con cámara, fotos externas y negativos.

### 2. Mexican Bread — especialización mexicana

**Uso:** conservar las clases mexicanas que realmente nos interesan: bolillo, concha, telera, dona, oreja, etc.

Fue nuestro primer experimento con YOLO26s-seg. Logró métricas internas muy altas, pero mostró domain shift fuerte en cámara e imágenes externas: color, escala y objetos no-pan afectaron mucho la clasificación.

**Decisión:** no descartarlo. Usarlo después para especializar un detector que ya tenga una representación más robusta de panes.

Fuente: https://universe.roboflow.com/jpia/mexican-bread

### 3. FoodSeg103 — contexto real y diversidad

**Uso potencial:** mejorar representación de escenas reales de comida y contexto.

- 7,118 imágenes.
- 40,275 anotaciones.
- 103 clases.
- Anotaciones poligonales.
- Contiene la clase genérica `bread`, pero no separa tipos de pan como necesitamos.
- Fuente: https://huggingface.co/datasets/pictograph/foodseg103

**Valor:** mucha más diversidad visual y alimentos/contexto alrededor.

**Limitación:** sirve mejor para aprender contexto o segmentación genérica de comida que para distinguir concha vs bolillo.

### 4. full-bakery — alternativa de segmentación

**Uso potencial:** volver a instance segmentation si la máscara exacta aporta valor.

- Aproximadamente 1.6k imágenes.
- 16 clases.
- Instance Segmentation.
- Incluye `bread`, `baguette`, `bun`, `loaf`, `toast`, pero también atributos como `burned`, `cooked`, `white`, `black` y `no_seeds`.
- Fuente: https://universe.roboflow.com/university-qjltn/full-bakery

**Limitación:** la taxonomía mezcla tipo de pan con estado/apariencia, por lo que no encaja tan limpio con nuestro objetivo.

### 5. Bread101 — complemento pequeño

**Uso potencial:** benchmark o complemento de panes distintos.

- ~155 imágenes.
- 5 categorías de panadería francesa.
- Bounding boxes + instance segmentation.
- Fuente: https://www.kaggle.com/datasets/alexdelaveau/bread101

**Limitación:** demasiado pequeño para usarlo como base principal.

## Estrategia elegida

```text
Bread Detector
      ↓
YOLO26m-detect
      ↓
pruebas externas + negativos
      ↓
Mexican Bread / imágenes propias
para especializar clases mexicanas
      ↓
segmentación sólo si la aplicación
realmente necesita máscaras exactas
```

La selección puede cambiar si un experimento demuestra que otro dataset generaliza mejor. Se documentará el resultado de cada intento en esta carpeta.
