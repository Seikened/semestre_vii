# Investigación y evolución del motor documental

Revisión del 2 de noviembre de 2026. Fuentes primarias consultadas: documentación oficial, repositorios de los autores y artículos originales. Las propuestas de este documento no están implementadas ni autorizan cambios del núcleo.

Corte de esta investigación: benchmark de recuperación, antes del incremento conversacional. Después Fernando aprobó e incorporamos el [MVP de Luna](16_chat_luna_mvp.md), con [evidencia propia](07_Evidencias/luna_mvp.md). Las brechas del mapa siguiente describen aquel punto de partida; las demás estrategias siguen como propuestas.

## 1. Valor y límites de lo construido

Conviene continuar con el motor como base de un asistente documental para inmobiliarias. Ya permite cargar, organizar, leer y recuperar contratos ficticios, conservando archivo, página y método de extracción. Ese recorrido tiene una utilidad concreta: localizar una condición y comprobarla en el original.

La evidencia actual respalda viabilidad técnica acotada. En las 68 preguntas libres, nuestro híbrido recuperó el documento en 67 casos y la cita literal completa en 56; OpenAI lo hizo en 43 y 43. OpenAI recuperó las 17 citas de TXT frente a nueve del local. Los resultados y recibos están en la [matriz comparativa](13_matriz_capacidades.md).

Hay 240 documentos, pero los 68 casos consultan solo 16 y proceden de generación sintética. El corpus tiene 120 PDF digitales, 40 escaneados, 40 mixtos y 40 TXT; los casos sí están equilibrados por formato. Las 612 peticiones no representan 612 preguntas independientes. Esta medición no demuestra calidad general, superioridad aislada de E5, concurrencia, rentabilidad ni adecuación para producción. Tampoco se ha comparado directamente con NotebookLM.

La hipótesis de producto es un expediente inmobiliario consultable: encontrar contratos por persona o inmueble, mostrar cláusulas completas y distinguir versiones y anexos. Su valor deberá comprobarse con tareas de operadores, tiempo de resolución y errores, usando por ahora exclusivamente documentos ficticios.

## 2. Mapa por niveles hacia una experiencia como NotebookLM

La ayuda pública de NotebookLM describe preguntas sobre fuentes seleccionadas, citas verificables y navegación al pasaje citado. Es una referencia de experiencia de uso; no revela su arquitectura interna ni demuestra que nuestro sistema pueda igualarlo. [Ayuda oficial del chat](https://support.google.com/notebooklm/answer/16179559?hl=es-419).

| Nivel | Responsabilidad | Situación actual y siguiente necesidad |
| --- | --- | --- |
| 1. Biblioteca | Original, extracción, estructura y procedencia | PDF/TXT, OCR y página disponibles. Falta evaluar tablas, orden de lectura, versiones y coordenadas para resaltar el pasaje. |
| 2. Recuperación | Encontrar y ordenar evidencia del expediente correcto | Full-text, E5 y RRF disponibles. Mejorar contexto de cláusulas, identidad documental y orden final. |
| 3. Respuesta | Explicar lo encontrado y citar cada afirmación | Pendiente. Luna deberá consumir evidencia y reconocer insuficiencia o contradicción. |
| 4. Producto y operación | Seleccionar fuentes, gestionar biblioteca y controlar acceso | UI local disponible. Permisos por inmobiliaria, respaldo/restauración, observación y despliegue requieren diseño y verificación propios. |

La sensación de robustez depende de la conexión de estos niveles. Cambiar únicamente el embedding no resuelve un escaneo ilegible, una cláusula cortada o una fuente equivocada. Las colecciones actuales son filtros de organización, no controles de autorización.

## 3. Estrategias documentadas y pruebas propuestas

### 3.1. Recuperar un fragmento y devolver su contexto

LlamaIndex documenta *sentence-window retrieval*: indexar unidades pequeñas y, después de encontrarlas, recuperar las oraciones vecinas para dar contexto. Es una estrategia aplicable sin adoptar todo el framework. [Ejemplo oficial](https://developers.llamaindex.ai/python/examples/node_postprocessor/metadatareplacementdemo/).

**Aplicación propuesta:** comparar el corte actual con solapamiento y con recuperación de cláusula o contexto adyacente. Conservar el texto literal y sus páginas, incluyendo cláusulas que crucen páginas. Es el primer experimento porque seis de los ocho fallos de cita TXT cruzan fragmentos; sus textos completos sí están extraídos.

**Medición:** cita completa@5 sobre los mismos 68 casos, contexto adicional devuelto, duplicados y latencia. Separar el éxito de localizar la evidencia del éxito de reconstruirla completa. Recuperar esos seis cortes es una meta a comprobar, no un resultado anticipado.

### 3.2. Recuperación amplia y reranker multilingüe

Sentence Transformers describe dos etapas: un recuperador reúne candidatos y un *CrossEncoder* puntúa conjuntamente consulta y pasaje para reordenarlos. Esto reduce el número de pares que debe procesar el modelo más costoso. [Retrieve & Re-Rank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html).

**Aplicación propuesta:** conservar E5, full-text y RRF como base. Comparar RRF solo frente a RRF seguido de reranker sobre un conjunto acotado de candidatos. BAAI publica `bge-reranker-v2-m3` como modelo multilingüe con licencia Apache 2.0; es un candidato para una prueba local, sin asumir que será rápido o mejor en nuestros contratos en español. [Ficha de BAAI](https://huggingface.co/BAAI/bge-reranker-v2-m3).

**Medición:** presencia del pasaje correcto entre candidatos, Documento@1, MRR@10, cita completa@5, p50/p95 y memoria. Si el candidato correcto no llega al reranker, investigar primero la recuperación. Un reranker tampoco reconstruye texto que el OCR nunca extrajo. El score no se interpreta como probabilidad de que una respuesta sea cierta.

### 3.3. Dar identidad documental a los fragmentos

Anthropic documenta *Contextual Retrieval*: anteponer contexto específico del fragmento antes de vectorizarlo y crear su índice BM25. Su implementación utiliza un LLM para producir ese contexto. Los beneficios publicados pertenecen a su evaluación y no se transfieren automáticamente a nuestro servicio. [Investigación original](https://www.anthropic.com/research/contextual-retrieval).

**Aplicación propuesta:** empezar por contexto verificable sin LLM: título, folio, sección y otros metadatos realmente disponibles. Conservar la cita original por separado. Evaluar después si generar contexto adicional justifica su costo y riesgo. Nuestro ranking textual usa PostgreSQL `ts_rank_cd`, no BM25; incorporar BM25 sería otro experimento, no una descripción del código actual.

**Medición:** errores con contratos casi idénticos, personas homónimas, propiedades similares y anexos. Usar nombres, folios y fechas exactas como restricciones cuando la pregunta los identifique inequívocamente; pedir aclaración si hay ambigüedad. No convertir esas reglas de producto en supuestas capacidades ya implementadas.

### 3.4. Extracción con estructura y citas localizables

Docling ofrece procesamiento local con análisis de layout, orden de lectura, tablas y OCR. Su código es MIT; los modelos utilizados tienen licencias propias. Es una alternativa para evaluar documentos complejos, no una razón para sustituir de inmediato el OCR actual. [Repositorio oficial de Docling](https://github.com/docling-project/docling).

**Aplicación propuesta:** comparar Tesseract y la extracción actual frente a Docling en una muestra ficticia con dos columnas, tablas de pagos, encabezados digitales y cláusulas partidas. Conservar texto nativo cuando sea fiel. Para resaltar citas, registrar la relación entre texto, página y región visual; hoy solo existe el vínculo a página, sin resaltado.

**Medición:** exactitud de importes, fechas y negaciones, orden del texto, celdas de tabla, páginas omitidas, tiempo y memoria de ingesta. Una importación terminada no demuestra lectura correcta: la prueba de OpenAI ya mostró esa diferencia.

### 3.5. Evidencia suficiente y evaluación por componentes

Ragas distingue calidad del contexto recuperado, fidelidad al contexto y calidad de la respuesta. Esa separación sirve para diseñar la evaluación, aunque todavía no incorporemos la herramienta ni un juez LLM. [Artículo original de Ragas](https://arxiv.org/abs/2309.15217).

**Aplicación propuesta:** ampliar preguntas sin respuesta, con inmueble equivocado, importes contradictorios, versiones antiguas y negaciones. En esta prueba ambos motores devolvieron vecinos ante preguntas sin evidencia; eso no equivale a contestar correctamente ni demuestra abstención. Primero definir y comprobar qué evidencia permite mostrar un resultado como respaldo.

**Medición:** falsos positivos sobre casos negativos y pérdidas de casos válidos. Cuando se conecte Luna, medir además afirmaciones respaldadas, cita correcta y reconocimiento de evidencia insuficiente. Un umbral debe calibrarse con un conjunto separado; RRF no proporciona un porcentaje de confianza.

### 3.6. Contexto largo, GraphRAG e índices aproximados

El artículo *Lost in the Middle* muestra sensibilidad a la posición de la información en los modelos y tareas estudiados. Justifica evaluar tamaño y orden del contexto al conectar Luna; no prueba un defecto específico de Luna ni establece un límite universal. [Liu et al., TACL 2024](https://aclanthology.org/2024.tacl-1.9/).

GraphRAG propone grafos de entidades y resúmenes de comunidades para preguntas globales sobre un corpus. Puede interesar para explorar temas o relaciones entre expedientes, pero agrega extracción y generación con LLM. Lo reservaría para una necesidad demostrada de síntesis global. Para contar vencimientos con fechas verificadas, primero evaluar una consulta estructurada. [Edge et al., GraphRAG](https://arxiv.org/abs/2404.16130).

pgvector permite búsqueda exacta y aproximada. HNSW intercambia parte del recall de vecinos por velocidad; no aumenta por sí mismo la pertinencia jurídica. Hoy utilizamos búsqueda vectorial exacta. Con 5559 fragmentos no se ha demostrado que necesitemos HNSW. Adoptarlo después de medir carga, filtros y recall frente a la referencia exacta. [Documentación oficial de pgvector](https://github.com/pgvector/pgvector#indexing).

## 4. Cómo convertir esta investigación en evidencia

1. **Congelar la base actual.** Conservar manifiesto, resultados, configuración y recibos. Cambiar una sola técnica por experimento y repetir los casos existentes.
2. **Crear un conjunto nuevo reservado.** Usar plantillas ficticias distintas, redactar consultas sin copiar títulos de cláusula y separar documentos completos entre ajuste y evaluación. La semilla distinta no basta si repite el mismo molde.
3. **Ampliar dificultad, no solo volumen.** Añadir cláusulas entre páginas, escaneos torcidos y borrosos, tablas, homónimos, anexos, versiones y preguntas sin respuesta. Etiquetar de antemano documento, pasaje y páginas esperados.
4. **Separar los fallos.** ¿Se extrajo el texto? ¿Llegó al conjunto de candidatos? ¿Quedó bien ordenado? ¿Se devolvió completo? Más adelante, ¿la respuesta lo utilizó fielmente?
5. **Comparar en condiciones claras.** Una futura prueba con ambos motores recibiendo el mismo texto extraído permitiría aislar mejor la recuperación. Mantener también la prueba con originales para medir la experiencia completa. No se ha ejecutado esa comparación normalizada ni requiere ahora reutilizar una clave.
6. **Medir utilidad de producto.** Proponer a un operador tareas con contratos ficticios y registrar tiempo, errores y si puede verificar la fuente. Esa prueba pendiente aportaría evidencia de valor que el benchmark de recuperación no mide.

## 5. Prioridad recomendada

| Orden | Incremento propuesto | Evidencia necesaria para decidir |
| --- | --- | --- |
| 1 | Contexto completo de cláusulas | Mejorar los seis cortes TXT sin deteriorar los demás formatos. |
| 2 | Identidad y reordenamiento | Reducir confusiones y mejorar primeras posiciones con costo local aceptable. |
| 3 | Casos negativos y contradicciones | Separar evidencia válida de vecinos similares sobre evaluación reservada. |
| 4 | Interacción con fuentes y Luna | Respuestas comprobables, selección de documentos y navegación precisa a citas. |
| Según uso | Layout avanzado, versiones, acceso y operación | Resolver un caso concreto y validar sus requisitos propios. |

PostgreSQL, pgvector, E5 y Nuxt siguen siendo una base razonable para estos experimentos. No hace falta introducir simultáneamente otra base vectorial, LangChain, LlamaIndex, GraphRAG y un modelo mayor. Primero cerrar la entrega académica sobre el servicio verificado. Cada cambio crítico posterior necesita diseño, archivos afectados, presupuesto y aprobación antes de implementarse.

La oportunidad está en comprobar una tarea inmobiliaria completa con fuentes rastreables. La investigación ofrece maneras de mejorar esa capacidad; el producto y su viabilidad comercial todavía deben validarse.
