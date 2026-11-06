# Revisión independiente del primer incremento

Revisión del 2 de noviembre de 2026 por un subagente independiente. La revisión no sustituye los recibos de ejecución.

| Hallazgo | Prioridad | Decisión | Evidencia |
| --- | --- | --- | --- |
| Imagen renombrada como PDF aceptada por PyMuPDF | P2 | Corregido con `documento.is_pdf` | Negativa `imagen.pdf` produce `DOCUMENTO_FORMATO`. |
| Una cláusula corrupta pese a encontrar la página correcta | P2 | Conservar salida inicial; verificar Tesseract en Docker frente a RapidOCR | `ocr_inicial.json`, variante mediana y ocho controles aprobados en `recuperacion_tesseract.json`. |
| Orden global de fragmentos frente a orden por página del DDA | P3 | Corregido, reiniciar orden en cada página | `backend/app/modelos.py`. |
| Motor ONNX usado por OCR no declarado en dependencias | P2 | Añadir `onnxruntime` y repetir desde el entorno del servicio | `backend/pyproject.toml`, `uv.lock` y ejecución posterior. |
| Diagramas sin puntas de flecha en el render SVG | P3 | Dibujar las puntas explícitamente y separar el texto de las líneas | Fuentes draw.io y PNG regenerados. |

El incremento de procesamiento y demostración tiene 576 líneas Python, 26 sobre las 550 estimadas, por la comparación de motores OCR y sus controles. El generador de diagramas y Dockerfile se contabilizan aparte. No se agregaron tablas, endpoints, acceso ni un LLM durante esta primera porción.

La última pasada pidió conservar por separado las salidas de cada motor. El verificador ahora utiliza un nombre específico por motor y tamaño; ejecutar RapidOCR no reemplaza el informe de Tesseract.

## Ampliación del servicio

Fernando autorizó PostgreSQL, CRUD, API key, Nuxt y Compose sin LLM. La segunda revisión independiente no detectó nuevos bloqueos tras corregir:

- Separar la API key del volumen de contraseña PostgreSQL. Web solo tiene la clave que utiliza el BFF y no participa en la red de datos.
- Invalidar respuestas y errores tardíos del panel documental; bloquear su cierre durante guardado.
- Añadir ejemplos y respuestas a OpenAPI, salud 503 y formatos de descarga PDF/TXT.
- Nombrar correctamente la búsqueda textual y revisar contraste y posición de resultados.

Evidencia: 78/78 comprobaciones HTTP, ocho controles OCR y seis consultas híbridas con fuente esperada en top 5. Chrome verificó consulta, original, colección, carga mixta, edición, retiro, vacío, error y reintento. La copia independiente creó sus propios volúmenes y el corpus completo. Ver recibos en `07_Evidencias/`. No se añadieron suites unitarias ni se conectó Luna.

Presupuesto: 1469 líneas de aplicación y configuración, dentro del intervalo aprobado de 1200 a 1600. Se excluyen locks, documentación, corpus y scripts de demostración o verificación. Cada módulo Python conserva menos de 600 líneas.

## Evaluación ampliada

La auditoría independiente comprobó 240 hashes, 1640 páginas lógicas y la pertenencia de las 68 citas a sus cláusulas fuente. Antes de la medición final se corrigió el alcance de las consultas, la duplicación de anclas genéricas, la conservación de tiempos de ingesta, el registro de envíos pendientes, la validación de versión y la identidad del manifiesto.

Se conservaron los fallos de extracción y fragmentación. La medición inicial usa 612 consultas, captura el hash de los mismos bytes cargados y separa preguntas libres, naturales con folio y precisas. El núcleo permaneció sin cambios durante esa medición. El piloto de OCR parcial se conservó por separado antes de autorizar su aplicación.

## Corrección autorizada del OCR intrapágina

Fernando autorizó aplicar y verificar el parche acotado de `backend/app/extraccion.py`. La revisión independiente posterior no encontró discrepancias bloqueantes en el cambio ni en la documentación.

La auditoría confirmó coincidencia exacta con el parche aprobado, los mismos 240 originales y 612 consultas, y únicamente las 16 páginas previstas con cambio de método. Verificó los hashes de los cuatro originales reindexados, las 16 páginas nativas idénticas y la conservación de los 16 encabezados digitales dentro de las páginas con OCR parcial.

No hubo pérdidas de página o cita literal en top 5. La única variación adversa de posición fue de tercero a cuarto en `SIM0017-C13`, consulta precisa vectorial, documentada en la evaluación. Los recibos posteriores conservan 78/78 comprobaciones HTTP, ocho controles OCR y seis fuentes esperadas del corpus inicial en top 5.

La evidencia posterior tiene sufijo `ocr_parcial` dentro de `07_Evidencias/corpus_amplio/`; la línea base permanece intacta. La auditoría mantuvo explícitas las limitaciones de OCR, fragmentación, ranking y falta de abstención. El resultado 68/68 de página primera corresponde a consultas precisas textuales, no a fidelidad universal del OCR.

## Comparación externa autorizada

El experimento opcional con OpenAI conserva los mismos originales y preguntas, sin modificar la aplicación ni sus dependencias. La revisión del cargador confirmó bytes, hashes y checkpoints; antes de buscar se corrigieron la conservación del snapshot inicial y la identidad completa de respuestas reutilizadas.

La auditoría final recalculó las 612 mediciones y las 13 filas resumidas sin diferencias. Confirmó 612 request IDs únicos, hashes de respuestas, correspondencia entre archivo e identificador, 240 archivos completed y configuración estática 800/400. Los contenidos de los 16 documentos con casos y las seis peticiones auxiliares son coherentes con el informe.

Se mantuvo una precisión metodológica: contenido parseado no equivale a fronteras de pasajes efectivos, por lo que una cita ausente de top 5 no se atribuye automáticamente solo a ranking. OpenAI usa la misma configuración en tres repeticiones, no tres modos equivalentes. Los números de página de búsqueda quedan sin equivalencia directa y no se afirma superioridad general. Ver `12_comparacion_openai.md`.
