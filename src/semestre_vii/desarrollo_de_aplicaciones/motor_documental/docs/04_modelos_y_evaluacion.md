# Modelos y evaluación

## Modelo actual

Modelo local `intfloat/multilingual-e5-small`, dimensión 384, revisión `614241f622f53c4eeff9890bdc4f31cfecc418b3`. Se normalizan los vectores y se usan los prefijos `passage:` y `query:` indicados por el modelo. GPT-6 Luna queda reservado para la segunda etapa.

La primera ejecución utiliza búsqueda exacta por similitud coseno sobre doce vectores en memoria; conserva los vectores y sus fuentes. Ese experimento se conserva como antecedente. El servicio actual ejecuta búsqueda persistente en PostgreSQL, con informe HTTP separado. Consultar el [informe Tesseract](07_Evidencias/recuperacion_tesseract.json).

## Comparación

Evaluar búsqueda textual, vectorial e híbrida sobre el mismo corpus y las mismas consultas. Conservar los primeros resultados, documento y página esperados, tiempo y configuración.

Casos mínimos: devolución del depósito, penalización por salida anticipada, reparaciones autorizadas, anticipo de compraventa y devolución del apartado. Incluir preguntas sin respuesta en el corpus.

## Extracción

Revisar PDF digital, escaneado y mixto. Confirmar método por página y recuperación de importes, plazos y folios. Una extracción no vacía puede contener errores de OCR, por lo que debe compararse con el original.

## Criterios

- Encontrar la evidencia correcta entre los primeros cinco resultados.
- Mantener archivo y página correctos.
- Registrar fallas y limitaciones sin presentarlas como resultados satisfactorios.
- Separar precisión de recuperación de calidad de una respuesta generada, que todavía no se mide.

Un reranker y un índice HNSW se incorporarán únicamente si las mediciones justifican su costo. El experimento actual no acredita equivalencia con OpenAI File Search.

## Limitaciones observadas

La configuración OCR inicial recuperó la página correcta, pero corrompió una cláusula sobre mobiliario. Se conserva [su salida](07_Evidencias/ocr_inicial.json). RapidOCR mediano también tuvo un control fallido, registrado en [su informe](07_Evidencias/recuperacion_rapidocr_medium.json).

Tesseract `spa+eng` en Docker superó los ocho controles de texto del corpus. En seis consultas, la fuente esperada apareció entre los primeros cinco resultados; cinco aparecieron primero y una, segunda. Estos controles son una muestra limitada, no una garantía de fidelidad de todas las palabras ni de recuperación en un archivo inmobiliario grande.

La heurística de 60 caracteres distingue las páginas del corpus. Todavía no se acredita una página con encabezado digital largo y cuerpo escaneado. Las preguntas sin respuesta y la comparación textual/híbrida también siguen pendientes.
