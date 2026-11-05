# Comparación con OpenAI Retrieval

Fernando autorizó cargar los mismos documentos ficticios y repetir las mismas consultas mediante una clave temporal del proyecto Epok. El experimento es opcional y separado del servicio local; no conecta el agente conversacional ni cambia la arquitectura de la aplicación.

## Entradas y condiciones fijadas

- 240 originales PDF/TXT, con los mismos hashes del manifiesto versión 2.
- 68 casos, tres formulaciones y tres filas de referencia local: 612 peticiones de búsqueda.
- Las preguntas y citas esperadas son las del informe posterior a la corrección OCR; se cotejaron campo por campo antes de la carga.
- Se envían los bytes originales, sin OCR previo, división ni conversión adicionales.
- Los errores de indexación permanecen visibles y sus casos se conservan en el denominador.

Store utilizado: `vs_6ae911da598c81918e58f3cd6138f3c6`, llamado “Evaluación motor documental | 240 ficticios | 2026-11-02”. La verificación inicial mediante API confirmó acceso y cero archivos.

## Qué se compara

La [API de búsqueda](https://developers.openai.com/api/reference/resources/vector_stores/methods/search) recibe cada pregunta original, con cinco resultados como máximo, reescritura desactivada, `ranker=auto` y umbral cero. No se llama a Responses ni a un modelo conversacional.

Los modos textual, vectorial e híbrido pertenecen a nuestro motor. En este experimento OpenAI ejecuta la misma configuración de búsqueda en las tres repeticiones de cada pregunta. La etiqueta `modo_local` identifica la fila local comparada; no significa que se haya configurado un modo equivalente en OpenAI.

Se comparan documento esperado en top 5 y cita completa dentro de un único bloque de contenido de ese documento. La comparación literal solo unifica espacios; la normalizada también ignora diferencias de mayúsculas, acentos y puntuación. Se conserva el número de resultados y de bloques devueltos para identificar diferencias en las unidades de recuperación.

La respuesta de búsqueda documentada por OpenAI no incluye un número de página nativo. Esa métrica queda sin equivalencia directa; no se inventan números de página a partir de la posición del resultado.

## Trazabilidad y límites

`demo/cliente_openai.py`, `demo/modelos_openai.py` y `demo/evaluar_openai.py` implementan el experimento. Los recibos y respuestas completas quedan en `data/desarrollo_de_aplicaciones/evaluacion_documental/comparacion_openai/`. Los envíos guardan una operación pendiente antes de contactar al proveedor y exigen reconciliar una respuesta incierta antes de reenviar.

La clave se lee desde un archivo privado externo al repositorio. Los errores HTTP conservan únicamente estado y request ID. Se mantiene verificación TLS.

La medición compara los sistemas completos de ingesta y búsqueda. No aísla el modelo de embeddings, no mide respuestas generadas y no demuestra precisión universal. El corpus y sus plantillas son sintéticos, con 68 casos anotados sobre 16 documentos; los demás documentos actúan como distractores.

## Resultados ejecutados el 2 de noviembre de 2026

OpenAI completó los 240 procesamientos sin reportar fallos. El índice ocupa 7 461 014 bytes. Se conservaron 612 respuestas principales con 612 request IDs distintos, además de seis controles auxiliares de preguntas sin evidencia.

En preguntas libres, comparando nuestro modo híbrido con la búsqueda predeterminada de OpenAI:

| Formato | Casos | Documento@5 local | Documento@5 OpenAI | Cita literal completa@5 local | Cita literal completa@5 OpenAI |
| --- | --- | --- | --- | --- | --- |
| PDF digital | 17 | 17 | 17 | 17 | 17 |
| PDF escaneado | 17 | 17 | 0 | 15 | 0 |
| PDF mixto | 17 | 17 | 9 | 15 | 9 |
| TXT | 17 | 16 | 17 | 9 | 17 |
| Total | 68 | 67 | 43 | 56 | 43 |

La mediana fue de 50,3 ms en la API local y 1321,6 ms en OpenAI remoto. Son condiciones e infraestructuras diferentes; no se atribuye esa diferencia únicamente al algoritmo. El [resumen completo](07_Evidencias/comparacion_openai/resumen.md) conserva las nueve combinaciones de referencia y sus métricas.

## Qué explica las diferencias

Se consultó el contenido parseado de los 16 documentos con casos, después de terminar las 612 búsquedas. En los cuatro escaneados, OpenAI devolvió un aviso de texto no extraído y ocho marcadores de imagen por archivo. El estado completed no acreditó la lectura de sus cláusulas. Esta inspección no revisó los otros 36 escaneados sin casos.

La disponibilidad literal en ese contenido fue 17/17 para PDF digital, 0/17 para escaneado, 9/17 para mixto y 17/17 para TXT. Las 43 citas disponibles fueron exactamente las recuperadas en los 43 casos correspondientes. El endpoint de contenido parseado no garantiza exponer las fronteras efectivas de los pasajes de búsqueda.

El inventario sí registra una configuración estática de 800 tokens y 400 de solapamiento en todos los archivos. Nuestro motor utiliza un límite de 900 caracteres sin solapamiento. Son unidades y estrategias distintas; este experimento no aísla por separado el efecto del parser, la fragmentación, los embeddings y el ranker.

En TXT nuestro texto completo conserva las 17 citas, pero solo nueve llegan completas en top 5. El diagnóstico local previo identifica seis citas cortadas entre fragmentos y dos fallos de recuperación: `SIM0201-C21` y `SIM0202-C09`. La comparación confirma una prioridad concreta para el motor local: devolver contexto completo y mejorar la selección de esos pasajes antes de sustituir el modelo de embeddings.

Los seis controles auxiliares, dos preguntas inexistentes repetidas tres veces, devolvieron cinco vecinos cada uno en OpenAI. La búsqueda híbrida local también devolvía cinco. Esto no evalúa respuestas generadas ni acredita abstención de ninguno de los dos motores.

## Siguientes mejoras justificadas

1. Conservar cláusulas completas o recuperar contexto adyacente cuando una cita cruza fragmentos. Repetir los mismos casos de TXT para medir el efecto.
2. Evaluar un reranker y el tratamiento de identidad del documento sobre los fallos de recuperación restantes.
3. Continuar midiendo fidelidad OCR y detección de preguntas sin evidencia con ejemplos diversos y una muestra independiente de las plantillas actuales.

No se implementaron esas mejoras durante la comparación. Tampoco se subió texto preprocesado a OpenAI: una segunda prueba con el mismo texto extraído en ambos sistemas permitiría aislar mejor la recuperación, pero sería otro experimento.

## Evidencia y reproducción

[Resultados y hashes](07_Evidencias/comparacion_openai/comparacion.json), [recibos por respuesta](07_Evidencias/comparacion_openai/recibos_respuestas.tsv), [método y procedencia](07_Evidencias/comparacion_openai/metodo_y_procedencia.json) y cuatro muestras completas por formato en esa misma carpeta. Las 612 respuestas completas permanecen en los datos locales; sus hashes permiten cotejar los archivos conservados.

La revisión independiente recalculó las 13 filas, verificó las 612 respuestas y sus hashes, las identidades de archivos, los parámetros, los contenidos parseados y los seis controles auxiliares. No encontró inconsistencias ni bloqueos.

Con un corpus generado, su informe local correspondiente, una clave privada y un Store de prueba propio:

```bash
export OPENAI_API_KEY_FILE=/ruta/privada/clave
uv run --project backend python demo/evaluar_openai.py RUTA_CORPUS RUTA_INFORME_LOCAL VECTOR_STORE_ID
uv run --project backend python demo/resumir_openai.py RUTA_CORPUS RUTA_INFORME_LOCAL RUTA_SALIDA
uv run --project backend python demo/diagnosticar_openai.py RUTA_CORPUS docs/07_Evidencias/corpus_amplio/sin_evidencia_base.json
```

Ejecutar desde la raíz del producto. Para una carga nueva el Store debe estar vacío; para reanudar se conservan sus recibos originales. La configuración TLS puede requerir un CA bundle válido mediante SSL_CERT_FILE; no se desactiva la verificación de certificados.

El resultado corresponde a una muestra de casos equilibrada por formato dentro de este corpus sintético y a la configuración utilizada: 68 casos, 17 por formato. No demuestra superioridad general sobre OpenAI File Search ni compara agentes conversacionales.

La [matriz de capacidades y resultados](13_matriz_capacidades.md) distingue funciones ofertadas, consumidas y evaluadas, y propone las prioridades de trabajo.
