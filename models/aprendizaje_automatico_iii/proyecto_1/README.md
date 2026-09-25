# Modelo · Proyecto 1

Modelos finales publicados para la caja asistida de panadería.

```text
bread_detector_best.pt
yolo26s_mexican_bread_seg_best.pt
yolo26n_bread-v2_det/weights/best.pt
```

`bread_detector_best.pt` corresponde al fine-tuning de **YOLO26m-detect** con Bread Detector v2 y sigue siendo el predeterminado para inferencia. `yolo26s_mexican_bread_seg_best.pt` conserva el experimento anterior de **YOLO26s-seg** con Mexican Bread. La carpeta `yolo26n_bread-v2_det` contiene el primer peso publicado por la nueva cola.

Este directorio contiene sólo los checkpoints finales. Los checkpoints intermedios, `last.pt`, datasets y resultados de entrenamiento permanecen fuera de Git.

Los entrenamientos nuevos usan carpetas como `yolo26n_bread-v2_det/weights/best.pt` y
`yolo26m_mexican-v3_seg/weights/best.pt`. Sólo se publica `best.pt` mediante Git LFS;
los archivos temporales de cada corrida quedan locales.

El consumidor principal es:

```text
src/semestre_vii/aprendizaje_automatico_iii/proyecto_1/app.py
```
