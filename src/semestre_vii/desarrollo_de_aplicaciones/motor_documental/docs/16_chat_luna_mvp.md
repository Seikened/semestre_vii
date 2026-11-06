# Chat MVP de Luna

Incremento aprobado por Fernando el 2 de noviembre de 2026: «Sí, implementar y probar el MVP». El plan presentado delimitó archivos de backend y frontend, secreto privado, un endpoint y 450 a 650 líneas de código, sin nuevas tablas ni otro Vector Store. La ejecución se acredita por separado.

## Cuatro niveles

1. **Nuxt:** conversación, últimos tres pares de mensajes en memoria y selección de colección. Conserva biblioteca, CRUD y búsqueda directa. El BFF agrega la API key local del motor.
2. **FastAPI:** valida entradas y acceso. `POST /chat` admite pregunta, modo, colección e historial acotado. La clave de OpenAI solo está disponible en API mediante Compose secret.
3. **Luna:** `gpt-6-luna` mediante Responses. Primera llamada obligada a formular una búsqueda; segunda llamada para redactar con salida estructurada. Sin reintentos automáticos.
4. **Motor:** la herramienta `buscar_documentos` ejecuta `MotorDocumental.buscar`, con los filtros y originales locales existentes. Devuelve hasta cinco pasajes con documento y página.

`file_search` gestionado de OpenAI utiliza sus propios Vector Stores. Este incremento integra nuestro motor como una **function tool**; no sube el corpus ni consume aquel Store. El proveedor recibe pregunta, historial reciente y pasajes recuperados.

## Contrato y límites

Entrada de ejemplo:

```json
{"texto":"¿Cuándo se devuelve el depósito de Aurora?","modo":"hibrida","coleccion_id":null,"historial":[]}
```

Salida: `respuesta`, `resultado: ResultadoBusqueda` y `modelo`. Los vínculos al original se construyen con UUID y página reales, nunca con una URL del modelo.

- Pregunta de hasta 1000 caracteres y hasta seis mensajes anteriores de 4000 caracteres cada uno.
- Una búsqueda y hasta dos llamadas Responses por turno. Cada llamada tiene máximo de 4096 tokens de salida y timeout de 45 segundos; esos tokens incluyen razonamiento.
- La continuación conserva todos los elementos de la primera respuesta y agrega el resultado de la función con su `call_id`.
- La respuesta final indica índices de las fuentes utilizadas. El backend verifica sus límites, elimina duplicados y agrega la numeración correspondiente a las fuentes devueltas.
- Sin evidencia o sin citas: mensaje explícito de evidencia insuficiente, sin fuentes presentadas como respaldo.
- Clave ausente o proveedor no disponible: 503 seguro. Salida incompleta, sin formato válido o con fuente inexistente: 502 seguro. La recuperación directa conserva su funcionamiento.
- No hay acciones de escritura, conversaciones persistidas ni herramientas de navegación o ejecución. Los documentos son datos, no instrucciones.
- `store=false` permite administrar el contexto localmente; no representa una política de Zero Data Retention.

## Configuración

El archivo privado del proveedor se mantiene fuera del repositorio y se selecciona mediante la ruta `LUNA_API_KEY_FILE` en `.env`. Compose lo monta en `/run/secrets/luna_api_key` solo para API. El ejemplo vacío permite instalar y usar el motor sin credenciales. La entrega nunca incluye `.env` real ni la clave.

La vigencia y el saldo pertenecen a la cuenta del proveedor. Cuando la clave deje de funcionar, usar **Buscar fragmentos** o configurar otra clave autorizada. El chat no puede renovar una credencial.

## Verificación necesaria

Comprobar respuestas y fuentes de Aurora, Cedro y un documento escaneado o mixto; seguimiento conversacional; consulta sin evidencia; negativos de acceso/validación; funcionamiento sin clave; separación del secreto respecto de web; recorrido del chat en navegador. Conservar resultados reales y errores sin registrar claves.

Estos recorridos están ejecutados en el [recibo del MVP](07_Evidencias/luna_mvp.md), incluidos un ajuste de consulta, un 503 conservado y su reintento manual. La causa del fallo de comunicación no se identificó. El ensayo completo de la exposición sigue pendiente.

El benchmark de 68 casos y 612 peticiones comparó recuperación sin LLM. No acredita calidad de las respuestas conversacionales. Validar índices de citas tampoco garantiza por sí solo que cada afirmación esté respaldada.

## Fuentes oficiales

- [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna): identificador y capacidades del modelo.
- [Function calling](https://developers.openai.com/api/docs/guides/function-calling): función estricta, resultado y continuación.
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs): validación de la salida con Pydantic.
- [Estado conversacional](https://developers.openai.com/api/docs/guides/conversation-state): historial y contexto administrados por la aplicación.
