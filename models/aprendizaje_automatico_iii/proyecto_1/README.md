# Modelo · Proyecto 1

Modelo final publicado para la caja asistida de panadería.

```text
yolo26s_mexican_bread_seg_best.pt
```

Corresponde al **`best.pt`** del fine-tuning de **YOLO26s-seg** con el dataset Mexican Bread.

Este directorio contiene únicamente el modelo final usado para inferencia. Los checkpoints intermedios, `last.pt`, datasets y resultados de entrenamiento permanecen fuera de Git.

El consumidor principal es:

```text
src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/aplicacion/run.py
```
