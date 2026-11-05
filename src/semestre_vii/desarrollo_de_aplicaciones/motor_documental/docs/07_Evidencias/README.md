# Evidencias

La evidencia deberá identificar fecha, comando o recorrido, entrada y resultado observado.

El [MVP conversacional de Luna](luna_mvp.md) tiene evidencia independiente: respuestas HTTP reales, seguimiento, citas, ausencia de evidencia, instalación sin clave y recorrido en Chrome de escritorio/móvil. No forma parte del benchmark anterior de recuperación sin LLM.

El [pulido anterior de interfaz](ui_pulida.md) registra recorridos de Nuxt UI 4.12, carga TXT/PDF/OCR, gestión, recuperación de errores, citas y móvil. Sus capturas se conservan como evidencia histórica.

El [cierre B5 de A*](b5_final/README.md) registra la interfaz actual: carga TXT y PDF mixto, OCR, fuente y original, vacío, errores reales y reintento. Incluye capturas anteriores y posteriores a dos correcciones de estado, junto con los gestos de arrastre todavía no observados.

El [arranque posterior al pulido](c2_ui_paquete.md) repite C2 desde el ZIP: volúmenes nuevos, seis contratos, Chrome y recuperación local sin credenciales de OpenAI.

| Comprobación | Estado |
| --- | --- |
| Rúbrica descargada y leída completa | Comprobado el 2 de noviembre de 2026. |
| Corpus ficticio | Seis PDF generados: dos digitales, dos escaneados y dos mixtos. |
| Extracción digital, OCR y PDF mixto | Doce páginas; seis nativas y seis OCR. Tesseract en Docker superó ocho controles de texto. |
| Embeddings locales y recuperación | Doce vectores de 384 dimensiones; seis consultas con archivo y página esperados en top 5. |
| CRUD, API key y prueba negativa | 78/78 comprobaciones HTTP correctas, incluido OCR por carga, baja lógica y negativos. |
| OpenAPI exportado de la API real | Once operaciones HTTP con el chat actual, ejemplos, schemas, seguridad y respuestas. |
| UI conectada, vacío y error | Chrome: consulta, original, carga mixta, edición, retiro, vacío, error y reintento verificados. |
| Arranque con Compose desde copia limpia | Copia independiente con volúmenes nuevos: seis documentos, doce páginas y doce fragmentos. |
| Auditoría independiente del código | Procesamiento y servicio completo revisados; ver `../revision_codigo.md`. |
| OneDrive, presentación y correo oficial | Pendiente; no enviados. |

No utilizar capturas de otras materias como evidencia. Los archivos de `tmp/pdfs/rubrica/` del repositorio pertenecen a una actividad anterior de otra materia.

## Recibos

- `recuperacion_tesseract.json` y `.npz`: ejecución completa en Docker, con configuración y fecha dentro del JSON.
- `docker_build.log`: construcción de la imagen del verificador.
- `verificacion_docker.log`: doce páginas procesadas, seis consultas y ocho controles de contenido.
- `ocr_inicial.json`: extracción anterior con una cláusula corrupta; se conserva para explicar la corrección.
- `recuperacion_rapidocr_medium.json`: alternativa con un control de contenido fallido.
- `recuperacion_rapidocr_small.json` y `.npz`: alternativa local reproducida con el código actual; siete controles de contenido aprobados.
- `negativas_extraccion.json`: cuatro entradas rechazadas, ejecutadas el 2 de noviembre de 2026 a las 13:57, America/Mexico_City.

La reproducción de Tesseract está en el [README](../../README.md). Ese recibo histórico corresponde a una imagen aislada de procesamiento. El servicio completo tiene evidencia separada en `servicio_http.json`, `postgres_objetos.txt`, `compose_estado.txt` y `recorrido_interfaz.md`.

Imagen verificada del primer incremento: `sha256:03c7162294b61f8049c3badc7e49e5913ac1a11afafed2f5ac3986daa43fee4d`. Ejecución Tesseract: 2 de noviembre de 2026, 14:12, America/Mexico_City. La emulación y lectura de fuentes está registrada en [emulacion.md](emulacion.md), y las negativas se reproducen con [negativas.md](negativas.md).

## Límites

Doce fragmentos y seis preguntas preparadas constituyen una comprobación pequeña. No acreditan fidelidad universal del OCR, respuesta a preguntas sin evidencia, seguridad de una API ni calidad sobre documentos reales.

## Servicio completo

`servicio_http.json` registra 78/78 comprobaciones correctas del 2 de noviembre de 2026 a las 14:40, America/Mexico_City. Incluye seis consultas híbridas con fuente conocida en top 5, ocho controles OCR, CRUD y rechazos seguros. No es una suite unitaria ni una evaluación sobre documentos reales.

`recorrido_interfaz.md` describe las acciones realizadas en Chrome y sus capturas. La API key no aparece en ellas. `postgres_objetos.txt` conserva tablas, índices, vista y conteos reales.

La copia independiente se documenta en `copia_independiente.md`. El BFF rechazó tres casos adicionales de origen/ruta; la clave no aparece en HTML y web no puede resolver PostgreSQL ni leer su contraseña.

## Corpus ampliado

`corpus_amplio/` contiene la medición de 240 documentos y 612 consultas: recuperación, controles por página, diagnóstico de citas, SQL y repetición del CRUD. La [guía](../11_guia_consultas.md) incluye preguntas verificadas y explica los límites. Esta medición amplía el experimento inicial de seis documentos y no sustituye sus recibos históricos.

La corrección autorizada de OCR intrapágina tiene recibos separados con sufijo `ocr_parcial`: comparación de las mismas 612 consultas, 480 páginas OCR, integridad de los 236 documentos no reindexados y 78/78 comprobaciones HTTP posteriores. `antes_ocr_parcial.json` y `retiros_ocr_parcial.json` conservan el estado y los identificadores anteriores. `corpus_ocr_intrapagina_corregido.png` muestra la cláusula antes omitida de `SIM0170`, página 4.

## Comparación con OpenAI

`comparacion_openai/` conserva resultados de las 612 búsquedas con los mismos originales, controles de contenido parseado de 16 documentos, seis negativas auxiliares y recibos de indexación. Las 612 respuestas completas quedan en los datos locales, identificadas por SHA256 y request ID en el TSV. Cuatro muestras completas permiten revisar los formatos desde la entrega. Ver [método, resultados y límites](../12_comparacion_openai.md).

`preparacion_openai.json` y `openai_store_preparado.png` son el estado anterior a la carga. `openai_store_indexado.png` muestra el Store después de procesar los archivos. El estado completed no acredita fidelidad OCR; el reporte distingue presencia de texto y recuperación de citas.
