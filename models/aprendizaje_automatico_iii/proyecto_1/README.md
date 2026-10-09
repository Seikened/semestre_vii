# Modelos · Proyecto 1

Checkpoints finales publicados para la caja asistida de panadería.

## Catálogo disponible

La rama `main` conserva dos checkpoints previos por compatibilidad:

```text
bread_detector_best.pt
yolo26s_mexican_bread_seg_best.pt
```

Además publica la matriz actual de **10 modelos YOLO26**, con cinco tamaños por dataset y tarea:

```text
yolo26n_bread-v2_det/weights/best.pt
yolo26s_bread-v2_det/weights/best.pt
yolo26m_bread-v2_det/weights/best.pt
yolo26l_bread-v2_det/weights/best.pt
yolo26x_bread-v2_det/weights/best.pt

yolo26n_mexican-v3_seg/weights/best.pt
yolo26s_mexican-v3_seg/weights/best.pt
yolo26m_mexican-v3_seg/weights/best.pt
yolo26l_mexican-v3_seg/weights/best.pt
yolo26x_mexican-v3_seg/weights/best.pt
```

Los nombres siguen la convención `yolo26{tamano}_{dataset}_{tarea}`:

- `n`, `s`, `m`, `l`, `x`: tamaño del modelo.
- `bread-v2_det`: Bread Detector v2, **object detection**.
- `mexican-v3_seg`: Mexican Bread v3, **instance segmentation**.

`bread_detector_best.pt` corresponde al detector mediano previo de Bread Detector v2. `yolo26s_mexican_bread_seg_best.pt` conserva el segmentador previo de Mexican Bread. Los checkpoints con la convención nueva son las corridas publicadas por la cola de entrenamiento.

Este directorio conserva únicamente `best.pt`. Los checkpoints intermedios, `last.pt`, datasets y resultados de entrenamiento permanecen fuera de Git. Los pesos finales se versionan con Git LFS.

## Consumo desde la aplicación

El consumidor principal es:

```text
src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/app.py
```

`app.py` selecciona el modelo mediante el dataset y el tamaño:

```bash
uv run src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/app.py bread-v2 m
uv run src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/app.py mexican-v3 s
```

Sin argumentos usa `DATASET="bread-v2"` y `TAMANO="x"`, que apuntan a `yolo26x_bread-v2_det/weights/best.pt`. Ambos valores pueden ajustarse al inicio del archivo.

También puede consumirse cualquier checkpoint explícitamente desde la CLI del proyecto:

```bash
uv run python -m semestre_vii.aprendizaje_automatico_iii.proyecto_1 caja \
  --source 0 \
  --model models/aprendizaje_automatico_iii/proyecto_1/yolo26m_bread-v2_det/weights/best.pt
```

Para segmentación se usa exactamente la misma frontera:

```bash
uv run python -m semestre_vii.aprendizaje_automatico_iii.proyecto_1 caja \
  --source data/aprendizaje_automatico_iii/proyecto_1/concha.jpg \
  --model models/aprendizaje_automatico_iii/proyecto_1/yolo26s_mexican-v3_seg/weights/best.pt \
  --sin-ventana
```

## Consumo desde Python

La frontera recomendada dentro del proyecto es `ModeloYOLO`, porque normaliza detección y segmentación al mismo contrato `Lectura`:

```python
from pathlib import Path

import cv2

from semestre_vii.aprendizaje_automatico_iii.proyecto_1.modelo.yolo import ModeloYOLO

pesos = Path(
    "models/aprendizaje_automatico_iii/proyecto_1/"
    "yolo26m_bread-v2_det/weights/best.pt"
)
imagen = cv2.imread("bandeja.jpg")

modelo = ModeloYOLO(pesos, device="auto", conf=0.5, imgsz=640)
lectura = modelo.predecir(imagen)

for instancia in lectura.instancias:
    print(instancia.clase, instancia.confianza, instancia.poligono)
```

Para un checkpoint `det`, el polígono normalizado por la frontera corresponde a las cuatro esquinas de la caja. Para un checkpoint `seg`, conserva el contorno devuelto por la máscara. Así, el código consumidor no necesita una ruta distinta para cada tarea.

Si un consumidor necesita la salida nativa de Ultralytics puede cargar directamente el mismo `best.pt`; no debe combinarlo con pesos base.

## Elección del modelo

Los sufijos `n/s/m/l/x` representan distintas capacidades de YOLO26, no una clasificación de calidad del proyecto. Elegir el checkpoint con las métricas de validación del experimento y el hardware objetivo. No asumir que el modelo más grande es automáticamente el mejor para el caso real.
