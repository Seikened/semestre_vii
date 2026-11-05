# A*: guion de la demostración en vivo

**Alumno:** Fernando León Franco, matrícula 192488-7, datos confirmados por Fernando.
**Exposición:** 4 de noviembre de 2026 a las 17:00, hora de America/Mexico_City, confirmada por Fernando.
**Duración:** diez minutos. La presentación será en vivo, con este archivo como apoyo.

El guion está preparado. Su lectura no acredita un ensayo ni la exposición. El [checklist](../15_cierre_rubrica.md) conserva los pendientes reales de la aplicación y de su entrega.

## Apertura lista para decir

> Mi proyecto se llama A*. Es un motor documental pensado para una inmobiliaria que necesita organizar muchos contratos y encontrar información dentro de ellos, conservando siempre el documento y la página de origen.
>
> En este MVP puedo cargar un PDF o un archivo de texto, extraer su contenido, aplicar OCR cuando corresponde, generar sus vectores y buscar información por palabras o por significado. También puedo conversar con un agente que utiliza ese mismo buscador y muestra las fuentes que respaldan su respuesta.
>
> Hoy voy a demostrar la carga de un contrato ficticio, la búsqueda de una cláusula y su comprobación en el original. Después mostraré la solicitud de cambio, una operación rechazada y la arquitectura que conecta la interfaz, la API y PostgreSQL.

La denominación completa para la documentación es: **motor documental modular con OCR, vectorización local, búsqueda híbrida y respuestas con fuentes**. Multicanal es una evolución prevista: hoy funciona mediante la interfaz web.

## Preparación antes de clase

- [ ] Arrancar desde la raíz del producto con `docker compose up --build`; construir imágenes y descargar el modelo antes de la exposición.
- [ ] Abrir [A*](http://localhost:3000), [Swagger](http://localhost:8000/docs) y comprobar [salud](http://localhost:8000/salud).
- [ ] Dejar abiertos [C4](../01_Arquitectura/C4_Contexto.png), [DAR](../01_Arquitectura/DAR_Arquitectura.png), [DER](../02_Datos/DER.png), [SC-001](../05_Cambios/solicitudes_cambio.md) y [bitácora](../06_IA/bitacora_prompts.md).
- [ ] Tener a mano `demo/contratos/FIC-003_mixto.pdf` y los archivos ficticios `test.txt` y `test.pdf` del escritorio.
- [ ] Ensayar la carga con el selector nativo, comprobado con TXT y PDF mixto en el cierre B5. Fernando confirmó también el arrastre simple. Para el recorrido principal usar un solo archivo; arrastre múltiple y durante carga tienen comprobación física pendiente.
- [ ] Comprobar que la clave del chat siga vigente. Si falla, mantener la demostración de búsqueda local y declarar la indisponibilidad actual del chat.
- [ ] Preparar la negativa HTTP de abajo, sin abrir claves, archivos privados ni `.env` en pantalla.
- [ ] Practicar una vuelta completa con cronómetro. Reservar el último minuto para preguntas.

## Recorrido de 600 segundos

| Tiempo | Acción concreta | Explicación y criterio |
| --- | --- | --- |
| 0:00 a 0:45 | Mostrar A* y decir la apertura. | Problema inmobiliario, documentos ficticios y alcance de MVP. |
| 0:45 a 1:30 | Abrir C4 y señalar operador, sistema y servicio externo. | «El operador incorpora y consulta documentos. A* conserva su procedencia. OpenAI apoya la conversación; la búsqueda documental puede funcionar por separado». A1 y D2. |
| 1:30 a 2:30 | Mostrar DAR y después el estado de los tres contenedores. | «Hay cuatro niveles: interfaz y BFF, API, motor de procesamiento y almacenamiento. Se distribuyen en tres contenedores: web, API y base. El motor forma parte de la API». Explicar HTTP/JSON local, SQL privado y HTTPS hacia OpenAI. A2, B2 y D2. |
| 2:30 a 3:15 | Mostrar DER y SQL. | «Las cuatro tablas son colecciones, documentos, páginas y fragmentos. Sus llaves permiten volver del fragmento al original. El índice GIN sirve a la búsqueda textual; la vista resume documentos disponibles». A3 y A4. |
| 3:15 a 4:45 | Crear **Exposición ficticia**, cargar `FIC-003_mixto.pdf` y revisar el detalle. | «Conservo el PDF, extraigo texto por página y genero embeddings locales. La página 1 es digital y la 2 requiere OCR. Esta capacidad corresponde a SC-001». La animación indica actividad de la petición, no porcentaje ni etapa real publicada por la API. B3, B5, B6 y D1. |
| 4:45 a 6:15 | En esa colección, buscar en híbrida `¿Qué debo pagar si desocupo antes de tiempo el local Cedro?`. Abrir fuente y página 2. Si el chat está disponible, repetir allí. | Comprobar dos mensualidades y aviso de sesenta días contra el original. «La búsqueda textual ayuda con términos exactos y la vectorial con significado. RRF combina sus posiciones. El agente recibe los pasajes y redacta; la cita permite revisarlo». B5 y D1. |
| 6:15 a 7:00 | Cambiar el título y retirar solo la copia de exposición. Ver la colección vacía. | «La edición y el retiro pasan por la API. La baja lógica excluye el documento de consulta y descarga. El estado vacío es una respuesta válida». Mostrar CRUD y vacío. B3 y B5. |
| 7:00 a 7:45 | Abrir Swagger y ejecutar la petición sin credencial. | Mostrar once operaciones y el HTTP 401 real. «La autorización se aplica en backend; el navegador no recibe la clave interna». A5, B3, B4 y D1. |
| 7:45 a 8:30 | Mostrar bitácora y README. | «Registré cuatro prompts, el contexto, los límites, el plan disponible, los ajustes y el resultado. La instalación usa Docker Desktop y Compose; la documentación explica datos de ejemplo, URLs, reinicio y problemas comunes». B1, C2 y C3. |
| 8:30 a 9:00 | Volver a A* y explicar límites. | «Esta es una primera versión funcional. Quedan por evaluar más documentos, mejorar el contexto recuperado e incorporar acceso por usuarios. WhatsApp y R2 son pasos posteriores». |
| 9:00 a 10:00 | Responder con el diagrama o la fuente a la vista. | Nombrar la pieza, su responsabilidad y cómo se conecta. Si algo no se midió, decirlo. D3. |

En la [copia técnica de A*](../07_Evidencias/c2_a_asterisco.md), la pregunta natural de Cedro recuperó la cláusula en posición 2, página 2 OCR. Durante la demo revisar esa fuente; el primer resultado puede ser otra página del mismo contrato. No se afirma ranking perfecto.

## Negativa y contenedores

```bash
docker compose ps
```

Desde una terminal, con la API arrancada, ejecutar sin `X-API-Key`:

```bash
curl -i -X POST http://localhost:8000/buscar \
  -H 'Content-Type: application/json' \
  --data '{"texto":"depósito","modo":"hibrida","limite":5}'
```

Esperado: **HTTP 401**, código `ACCESO_DENEGADO`, sin resultados documentales. La [revisión actual](../07_Evidencias/revision_rubrica_actual.json) conserva este rechazo y disponibilidad HTTP de web, salud y Swagger.

## Respuestas de apoyo

| Pregunta del profesor | Respuesta breve |
| --- | --- |
| ¿Qué construiste tú? | El servicio que organiza, procesa, indexa y recupera documentos, sus contratos HTTP y la interfaz. Integro bibliotecas y modelos públicos; no entrené desde cero un LLM ni el modelo E5. |
| ¿Qué significa vectorizar? | Convertir cada fragmento en 384 números que permiten comparar su significado con una pregunta. El texto y la página se conservan para revisar lo recuperado. |
| ¿Qué es indexar? | Preparar y guardar el contenido para consultarlo. Aquí genero fragmentos, vectores y representación textual; pgvector almacena vectores y GIN apoya el texto. No utilizo HNSW todavía. |
| ¿Son dos bases? | Una base PostgreSQL contiene metadatos, texto y vectores. Los archivos PDF/TXT originales están en un volumen separado. |
| ¿Qué diferencia hay entre C4 y DAR? | C4 de contexto muestra quién utiliza el sistema y con qué sistemas se relaciona. DAR muestra sus piezas técnicas, despliegue y protocolos. |
| ¿Dónde está el modelo de ML? | E5 está dentro del contenedor API y produce embeddings locales. GPT-6 Luna es un servicio externo opcional para conversar. |
| ¿Por qué búsqueda híbrida? | Los términos exactos ayudan con folios y nombres; los vectores ayudan con otras formas de expresar una idea. Combino rankings con RRF. Recuperar un vecino parecido no demuestra que exista la respuesta. |
| ¿Cómo llega Luna a PostgreSQL? | Luna solicita `buscar_documentos`; nuestro backend ejecuta la búsqueda y devuelve pasajes. Luna no recibe credenciales SQL ni acceso directo a la base. |
| ¿Es el File Search nativo de OpenAI? | Uso una herramienta propia sobre el motor local. No subo los originales al Store gestionado. La conversación sigue consumiendo tokens del proveedor. |
| ¿Qué cambió SC-001? | Añadí soporte OCR y procedencia por página a la ingesta. Quedó reflejado en datos, API y UI. Después corregí páginas con encabezado digital y cuerpo en imagen mediante OCR parcial. |
| ¿Es multicanal? | Hoy tiene interfaz web. La API permite plantear otro canal, pero WhatsApp oficial todavía no está conectado. |
| ¿Qué seguridad tiene? | API key validada en backend, entradas acotadas, BFF con credencial privada, orígenes permitidos y base sin puerto público. El alcance es un operador local; faltan identidad y aislamiento por empresa para uso compartido. |
| ¿Qué pruebas tienes? | Recorridos HTTP reales, OCR, navegador, consultas con respuestas conocidas y arranque de una copia. No mantengo una suite de pruebas unitarias. Cada recibo indica qué versión se comprobó. |
| ¿Es mejor que OpenAI? | Solo hay una comparación acotada de recuperación con contratos sintéticos y configuración documentada. Hay escenarios favorables a cada sistema. Eso no prueba superioridad general ni evalúa respuestas del agente. |
| ¿Cómo usaste IA? | Definí el problema, pedí contratos ficticios y pruebas equivalentes, revisé propuestas y autoricé cambios concretos. La bitácora distingue lo conservado del chat de los vacíos del registro. La demostración muestra qué entiendo y qué puedo comprobar. |

## Contingencias

- Si el proveedor falla o la clave vence, mostrar el error y continuar con **Buscar fragmentos**. No atribuir al chat una respuesta nueva que no haya generado.
- Si la nueva carga tarda, utilizar el `FIC-003` inicial sin repetir peticiones a ciegas. Explicar que se trata de un documento previamente indexado.
- Si falla el arrastre, usar adjuntar y el selector de archivos. El procesamiento del backend es el mismo; conservar el fallo para revisarlo después.
- Si falla la API, comprobar salud. Una captura guardada se presenta como evidencia anterior, nunca como una ejecución que acaba de ocurrir.
- No reconstruir imágenes, generar el corpus ampliado ni repetir el benchmark durante los diez minutos.

## Registro del ensayo

| Comprobación | Estado |
| --- | --- |
| Nombre, matrícula y horario | Confirmados por Fernando. |
| Vuelta completa con cronómetro | Pendiente. Anotar duración y pasos que excedan su tiempo. |
| Carga mixta, fuente y negativa ejecutadas por Fernando | Pendiente de ensayo. |
| Disponibilidad del chat justo antes de clase | Pendiente. La clave temporal puede vencer. |
| Exposición y respuestas | Pendientes del 4 de noviembre a las 17:00. |

OneDrive y correo son la entrega formal posterior al cierre de la app. El PDF fija recepción antes del 4 de noviembre a las 19:00; la exposición de las 17:00 no sustituye el correo.
