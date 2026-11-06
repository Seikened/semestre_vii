# A*: producto y alcance del MVP

A* es un motor documental inmobiliario modular, con extracción de texto y OCR, vectorización local, búsqueda híbrida y recuperación de fuentes por archivo y página. Una interfaz web permite gestionar documentos y conversar con un agente opcional conectado al motor.

El problema es encontrar información dentro de muchos contratos sin perder el vínculo con su origen. El producto se presenta como MVP local. Todos los contratos, inmuebles, importes y partes de la demostración son ficticios.

## Capacidades actuales

| Capacidad | Qué hace el MVP | Evidencia y límite |
| --- | --- | --- |
| Gestión documental | Crear colecciones, cargar PDF/TXT, consultar, editar título o colección y retirar documentos mediante baja lógica. | API y UI conectadas; [recorridos HTTP](07_Evidencias/servicio_http_luna.json). Un operador local. |
| Extracción y OCR | Leer texto digital y aplicar Tesseract a páginas escaneadas o con imágenes relevantes, conservando su número y método. | [SC-001](05_Cambios/solicitudes_cambio.md). La detección intrapágina es heurística. |
| Fragmentación | Dividir el texto conservando la página de origen. | Todavía puede separar condiciones entre fragmentos; no reconoce cláusulas jurídicas arbitrarias. |
| Vectorización local | Generar embeddings con E5 multilingüe de 384 dimensiones. | Modelo público preentrenado con revisión fija; no se entrenó un modelo fundacional propio. |
| Recuperación | Buscar por texto, similitud vectorial o combinación de rankings con RRF. | PostgreSQL Full-Text Search y pgvector. La búsqueda vectorial es exacta; no hay HNSW ni reranker. |
| Procedencia | Mostrar el pasaje recuperado y abrir el archivo original en su página. | El usuario debe revisar la fuente; una puntuación no es un porcentaje de certeza. |
| Conversación opcional | GPT-6 Luna formula una consulta mediante `buscar_documentos` y responde a partir de los pasajes recuperados. | [Piloto del chat](07_Evidencias/luna_mvp.md). Hasta dos llamadas externas y una búsqueda por turno. Requiere clave vigente. |
| Ejecución reproducible | Levantar web, API y PostgreSQL en tres contenedores y cargar seis contratos iniciales. | [Copia independiente del paquete A*](07_Evidencias/c2_a_asterisco.md), con volúmenes nuevos y sin clave OpenAI. |

El buscador y los embeddings funcionan sin OpenAI. El chat utiliza una herramienta propia sobre PostgreSQL; no utiliza el `file_search` gestionado ni carga los originales a los Vector Stores de OpenAI. El proveedor recibe pregunta, contexto reciente y pasajes recuperados.

## Mapa de piezas

1. **Interfaz:** Nuxt UI presenta biblioteca, carga, consulta y fuentes. Su BFF comunica con la API y conserva la credencial de acceso en servidor.
2. **Servicio y motor:** FastAPI valida las solicitudes; los módulos de extracción, OCR, embeddings y recuperación procesan documentos y consultas.
3. **Datos:** una base PostgreSQL contiene metadatos, texto y vectores mediante pgvector. Un volumen separado conserva los archivos originales. No son dos bases de datos.
4. **Agente opcional:** GPT-6 Luna utiliza la herramienta del servicio para consultar esa información y redactar una respuesta.

## Éxito verificable

Un contrato puede cargarse, procesarse y encontrarse por una cláusula conocida. El resultado conserva archivo y página; el usuario puede comprobarlo en el original. La gestión aplica las reglas en backend y una operación no autorizada devuelve el error previsto.

La comparación con OpenAI es una evaluación de recuperación sobre un corpus sintético acotado. No demuestra superioridad general ni la calidad universal de las respuestas del agente. Ver [método y resultados](12_comparacion_openai.md).

## Evolución posterior

- **Multicanal:** añadir WhatsApp oficial como otra entrada al mismo servicio. El canal implementado hoy es la web.
- **Almacenamiento remoto:** sustituir el volumen local por Cloudflare R2 mediante una integración posterior.
- **Calidad de recuperación:** evaluar segmentación por secciones, recuperación de contexto vecino y reranking con casos nuevos.
- **Uso por empresas:** diseñar identidad, permisos y aislamiento antes de atender múltiples usuarios o inmobiliarias.
- **Escala y operación:** medir carga y latencia antes de introducir índices aproximados, colas o trabajadores.

La [investigación](14_investigacion_y_evolucion.md) detalla alternativas. Estas capacidades futuras no se presentan como implementadas. La [lista de cierre](15_cierre_rubrica.md) distingue los pendientes del MVP de los requisitos académicos y de la entrega formal.
