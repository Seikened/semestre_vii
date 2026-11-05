# Arquitectura

Se utiliza un servicio modular en Python y un frontend separado. El motor no depende de un LLM para indexar o recuperar documentos.

## Niveles

1. **Nuxt UI 4.12 y BFF:** interacción y proxy HTTP con lista de rutas permitidas. La API key se lee exclusivamente en el servidor. El BFF valida el origen de las peticiones del navegador.
2. **FastAPI:** acceso por API key, validación Pydantic, endpoints, errores seguros y coordinación del motor.
3. **Motor documental:** PyMuPDF para texto nativo, Tesseract para páginas escaneadas, fragmentación por página y embeddings locales `intfloat/multilingual-e5-small` de 384 dimensiones con revisión fija.
4. **Datos:** PostgreSQL con pgvector y originales en volumen privado. Colecciones, documentos, páginas y fragmentos conservan procedencia e integridad.

Es como una biblioteca: Nuxt es el mostrador, la API recibe y valida las solicitudes, el motor lee y prepara las fichas, y PostgreSQL mantiene el catálogo. Los originales se conservan en su archivo.

## Organización

- `backend/app/main.py`: frontera HTTP y ciclo de arranque.
- `backend/app/contratos.py`: contratos de entrada y salida.
- `backend/app/motor.py`: coordinación de extracción, vectorización e incorporación.
- `backend/app/extraccion.py`, `modelos.py`, `embeddings.py`: procesamiento.
- `backend/app/persistencia.py`: SQL y transacciones, sin ORM adicional.
- `backend/app/recuperacion.py`: búsqueda léxica, exacta por coseno e híbrida con RRF.
- `backend/app/chat.py` y `chat_contratos.py`: conversación opcional con Luna y contratos validados.
- `backend/app/errores/`: catálogo, excepción, registro y traducción HTTP.
- `db/objetos_bd.sql`: esquema inicial, restricciones, índices y vista.
- `frontend/`: interfaz y BFF. No accede a PostgreSQL ni a los originales directamente.

## Ejecución

Compose levanta tres contenedores: `web`, `api` y `db`. PostgreSQL no publica un puerto al host. Web y Swagger se exponen únicamente en localhost. Los volúmenes conservan datos, originales, modelos y credenciales generadas al arrancar.

La incorporación es síncrona y el esquema se inicializa en una base nueva. Páginas y vectores se guardan en una transacción. Un fallo de inserción retira el original recién copiado; una interrupción del proceso entre archivo y commit puede dejar un original huérfano. No se implementa una transacción distribuida ni un sistema de migraciones de versiones todavía.

La demo utiliza un único proceso de API y limita los hilos de CPU del modelo. No hay colas, trabajadores, reranker, HNSW ni servicios adicionales sin un caso medido que los requiera.

Luna utiliza Responses mediante HTTPS saliente desde API. La herramienta `buscar_documentos` llama al motor local, respetando la colección seleccionada. La clave del proveedor se monta como secreto únicamente en API; no llega a web. El chat no añade persistencia y mantiene un máximo de dos llamadas externas y una búsqueda por turno. Ver [diseño conversacional](16_chat_luna_mvp.md).

R2 sustituirá el almacenamiento local mediante una frontera posterior; WhatsApp será otro canal. Esas dos conexiones siguen pendientes.
