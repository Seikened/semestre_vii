# Documentación · Proyecto 1

Este directorio conserva las decisiones y resultados del proyecto, no sólo el estado final del código.

## Experimentos

- [Experimento 1 · Mexican Bread + YOLO26s-seg](01_experimento_segmentacion_mexican_bread.md)
  - Qué entrenamos.
  - Qué funcionó dentro del dataset.
  - Qué falló al probar imágenes y cámara reales.
  - Por qué grayscale mejoró la inferencia sin resolver la clasificación.

- [Plan 2 · Bread Detector + YOLO26m-detect](02_plan_detector_pan.md)
  - Nuevo objetivo.
  - Dataset elegido.
  - Configuración preparada para la GPU de la escuela.
  - Criterios que usaremos para decidir si realmente generaliza.

La regla para los siguientes experimentos es sencilla: **mAP alto en validación no basta**. También se prueban fotos externas, cámara en vivo y escenas sin pan.
