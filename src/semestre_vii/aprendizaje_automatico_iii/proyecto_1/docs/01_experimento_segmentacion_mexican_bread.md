# Experimento 1 · Mexican Bread + YOLO26s-seg

## Objetivo

Reconocer panes mexicanos por instancia y obtener una máscara para cada pieza.

## Entrenamiento realizado

Se hizo fine-tuning completo de `yolo26s-seg.pt`; no se congeló únicamente la cabeza. El backbone, neck y heads participaron en la optimización.

Configuración principal:

- YOLO26s-seg preentrenado.
- 50 épocas.
- `imgsz=640`.
- `batch=4`.
- CUDA en una NVIDIA RTX 4000 Ada Generation.
- Duración aproximada: 1.309 h.
- 11 clases: Bolillo, Concha, Cuernito, Dona, Mantecada, Oreja, Pinguino, Rebanada, Reja, Telera y Torta.

El run terminó con métricas internas muy altas. Las máscaras alcanzaron aproximadamente mAP50 ≈ 0.987 y mAP50-95 ≈ 0.956.

## Qué aprendimos

Las etiquetas poligonales sí son etiquetas válidas de instance segmentation. Los colores que aparecen en los mosaicos de Ultralytics son sólo una visualización de las máscaras.

El problema apareció fuera del dominio del dataset:

- A color, el modelo casi no detectaba imágenes externas.
- Convertir la entrada a grayscale mejoró muchísimo la detección.
- Con una concha externa, cambiar la escala también alteró radicalmente el resultado.
- Se observaron falsos positivos con confianza alta: cara → Pinguino, portavasos → Mantecada.
- En panes reales/externos, la localización mejoró antes que la clasificación correcta.

La conclusión no es que YOLO-seg esté roto. La conclusión es que **el modelo aprendió muy bien el dominio visual del dataset, pero generalizó mal hacia escenas reales distintas**.

## Por qué no seguimos aumentando épocas

Las curvas y métricas del dataset ya habían convergido bien. Más épocas sobre la misma distribución probablemente reforzarían los mismos sesgos en vez de resolver color, escala, fondos y falsos positivos.

## Qué conservamos

El checkpoint sigue siendo útil como evidencia y referencia:

`models/aprendizaje_automatico_iii/proyecto_1/yolo26s_mexican_bread_seg_best.pt`

No se elimina el experimento de segmentación. Simplemente dejamos de usarlo como única estrategia para responder primero una pregunta más básica: **qué panes hay, dónde están y cuántos hay**.
