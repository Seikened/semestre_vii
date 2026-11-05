# A*: motor documental inmobiliario

MVP de un servicio local para organizar y recuperar contratos completamente ficticios. Extrae PDF y TXT, aplica OCR por página, genera embeddings locales y busca con PostgreSQL y pgvector. La interfaz A* utiliza Nuxt UI 4.12, con temas claro y oscuro y una paleta neutra inspirada en ChatGPT.

La recuperación funciona sin credenciales de OpenAI. El chat opcional utiliza GPT-6 Luna mediante Responses y una herramienta de búsqueda sobre este motor. R2 y WhatsApp oficial corresponden a etapas posteriores.

El [alcance del MVP](docs/01_producto_y_alcance.md) distingue capacidades actuales y evolución. El [guion de diez minutos](docs/08_Presentacion/guion.md) prepara la exposición del 4 de noviembre de 2026 a las 17:00, hora de México. El [checklist punto por punto](docs/15_cierre_rubrica.md) conserva evidencias y pendientes, sin confundirlos con una calificación.

## Arranque

Requisito: Docker Desktop abierto, conexión a Internet durante la primera construcción y descarga de modelos. Desde esta carpeta:

```bash
cp .env.example .env
docker compose up --build
```

En PowerShell, usar `Copy-Item .env.example .env` para el primer comando. La variante de PowerShell no se ha ejecutado en Windows.

- Interfaz: http://localhost:3000
- Swagger: http://localhost:8000/docs
- Disponibilidad: http://localhost:8000/salud

Esperar a que la API indique `Application startup complete`. El primer arranque descarga el modelo público y procesa los seis contratos incluidos. Los siguientes conservan la base, los originales y el modelo en volúmenes. La carga inicial no vuelve a activar contratos retirados.

Las credenciales internas se generan automáticamente y permanecen en un volumen privado. Nuxt agrega la API key desde su servidor; el navegador no la recibe. Para autorizar Swagger, el operador puede consultar su clave local con este comando y pegarla en **Authorize**:

```bash
docker compose exec api cat /clave_api/clave
```

No publicar esa salida. Solo se exponen puertos en localhost. Es una demostración para un operador local; no incorpora cuentas, permisos por inmobiliaria ni acceso público.

Para detener conservando los datos:

```bash
docker compose stop
```

No eliminar los volúmenes si se quiere conservar la biblioteca.

Para reiniciar los contenedores detenidos:

```bash
docker compose start
```

Si cambió el código o todavía no existen los contenedores, ejecutar de nuevo `docker compose up --build`. No hace falta instalar Python, uv, Node ni pnpm en la computadora para usar esta modalidad.

### Problemas comunes

| Problema | Acción |
| --- | --- |
| Docker no puede conectarse al daemon | Abrir Docker Desktop y esperar a que termine de iniciar. Repetir el comando de arranque. |
| Puerto 3000 u 8000 ocupado | Detener la otra aplicación o cambiar `WEB_PORT` y `API_PORT` en `.env`. Ejecutar de nuevo `docker compose up --build` y usar las nuevas direcciones. |
| La web aún no está disponible durante el primer arranque | Consultar `docker compose ps` y `docker compose logs --tail=80 api`. La API descarga el modelo y procesa la demo antes de habilitar la web. Comprobar la conexión a Internet si falla la descarga; después repetir el arranque. |
| La búsqueda no encuentra un contrato cargado | Seleccionar su colección y comprobar que el documento aparece en la biblioteca. Abrir sus páginas y verificar el texto extraído antes de cambiar la consulta. |
| Un escaneo devuelve texto incorrecto o incompleto | Revisar el original y el método de extracción de cada página. El OCR no garantiza leer imágenes borrosas ni todas las composiciones mixtas. Conservar el archivo para diagnosticarlo. |
| El chat A* no está disponible | Comprobar la configuración privada y vigencia de su clave. Usar **Buscar fragmentos** para continuar con el motor local. No se reintenta automáticamente una llamada al proveedor. |

## Activar el chat opcional de A*

1. Guardar la clave de OpenAI en un archivo privado fuera del proyecto. Ese archivo contiene solo la clave y no se incluye en Git ni en la entrega.
2. En `.env`, indicar su ruta absoluta mediante `LUNA_API_KEY_FILE=/ruta/privada/luna.key`. La variable contiene una ruta, nunca la clave.
3. Ejecutar `docker compose up --build`. Compose monta el archivo como secreto únicamente en API. Sin configuración se usa el ejemplo vacío y la búsqueda local continúa disponible.
4. Abrir el modo A*, elegir colección y preguntar. Desplegar las fuentes para revisar el pasaje exacto y abrir el original.

Se usa el modelo `gpt-6-luna`. Cada turno tiene una búsqueda local y hasta dos llamadas a Responses, con salida máxima de 4096 tokens por llamada, timeout de 45 segundos y sin reintentos automáticos. El historial es volátil y se limita a los últimos seis mensajes enviados al backend. OpenAI recibe pregunta, contexto reciente y hasta cinco pasajes recuperados; los archivos no se cargan en otro Store. Las llamadas tienen el costo del proveedor y la aplicación no renueva claves vencidas.

La API utiliza `store=false`; esto no equivale a una garantía de Zero Data Retention. Ver [diseño y límites del chat](docs/16_chat_luna_mvp.md).

## Recorrido

1. Abrir un documento de la biblioteca y revisar sus páginas, texto y método de extracción.
2. Conversar con A* si el chat está configurado, o usar **Buscar fragmentos**. El modelo del chat sigue siendo GPT-6 Luna. Cada fuente enlaza al original y a su página.
3. Alternar búsqueda híbrida, semántica o textual. Las puntuaciones ordenan resultados; no son porcentajes de certeza.
4. Incorporar un PDF o TXT ficticio de hasta 10 MiB mediante arrastre o el botón de adjuntar del compositor.
5. Editar el título o moverlo de colección. Retirarlo aplica baja lógica y lo excluye de consulta y descarga.

Ejemplos: `¿Qué debo pagar si desocupo antes de tiempo el local Cedro?`, `¿Cuándo se devuelve el depósito de la casa Aurora?`, `¿Qué multa corresponde si se entrega tarde el departamento Bruma?`.

### Incorporar documentos

Arrastrar un único archivo sobre la aplicación o usar **Adjuntar documento** en el compositor. El título se toma del nombre sin extensión y puede editarse. Se admiten PDF y TXT no vacíos de hasta 10 MiB; la API conserva la validación del archivo.

| Contexto de la biblioteca | Acción de la interfaz |
| --- | --- |
| Una colección seleccionada | Un archivo válido comienza a indexarse en esa colección. |
| Todas las colecciones, con una única colección disponible | El archivo válido se indexa en ese único destino. |
| Todas las colecciones, con varios destinos disponibles | Elegir colección y pulsar **Indexar documento**. |
| Ninguna colección disponible | Crear una colección antes de indexar. |

Durante la petición se muestra una animación indeterminada. El recorrido «Texto y OCR, Fragmentos, Embeddings, Índice vectorial» explica el procesamiento en PostgreSQL y pgvector; no informa qué etapa está ejecutándose ni simula porcentajes. El éxito se muestra después de la respuesta real de la API.

El [diseño A*](docs/17_diseno_a_asterisco.md) conserva la revisión de temas, móvil, hover y foco. El [cierre B5](docs/07_Evidencias/b5_final/README.md) añade carga TXT/PDF mixto, OCR, cita, original, vacío, errores reales y recuperación. Fernando confirmó la indexación al soltar un archivo; se observó el PDF indexado sin pulsar Indexar. El arrastre múltiple y un segundo arrastre durante carga siguen sin verificación física. La [copia C2 inicial](docs/07_Evidencias/c2_a_asterisco.md) acredita arranque con volúmenes nuevos; B5 reutiliza esos volúmenes aislados y no utiliza OpenAI.

## Arquitectura

1. **Interfaz:** Nuxt y Nuxt UI. Un BFF conserva la clave fuera del navegador y solo permite las rutas del motor.
2. **Servicio:** FastAPI valida entradas, acceso y contratos, y coordina el procesamiento.
3. **Motor:** extracción y OCR, fragmentación por página, embeddings E5 multilingües de 384 dimensiones y recuperación textual, vectorial o RRF.
4. **Almacenamiento:** PostgreSQL con cuatro tablas y pgvector; originales en un volumen privado. La UI solo consume HTTP.

El backend se organiza en módulos pequeños: `extraccion.py`, `embeddings.py`, `motor.py`, `persistencia.py`, `recuperacion.py`, `contratos.py` y `errores/`. `chat.py` y `chat_contratos.py` incorporan el adaptador conversacional opcional, sin nuevas tablas ni microservicios.

## Verificar

Con los contenedores arrancados:

```bash
docker compose exec api python demo/verificar_servicio.py
docker compose cp api:/tmp/servicio_http.json docs/07_Evidencias/servicio_http.json
```

El recorrido ejecuta HTTP real: consultas conocidas, controles de OCR, CRUD, colección vacía, baja lógica y errores de acceso, formato, tamaño y validación. Incorpora documentos de verificación y los retira al final; conserva una colección vacía y los registros históricos. No borra los seis contratos iniciales.

No se mantiene una suite de pruebas unitarias, conforme a las reglas académicas del repositorio. Los scripts y los informes documentan ejecuciones reales y sus resultados. La [evidencia](docs/07_Evidencias/README.md) distingue el primer experimento en memoria de la verificación actual del servicio.

La verificación aislada de OCR y embeddings sigue disponible:

```bash
docker compose exec api python demo/verificar_motor.py
```

Ese comando utiliza Tesseract y guarda su informe dentro del contenedor. Para conservarlo, copiarlo con `docker compose cp`. No reemplaza la verificación de persistencia y HTTP.

## Probar con un corpus mayor

La instancia local tiene una colección adicional con 240 documentos ficticios, 480 páginas OCR y 5559 fragmentos después de la corrección intrapágina. Consultar la [guía de consultas verificadas](docs/11_guia_consultas.md) y la [evaluación ampliada](docs/10_evaluacion_ampliada.md), con sus fallos incluidos.

Esta carga es opcional y no se ejecuta al iniciar Compose desde una instalación nueva. El arranque académico conserva los seis contratos pequeños. Los scripts de `demo/` permiten reconstruir el experimento sin un LLM.

La [comparación con OpenAI Retrieval](docs/12_comparacion_openai.md) es un experimento externo opcional autorizado por Fernando. Usa los mismos originales y preguntas, con una clave temporal fuera del repositorio. El servicio local conserva su funcionamiento independiente de OpenAI. La [matriz de capacidades](docs/13_matriz_capacidades.md) resume oferta, consumo, resultados y prioridades.

## Desarrollo

El backend tiene su propio entorno Python 3.12 administrado con uv; no cambia el entorno de otras materias. Para instalar dependencias de desarrollo:

```bash
uv sync --project backend --group demo
pnpm --dir frontend install --frozen-lockfile
```

Gates: `uv lock --check --project backend`, Ruff desde la raíz del semestre, `uv build --project backend`, y `pnpm --dir frontend lint`, `typecheck` y `build`.

El modo uv aislado del primer experimento usa RapidOCR y tuvo errores en cláusulas del corpus. El servicio utiliza Tesseract, seleccionado mediante controles de fidelidad. Aplica OCR completo cuando una página tiene menos de 60 caracteres nativos y OCR parcial cuando contiene texto nativo e imágenes que ocupan al menos una cuarta parte de la página. Esta heurística no cubre todas las composiciones posibles. La fragmentación respeta páginas y un límite de tamaño; todavía no reconoce cláusulas jurídicas arbitrarias.

## Documentación

[Índice](docs/README.md), [plan académico](docs/06_plan_de_trabajo.md), [proceso](DEVELOPMENT.md), [diseño API](docs/03_API/Diseno_API.md), [datos](docs/02_Datos/DDA.md), [rúbrica](docs/09_matriz_rubrica.md).

La [investigación de mejoras](docs/14_investigacion_y_evolucion.md) relaciona estrategias documentadas con nuestros fallos medidos. El profesor aceptó sustituir el proyecto, confirmado por Fernando el 2 de noviembre de 2026. El [cierre de rúbrica](docs/15_cierre_rubrica.md) distingue pendientes funcionales, demostración y entrega oficial. Para este semestre basta la demo local; OneDrive y correo se atienden al finalizar la app. Todavía no se han realizado.
