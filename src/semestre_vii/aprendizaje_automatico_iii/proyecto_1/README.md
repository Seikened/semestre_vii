# Proyecto 1 · Caja asistida de panadería

**Aprendizaje Automático III — Semestre VII.** Segmentar cada pan de una bandeja, clasificarlo, contar las instancias visibles y estimar un ticket en MXN. No procesa pagos ni es una caja autónoma certificada.

La red aprende **dónde está cada pan y qué clase es**. `precios.py` decide su precio; `cobro.py` calcula `cantidad × precio`. Cambiar un precio no requiere reentrenar. El ejemplo usa precios ficticios y centavos enteros: dos conchas de $12, un bolillo de $5 y una dona de $15 suman **$44 MXN**.

## Arquitectura

```text
proyecto_1/
├── __main__.py       # CLI por etapas, sin ejecutar nada al importar
├── configuracion.py  # Rutas y selección CPU / MPS / CUDA
├── datos.py          # YAML, anotaciones, conteos y auditoría
├── preparacion.py    # Descarga; propuestas SAM sólo cuando hay cajas
├── entrenamiento.py # Fine-tuning y evaluación técnica + de negocio
├── vision.py         # Adaptador de Ultralytics a instancias explícitas
├── precios.py        # Única fuente de verdad de precios ficticios
├── cobro.py          # Ticket y estabilidad, sin dependencias de visión
├── interfaz.py       # Máscaras, desglose y capturas JPG + JSON
└── aplicacion.py     # Foto, video o cámara; orquestación del recorrido
```

Los datos originales, derivados, pesos, configuraciones, experimentos y capturas van a `data/aprendizaje_automatico_iii/proyecto_1/`, fuera de `src` y excluidos de Git. Las pruebas están en `tests/proyecto_1/`. No hay base de datos, API web, servicios vacíos ni jerarquías de clases innecesarias.

## Antes de entrenar: este dataset aparece como detección

Fuente: [Mexican Bread de JPIA](https://universe.roboflow.com/jpia/mexican-bread). La página pública consultada el 17 de septiembre de 2026 indica **Object Detection**. Su versión **3** publica 5,964 imágenes: 4,173 train, 1,192 valid y 599 test; no confundirlas con las 9,330 imágenes del proyecto completo.

Las once clases publicadas son Bolillo, Concha, Cuernito, Dona, Mantecada, Oreja, Pinguino, Rebanada, Reja, Telera y Torta. El código **lee los IDs reales desde `data.yaml`**, no presupone que su orden sea el del diccionario de precios.

El nombre del proyecto ni un contorno dibujado en la web bastan para saber qué contiene una exportación. **`inspeccionar` revisa cada línea real del archivo de etiquetas**:

```text
0 0.50 0.50 0.20 0.30                      # caja: clase + centro/ancho/alto
0 0.10 0.10 0.80 0.10 0.80 0.80 0.10 0.80 # polígono: clase + puntos
```

YOLO26 **de segmentación** necesita polígonos por instancia; cambiar el nombre del checkpoint no inventa etiquetas. Si la exportación ya trae polígonos, se conservan. Si trae cajas, `preparar --con-sam` usa cada caja como prompt para SAM 2.1 Tiny y produce **propuestas de máscaras**, conservando la clase original. **Nunca convierte simplemente cuatro esquinas de una caja en ground truth de segmentación.**

Las propuestas pueden estar mal: fondo incluido, panes unidos, bordes cortados o agujeros perdidos. Revisar y corregir con una herramienta de anotación; para la evaluación final conviene disponer de máscaras revisadas por una persona. Las máscaras propuestas quedan identificadas en `procedencia.json` y su uso requiere `--aceptar-pseudoetiquetas`. Este flag reconoce su procedencia, **no certifica su calidad**.

## Instalación en el repositorio

Desde la raíz de `semestre_vii`:

```bash
uv add ultralytics opencv-python pyyaml
uv sync
uv run python -m semestre_vii.aprendizaje_automatico_iii.proyecto_1 --help
```

Se conserva el Python y las dependencias ya fijadas por el repositorio. `uv add` registra las dependencias nuevas y actualiza el lockfile en tu equipo; no se incluyó un lockfile inventado. Usa la variante de OpenCV con interfaz, no `opencv-python-headless`, para abrir la cámara.

Para abreviar los comandos siguientes, define este alias **sólo en la terminal actual**:

```bash
alias pan='uv run python -m semestre_vii.aprendizaje_automatico_iii.proyecto_1'
```

`pan` es sólo una abreviatura del comando anterior, no otro paquete.

## Descargar e inspeccionar

```bash
uv run --with roboflow python -m semestre_vii.aprendizaje_automatico_iii.proyecto_1 descargar
pan inspeccionar --verificar-fugas
```

El SDK de descarga se añade únicamente al entorno de ese comando; no es necesario durante entrenamiento ni inferencia. `descargar` solicita tu API key en una entrada oculta, o usa `ROBOFLOW_API_KEY` del entorno. **No envíes la clave por chat ni la guardes en el repositorio.** No consume entrenamiento alojado de Roboflow ni utiliza su endpoint de predicción: descarga los datos para trabajar localmente.

También puedes descargar el ZIP de la versión 3 en formato YOLO desde Universe y extraerlo. La ruta por defecto debe quedar así:

```text
 data/aprendizaje_automatico_iii/proyecto_1/roboflow/
 ├── data.yaml
 ├── train/images/ + train/labels/
 ├── valid/images/ + valid/labels/
 └── test/images/  + test/labels/
```

El exportador `yolov8` describe el **formato de anotación**, no obliga a entrenar YOLOv8: el modelo de este proyecto es YOLO26-seg. Una exportación sólo de cajas seguirá siendo sólo de cajas. Usa `--data /ruta/a/data.yaml` para otra ubicación; este cargador admite carpetas YOLO estilo Roboflow, no COCO JSON ni listas de imágenes.

La auditoría informa imágenes, cajas, polígonos y cantidades por clase. Rechaza clases inválidas, coordenadas no finitas, polígonos degenerados y etiquetas faltantes. Los negativos deben tener un `.txt` vacío explícito. `--verificar-fugas` detecta archivos de imagen idénticos entre splits; **no detecta por sí solo fotos casi idénticas o sesiones de captura compartidas**.

## Preparar y revisar

Con polígonos existentes:

```bash
pan preparar
```

Con cajas:

```bash
pan preparar --con-sam --device mps
```

Esta operación procesa la exportación completa y SAM necesita descargar sus pesos en la primera ejecución. No se activa sin `--con-sam`. No sobrescribe datos: si `segmentado` ya existe, usa otro `--destino`. Si una propuesta es inválida, se detiene y limpia solamente su carpeta temporal.

Revisar ejemplos de cada split:

```bash
pan revisar --split train --destino data/aprendizaje_automatico_iii/proyecto_1/revision/train
pan revisar --split val --destino data/aprendizaje_automatico_iii/proyecto_1/revision/val
pan revisar --split test --destino data/aprendizaje_automatico_iii/proyecto_1/revision/test
```

Se exportan 20 ejemplos distribuidos a lo largo del split. `--limite 0` exporta todos. Estas imágenes son **anotaciones superpuestas, no predicciones de YOLO**; revisar veinte ejemplos no equivale a revisar todo el dataset. Para corregir máscaras utiliza tu herramienta de anotación y vuelve a exportarlas. La preparación conserva la separación train/val/test original.

Cuando existe `segmentado/data.yaml`, los comandos posteriores lo eligen por defecto. Para otros destinos pasa `--data` explícitamente.

## Entrenar YOLO26-seg

Primero una prueba de ejecución, **no un modelo utilizable para cobrar**:

```bash
pan entrenar --device mps --epochs 1 --batch 2 --fraction 0.02 --aceptar-pseudoetiquetas
```

Después del chequeo, un primer experimento completo:

```bash
pan entrenar --device mps --epochs 30 --batch 4 --tamano n --aceptar-pseudoetiquetas
```

Si no usaste SAM, omite `--aceptar-pseudoetiquetas`. El programa se niega a entrenar segmentación con cajas. Empieza con **`yolo26n-seg.pt`**; puedes comparar `--tamano s` después de obtener una línea base. Los pesos iniciales son preentrenados, **no conocen automáticamente las once clases mexicanas**: se adaptan durante el entrenamiento.

`--device auto` selecciona CUDA, MPS o CPU según disponibilidad. En tu Mac puedes usar `mps`; ante falta de memoria reduce `--batch 2` o `--batch 1`. `--device cpu` es una alternativa funcional. Se usa `workers=0`, `cache=False` y semilla 42; la semilla no garantiza igualdad bit a bit entre diferentes dispositivos/versiones.

Cada ejecución crea un directorio propio en `runs/`. Ultralytics guarda pérdidas, métricas y `weights/best.pt` / `weights/last.pt`; el proyecto añade `experimento.json` con configuración, clases, procedencia y versiones. `ultimo_modelo.txt` apunta al último `best.pt` producido correctamente, incluso si era una prueba de una época: **no implica que ese checkpoint sea bueno**. Usa `--model` para elegir otro.

## Abrir la caja

```bash
pan caja --source 0 --device mps
```

Una foto o un video:

```bash
pan caja --source /ruta/bandeja.jpg --device mps
pan caja --source /ruta/video.mp4 --device mps
pan caja --source /ruta/bandeja.jpg --sin-ventana
```

Se dibuja una máscara por pan y se muestra clase, confianza, piezas, subtotales, total, FPS del recorrido e inferencia en milisegundos. **Espacio** pausa el video; **S** guarda una estimación JPG + JSON; **Q** o Escape cierra. Las fotos se guardan automáticamente. `--source 1` selecciona otra cámara y `--conf 0.65` cambia el umbral. En macOS debes conceder permiso de cámara a la terminal/IDE que lance Python.

**Se cuenta lo visible en el fotograma actual**, no se suman observaciones entre frames. La misma concha durante diez segundos sigue siendo una concha; al vaciar la bandeja, el total vuelve a cero. La estabilidad sólo indica que el conteo por clase se repitió cinco frames: **no demuestra que sea correcto** ni conserva detecciones antiguas. No es un contador de paso ni utiliza tracking acumulativo.

El catálogo usa nombres normalizados, no IDs rígidos. Una clase sin precio no se cobra como cero: el dominio invalida el total y la aplicación exige corregir el catálogo/modelo. El checkpoint COCO genérico no se acepta como si fuera uno entrenado para esta panadería. El límite operativo actual es 100 instancias por imagen; no es un sistema para montones de cientos de panes.

## Evaluar la problemática, no sólo una gráfica bonita

Mientras eliges parámetros, usa validación:

```bash
pan evaluar --split val --device mps --aceptar-pseudoetiquetas
```

Cuando fijes el modelo y el umbral con validación, usa test una sola vez como evaluación final:

```bash
pan evaluar --split test --device mps --aceptar-pseudoetiquetas
```

El reporte incluye mAP50–95 de cajas y máscaras, proporción de **canastas con todas las cantidades por clase correctas**, error absoluto de conteo por clase y error absoluto medio del importe en MXN. Se guardan también resultados por imagen. El mAP utiliza la evaluación estándar de Ultralytics; las métricas de negocio usan `--conf`, 0.50 por defecto. Un total coincidente no garantiza clases correctas: dos panes con igual precio podrían intercambiarse; por eso se mide también la canasta completa.

Si val/test tienen máscaras generadas por SAM, el mAP de máscaras mide concordancia con esas **pseudoetiquetas**, no calidad contra segmentación humana. El reporte lo identifica explícitamente. Las cantidades se comparan contra las clases de las anotaciones, que también deben auditarse.

Como objetivo experimental propuesto (no resultado obtenido), podemos exigir al menos 95% de canastas exactas y un error medio del importe menor a $1 MXN en bandejas nuevas. Cambia esos criterios según el riesgo tolerable. Mide además canastas vacías, objetos ajenos, iluminación distinta, panes parcialmente tapados y varios del mismo tipo.

La versión 3 publicada filtra imágenes sin anotaciones. Añadir ejemplos negativos y fotografías reales de tu cámara es importante antes de sacar conclusiones operativas. Divide nuevas capturas **por sesión o bandeja antes de aumentar datos**, no poniendo frames vecinos en train y test. Un pan completamente tapado no es observable; tampoco debe venderse la confianza del modelo como una probabilidad calibrada de cobro correcto.

## Pruebas y alcance verificado

```bash
uv run pytest tests/proyecto_1 -q
```

Las pruebas ejercitan cálculo real, validación de datos, transformación, exportación y flujo foto/cámara. SAM, YOLO y captura de cámara se **simulan explícitamente** en las pruebas de integración. No sustituyen una corrida con pesos reales y datos de Roboflow. El proyecto no incluye `best.pt` entrenado ni métricas de precisión inventadas.

## Fuentes y atribución

Dataset **Mexican Bread**, JPIA, Roboflow Universe, 2024, [versión 3](https://universe.roboflow.com/jpia/mexican-bread/dataset/3), licencia publicada **CC BY 4.0**. Conservar atribución a JPIA al reutilizar los datos. Las máscaras creadas con SAM son una transformación derivada, no etiquetas publicadas por JPIA.

Documentación primaria: [segmentación YOLO26](https://docs.ultralytics.com/tasks/segment/), [formato de etiquetas](https://docs.ultralytics.com/datasets/segment/), [entrenamiento y MPS](https://docs.ultralytics.com/modes/train/), [SAM 2](https://docs.ultralytics.com/models/sam-2/) y [exportación Roboflow](https://docs.roboflow.com/datasets/versions/dataset-versions/exporting-data). Consulta las licencias de las dependencias y pesos antes de convertir el prototipo académico en un producto comercial.
