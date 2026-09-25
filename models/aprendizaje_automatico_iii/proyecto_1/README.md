# Modelo · Proyecto 1

Modelos finales publicados para la caja asistida de panadería.

```text
bread_detector_best.pt
yolo26s_mexican_bread_seg_best.pt
```

`bread_detector_best.pt` corresponde al fine-tuning de **YOLO26m-detect** con Bread Detector v2 y es el predeterminado para inferencia. `yolo26s_mexican_bread_seg_best.pt` conserva el experimento anterior de **YOLO26s-seg** con Mexican Bread.

Este directorio contiene sólo los checkpoints finales. Los checkpoints intermedios, `last.pt`, datasets y resultados de entrenamiento permanecen fuera de Git.

El consumidor principal es:

```text
src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/app.py
```
