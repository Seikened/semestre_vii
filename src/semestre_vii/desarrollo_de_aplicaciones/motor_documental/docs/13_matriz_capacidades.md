# Matriz de capacidades y resultados

Evaluación del 2 de noviembre de 2026. Se compara nuestro motor documental, con embeddings preentrenados E5 locales, OCR y pgvector, frente a OpenAI Retrieval sobre Vector Stores. La calidad aislada del modelo de embeddings no fue medida.

Esta matriz corresponde al experimento de recuperación sin agente. Después se incorporó el [chat opcional de Luna](16_chat_luna_mvp.md), cuya [verificación](07_Evidencias/luna_mvp.md) es distinta. Sus respuestas no forman parte de las métricas comparativas de esta matriz.

La conclusión es doble: nuestro motor funcionó mejor en el conjunto evaluado por su lectura de escaneados y documentos mixtos; OpenAI recuperó mejor las citas de TXT y ordenó mejor los resultados de texto digital en los escenarios indicados. Su catálogo también ofrece funciones que todavía no hemos activado ni comparado.

## Alcance y criterio de comparación

- 240 documentos ficticios con los mismos bytes originales.
- 68 casos sobre 16 documentos: 17 casos por formato. El corpus completo contiene 120 PDF digitales y 40 documentos de cada formato restante.
- 612 peticiones: 204 textos distintos, con tres filas de referencia local. OpenAI utilizó la misma configuración en sus tres repeticiones.
- Local: modo híbrido para preguntas libres y naturales; modo textual para la consulta dirigida con folio y frase.
- OpenAI: `ranker=auto`, cinco resultados, `rewrite_query=false`, `score_threshold=0`, sin filtros adicionales por atributos.
- Seis controles auxiliares sin evidencia, separados de los 68 casos principales.

**Probada** significa ejecutada y respaldada por los recibos. **Ofertada** significa documentada por el proveedor; no acredita una mejora medida. La columna de ventaja distingue resultado observado, ventaja funcional y aspecto sin evaluación.

## Matriz de capacidades

| Capacidad | Nuestro motor actual | OpenAI: oferta y uso en la prueba | Ventaja o lectura correcta |
| --- | --- | --- | --- |
| Carga e indexación de PDF y TXT | Probada con los 240 archivos; procesamiento propio. | Probada con los mismos 240; ingesta gestionada. | Ambos completaron la carga; la fidelidad se verifica aparte. |
| OCR en escaneados y páginas mixtas | Tesseract, método por página y OCR parcial intrapágina, probados. | En los cuatro escaneados inspeccionados el contenido parseado conserva avisos y marcadores de imagen. | Local en los casos medidos. Esto no evalúa otras vías de visión o lectura de OpenAI. |
| Embeddings y búsqueda semántica | E5 multilingüe, 384 dimensiones, ejecutado en CPU. | Vectorización y búsqueda gestionadas; el modelo interno no se identificó en la prueba. | Ambos consumidos; no hay ganador del embedding aislado. |
| Búsqueda textual e híbrida | Full-text en español, búsqueda vectorial y fusión RRF; los tres modos se ejecutaron. | Ofrece recuperación semántica y por palabras clave. Se consumió su búsqueda predeterminada. | Ambos tienen estas capacidades; los tres modos locales no equivalen a tres modos OpenAI. |
| Fragmentación y solapamiento | Límite de 900 caracteres por página, sin solapamiento. | Se observó configuración estática de 800 tokens y 400 de solapamiento; admite configuración. | OpenAI ofrece una capacidad más completa para configurar fragmentos. No se aisló su efecto sobre el resultado. |
| Modelo de reordenamiento de candidatos | No implementado; sí existen ranking textual, similitud y RRF. | Se activó `ranker=auto`. | Ventaja funcional OpenAI; no se midió el efecto del reranker por separado. |
| Reformulación de consultas | No implementada. | Ofrece `rewrite_query`; estuvo desactivada. | Oferta adicional OpenAI, beneficio pendiente de medir. |
| Filtros por metadatos | Colección como filtro expuesto y usado. El backend también excluye documentos inactivos y otros modelos. | Ofrece filtros por atributos y combinaciones lógicas; no se activaron. | Mayor flexibilidad ofertada por OpenAI; sin comparación de calidad con esos filtros. |
| Umbral de relevancia | No está expuesto como parámetro de consulta. | Ofrece umbral; se fijó en cero. | OpenAI tiene el control disponible. La configuración usada no demuestra abstención. |
| Procedencia por archivo, página y método | Devuelve archivo, página, método y vínculo al original; probado. | La respuesta evaluada incluye archivo, ID, contenido y score, sin campo nativo de página. | Local para esta trazabilidad por página y método. File Search con respuestas generadas no se evaluó. |
| Formatos y límites de entrada | PDF y TXT UTF-8, máximo 10 MiB en nuestra API. | Documenta más formatos, como DOCX, HTML, Markdown y PPTX, y hasta 512 MB por archivo con límite de tokens. Solo se probaron PDF/TXT pequeños. | OpenAI tiene mayor cobertura ofertada; máximos y formatos adicionales no se probaron. |
| Lotes y estados de procesamiento | La ingesta HTTP procesa cada documento antes de devolverlo. | Se utilizó un lote de 240 archivos y se consultaron sus estados. | OpenAI aporta una capacidad de ingesta asíncrona ya gestionada. No se comparó rendimiento de ingesta en condiciones equivalentes. |
| Control del procesamiento y del almacenamiento | Código, modelo configurado, PostgreSQL y originales bajo nuestro control. | Se consume un servicio remoto; el proveedor administra su motor. | Local para personalización e inspección; OpenAI reduce la operación del motor que debemos mantener. |
| Operación y costo total | Debemos mantener infraestructura, modelos, originales y respaldos. El cómputo local también tiene costo. | Servicio alojado con tarifas; reduce la infraestructura propia de recuperación. | Es una decisión de operación. No se midió costo total ni se validó que uno sea más barato. |
| Agente que redacta respuestas | Etapa posterior, todavía sin conectar Luna. | File Search puede integrarse en Responses; no se consumió esa modalidad. | Oferta adicional OpenAI; calidad conversacional sin evaluar en ambos. |
| Escala, concurrencia y aislamiento por inmobiliaria | Demo de un operador; las colecciones no sustituyen permisos de acceso. | Servicio gestionado; no se probaron carga concurrente ni autorización de nuestra aplicación por inmobiliaria. | Sin ganador validado para estos requisitos. |

La oferta de filtros, ranking, reescritura, fragmentación y límites se consultó en la [guía oficial de Retrieval](https://developers.openai.com/api/docs/guides/retrieval). La cobertura de formatos, alojamiento e integración conversacional se contrastó con la [guía oficial de File Search](https://developers.openai.com/api/docs/guides/tools-file-search). El contrato de fuentes corresponde a la [API de búsqueda utilizada](https://developers.openai.com/api/reference/resources/vector_stores/methods/search).

## Matriz de resultados bajo los mismos escenarios

Documento@5 indica que el archivo esperado aparece entre los cinco primeros resultados. Cita literal@5 exige la cita completa dentro de un solo pasaje o bloque devuelto del archivo correcto, unificando únicamente espacios. Página@5 queda sin equivalencia directa para OpenAI.

| Escenario y modo local | Casos | Documento@5 local / OpenAI | Cita literal@5 local / OpenAI | Resultado observado |
| --- | --- | --- | --- | --- |
| Preguntas libres, PDF digital, híbrido | 17 | 17 / 17 | 17 / 17 | Empate en recuperación completa dentro de top 5. |
| Preguntas libres, PDF escaneado, híbrido | 17 | 17 / 0 | 15 / 0 | Local. |
| Preguntas libres, PDF mixto, híbrido | 17 | 17 / 9 | 15 / 9 | Local. |
| Preguntas libres, TXT, híbrido | 17 | 16 / 17 | 9 / 17 | OpenAI. |
| Preguntas libres, conjunto completo, híbrido | 68 | 67 / 43 | 56 / 43 | Local en esta muestra equilibrada de casos. |
| Pregunta natural con folio, conjunto completo, híbrido | 68 | 67 / 50 | 56 / 43 | Local con la configuración comparada. |
| Folio y frase dirigida, conjunto completo, textual | 68 | 68 / 48 | 58 / 43 | Local con ese modo de consulta. |

El empate de PDF digital en top 5 no implica el mismo orden. En esos 17 casos, OpenAI puso primero el documento correcto en **13/17**, frente a **11/17** del local. En TXT las cifras fueron **15/17** y **14/17**, respectivamente. Son ventajas observadas de posición en una muestra pequeña, sin demostración de significancia estadística.

La mediana de la búsqueda libre híbrida fue de **50,3 ms local** y **1321,6 ms remota**. El local tuvo menor latencia en esa ejecución; la comparación incluye redes, infraestructura y operaciones diferentes, por lo que no establece superioridad algorítmica o rendimiento a gran escala.

En las dos preguntas sin evidencia, OpenAI devolvió cinco vecinos en cada una de sus tres repeticiones; el híbrido local también devolvió cinco por pregunta. Es una limitación compartida de la configuración usada, no una evaluación de respuestas generadas.

## Qué tiene mejor OpenAI

- **Recuperación de TXT en esta prueba:** 17 citas completas frente a nueve. Nuestro índice conserva las 17 citas en el texto completo, pero seis cruzan fragmentos y dos fallan en recuperación.
- **Orden inicial en texto digital:** más documentos correctos en primera posición en los casos indicados de PDF digital y TXT.
- **Funciones listas para consumir:** reranker activado, fragmentación configurable con solapamiento e ingesta por lotes. Reescritura, filtros adicionales y mayor cobertura de formatos están ofertados, pero sus beneficios no se midieron aquí.
- **Menor carga operativa del motor de recuperación:** el proveedor administra el servicio; nuestra aplicación sigue necesitando diseño de acceso e integraciones propias.

Su desventaja principal observada fue la lectura insuficiente de los escaneados y de partes en imagen de los documentos mixtos evaluados. También dependemos del servicio remoto y de sus tarifas, sin control completo del motor interno.

## Qué tiene mejor nuestro motor

- **OCR y recuperación de imagen en los escenarios medidos:** 15 citas de escaneados y 15 de mixtos frente a cero y nueve.
- **Resultado global para esta mezcla de casos:** 67 documentos y 56 citas completas frente a 43 y 43 en preguntas libres.
- **Trazabilidad de la fuente:** archivo, página y método de extracción en nuestra API, con apertura del original.
- **Control técnico:** podemos inspeccionar y modificar extracción, segmentación, modelo y recuperación. Cambiar de modelo requiere reindexación y adecuar la dimensión persistida; no es un cambio automático desde la interfaz.
- **Menor latencia local observada**, con la limitación de condiciones ya indicada.

Sus desventajas actuales son los cortes de citas en TXT, ausencia de un reranker dedicado, menor cobertura de formatos y filtros, y responsabilidad propia de operación. Todavía no incorpora permisos multiusuario ni aislamiento de negocio por inmobiliaria.

## Conclusión para continuar

Conviene conservar la base actual y mejorarla por niveles:

1. **Preparación del documento:** recuperar cláusulas completas o contexto adyacente, empezando por los seis cortes de TXT identificados. Verificar el cambio contra los mismos casos.
2. **Selección de evidencia:** evaluar reordenamiento y tratamiento de identidad sobre los dos fallos restantes de recuperación. Medir calidad y latencia antes de adoptar otro modelo.
3. **Uso seguro de la evidencia:** diseñar el comportamiento ante preguntas sin respaldo y ampliar los casos negativos. Un score o cinco vecinos no acreditan que exista el documento solicitado.
4. **Ampliación según necesidad:** filtros de negocio y formatos adicionales; después, conversación con Luna. Escala y acceso multiusuario requieren pruebas y diseño propios.

Esto no demuestra que E5 sea mejor que los embeddings internos de OpenAI. Se compararon motores completos con extracción, fragmentación y ranking distintos. Para aislar mejor la búsqueda se podría diseñar otro experimento entregando a ambos el mismo texto ya extraído; esa prueba no se ha ejecutado.

## Evidencias y costo

La matriz reutiliza [las mediciones auditadas](07_Evidencias/comparacion_openai/comparacion.json) y el [reporte del experimento](12_comparacion_openai.md), sin volver a cargar archivos ni utilizar una clave. Las funciones ofertadas se distinguen de las consumidas y de las pendientes.

OpenAI documenta almacenamiento de File Search de USD 0,10 por GB/día después del primer GB gratuito y una tarifa por llamada de herramienta aplicable a Responses. Nuestra prueba usó búsqueda directa de Vector Stores; no se convierte su número de peticiones en llamadas de herramienta Responses ni se afirma un gasto facturado. Ver [tarifas y condiciones oficiales](https://developers.openai.com/api/docs/pricing). Tampoco se calculó el costo total local.
