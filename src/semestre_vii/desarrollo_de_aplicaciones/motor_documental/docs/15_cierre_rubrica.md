# Cierre de rúbrica y pendientes

Revisión del 2 de noviembre de 2026 contra las cuatro páginas de la [rúbrica original](Segundo_Parcial_Criterios_Evaluacion.pdf). Esta lista responde a «¿qué le falta a la app?». Un artefacto preparado no equivale a puntos otorgados; la calificación corresponde al profesor.

## Datos confirmados

- Fernando León Franco, matrícula 192488-7.
- El profesor aceptó sustituir gasolineras por el motor documental inmobiliario.
- Exposición en vivo: **4 de noviembre de 2026, 17:00**, hora de America/Mexico_City.
- Duración: diez minutos, con el [guion](08_Presentacion/guion.md) como archivo de apoyo.
- Para este semestre basta la demo local. No se requiere hosting público ni Docker Hub.
- OneDrive y correo se atienden después del cierre funcional, con indicación específica de Fernando.
- El PDF exige recepción por correo estudiantil antes del **4 de noviembre de 2026 a las 19:00**. Exponer no sustituye enviar.

## Checklist punto por punto

«Preparado» significa que existe un artefacto revisable y evidencia identificada. En B5 y C2 se distingue el cierre anterior del incremento A*. D1 a D3 requieren ejecución de Fernando.

| ID | Puntos | Qué pide | Evidencia concreta | Estado y acción pendiente |
| --- | --- | --- | --- | --- |
| A1 | 4 | C4 nivel 1: usuario, sistema y externos, sin detalles técnicos. | [Editable](01_Arquitectura/C4_Contexto.drawio), [PNG](01_Arquitectura/C4_Contexto.png). | Preparado. Explicarlo entre 0:45 y 1:30. |
| A2 | 6 | DAR: frontend, API, ML, base, red y protocolos. | [Editable](01_Arquitectura/DAR_Arquitectura.drawio), [PNG](01_Arquitectura/DAR_Arquitectura.png), [arquitectura](05_arquitectura.md). | Preparado. E5 dentro de API, OpenAI externo opcional, SQL privado, HTTP local y HTTPS saliente. |
| A3 | 7 | DER y diccionario con al menos cuatro tablas, llaves y restricciones. | [DER](02_Datos/DER.png), [editable](02_Datos/DER.drawio), [DDA](02_Datos/DDA.md). | Preparado. Explicar colección, documento, página y fragmento. |
| A4 | 3 | Índice y vista PostgreSQL justificados. | [SQL de entrega](02_Datos/objetos_bd.sql), [recibo PostgreSQL](07_Evidencias/postgres_objetos.txt). | Preparado. GIN textual y vista de documentos disponibles; no afirmar HNSW. |
| A5 | 5 | Endpoints, códigos y seguridad. | [Diseño API](03_API/Diseno_API.md), [negativa actual](07_Evidencias/revision_rubrica_actual.json). | Preparado. Distinguir API key, validación y CORS de autenticación multiusuario, que no existe. |
| B1 | 5 | Instrucciones permanentes equivalentes a CLAUDE.md. | [AGENTS](../AGENTS.md), [proceso](../DEVELOPMENT.md), [README](../README.md). | Preparado. Reglas, stack, carpetas y comandos documentados. |
| B2 | 7 | Frontend, API y base en contenedores separados. | [Compose](../docker-compose.yml), [DAR](01_Arquitectura/DAR_Arquitectura.png). | Verificados activos en esta revisión: API y PostgreSQL saludables, web HTTP 200. |
| B3 | 9 | Al menos cinco endpoints, CRUD, reglas y negativa. | [OpenAPI](03_API/openapi.json), [78 controles HTTP anteriores](07_Evidencias/servicio_http_luna.json), [401 actual](07_Evidencias/revision_rubrica_actual.json). | Once operaciones en OpenAPI. Demostrar crear, leer, editar y retirar la copia ficticia. |
| B4 | 6 | Swagger/OpenAPI con contratos, ejemplos y respuestas. | [Swagger local](http://localhost:8000/docs), [exportación](03_API/openapi.json). | Swagger HTTP 200 y exportación idéntica al servicio actual. Abrirlo durante la demo. |
| B5 | 8 | UI real conectada, diseño y estados vacío/error. | [Cierre B5](07_Evidencias/b5_final/README.md), [diseño A*](17_diseno_a_asterisco.md). | Verificado en el alcance de la rúbrica: carga TXT/PDF mixto, OCR, fuente y original, vacío, errores reales y reintento. Dos fallos de interfaz corregidos. Arrastre simple confirmado por Fernando; dos gestos adicionales siguen sin verificación física. |
| B6 | 5 | SC-001 documentada e implementada por capas. | [Solicitud](05_Cambios/solicitudes_cambio.md), [OCR mixto](07_Evidencias/ui_detalle_ocr.jpg), [corrección intrapágina](07_Evidencias/corpus_amplio/verificacion_ocr_parcial.md). | Implementada y con evidencia anterior. Mostrar carga mixta, métodos por página y cláusula recuperada. |
| C1 | 4 | Estructura completa en OneDrive estudiantil y permiso al profesor. | [Índice de entrega](00_LEEME.md). | Pendiente por decisión de Fernando. No se ha compartido ni enviado. |
| C2 | 9 | Copia independiente que arranque siguiendo README con Docker Desktop. | [README](../README.md), [copia actual A*](07_Evidencias/c2_a_asterisco.md). | Regenerado y arrancado con volúmenes nuevos, seis contratos y búsqueda local; sin clave OpenAI. El recibo final acompaña al ZIP. Windows no verificado. |
| C3 | 7 | Tres a cinco prompts, contexto, restricciones, salida, plan y ajustes. | [Cuatro ejemplos reales](06_IA/bitacora_prompts.md). | Preparado. Se declaran registros históricos incompletos; no se inventan aprobaciones ni prompts retrospectivos. |
| D1 | 6 | Flujo completo, SC-001 y negativa en vivo. | [Guion, 3:15 a 7:45](08_Presentacion/guion.md). | Pendientes ensayo y presentación de Fernando. |
| D2 | 5 | Explicar C4, DAR y conexión frontend/API/base. | [Guion, 0:45 a 3:15](08_Presentacion/guion.md). | Material preparado; exposición pendiente. |
| D3 | 4 | Diez minutos, preguntas y comprensión del trabajo. | [Cronograma y respuestas](08_Presentacion/guion.md). | Pendiente ensayo real con cronómetro y respuestas de Fernando. |

Total oficial: **100 puntos**. No se calcula una nota sumando artefactos o afirmaciones del asistente. Los bloques son A: 25, B: 40, C: 20 y D: 15.

## Pendientes que todavía afectan el cierre técnico

- [x] Verificar B5 contra la API real: carga, OCR, cita, original, vacío, error y recuperación; conservar capturas y corregir los fallos encontrados.
- [x] Registrar la confirmación de Fernando sobre indexación al soltar un archivo y el PDF indexado observado, sin atribuirlo a un arrastre automatizado.
- [ ] Verificación adicional de interacción: rechazo de un arrastre múltiple y segundo arrastre durante una carga. Las guardas están implementadas; no se logró observar la entrega de esos gestos. No se presentan como pruebas aprobadas ni son requisitos explícitos de B5.
- [x] Regenerar el paquete académico con la interfaz, documentación y guion actuales.
- [x] Extraer una copia independiente, arrancar con redes y volúmenes nuevos y conservar el recibo de consultas de A*. La cláusula de Cedro aparece en posición 2.
- [x] Revisar el contenido del paquete para excluir claves, `.env` real, dependencias, caches y volúmenes. Conservar manifiesto junto al ZIP.
- [ ] Comprobar disponibilidad del chat antes de exponer. La clave temporal puede vencer; la búsqueda local sigue siendo independiente.

La UI A* pasó lint, typecheck y build en su incremento. En esta revisión se comprobaron HTTP 200 de web/salud/Swagger, once operaciones y rechazo 401 sin clave. Estos controles de lectura no vuelven a acreditar todo el CRUD ni el chat. Ver [recibo actual](07_Evidencias/revision_rubrica_actual.json).

La [copia C2 inicial de A*](07_Evidencias/c2_a_asterisco.md) acredita arranque con volúmenes nuevos y seis contratos. El [cierre B5](07_Evidencias/b5_final/README.md) utiliza esa instalación aislada, sin clave OpenAI, y añade tres documentos ficticios. Se conservan por separado la prueba inicial, los fallos encontrados y su corrección. Los dos gestos adicionales pendientes no impiden comprobar los estados vacío y error solicitados por la rúbrica; tampoco permiten afirmar cobertura total de la interfaz.

## Pendientes de Fernando y entrega oficial

- [ ] Ensayar la vuelta de diez minutos con carga mixta, consulta, fuente, edición/retiro y negativa.
- [ ] Explicar las cuatro tablas y la ubicación de E5, pgvector y GPT-6 Luna.
- [ ] Presentar el 4 de noviembre a las 17:00 y responder preguntas.
- [ ] Cuando termine el cierre funcional, indicar que se prepare la carpeta OneDrive estudiantil `192488-7_Leon_Fernando_2P` y se comparta con permiso de lectura al profesor.
- [ ] Enviar desde el correo estudiantil a `28008@iberoleon.edu.mx` antes del 4 de noviembre a las 19:00, con enlace, nombre del proyecto y URL local.
- [ ] Conservar el recibo del envío y comprobar que el profesor puede abrir la carpeta.

Las nueve secciones oficiales son `00_LEEME.md` y las carpetas `01_Arquitectura` a `08_Presentacion`. El código ejecutable completo debe quedar en `04_Codigo`, con `frontend/`, `api/`, `db/`, Compose, `.env.example`, instrucciones y README.

## Alcance que se explica como MVP

La denominación es **A*: motor documental modular con OCR, vectorización local, búsqueda híbrida y respuestas con fuentes**. El [alcance](01_producto_y_alcance.md) describe capacidades y límites actuales.

WhatsApp oficial, R2, acceso multiusuario, reranking y mejoras de contexto son evolución posterior. El servicio actual tiene un canal web. No se presenta como motor multicanal terminado, asesor jurídico ni sistema infalible.

La rúbrica acepta tecnologías distintas, instrucciones equivalentes a CLAUDE.md y formato libre. No exige despliegue público, imagen publicada en Docker Hub, un modelo entrenado desde cero ni una versión final del producto. El docente evalúa rigor, estructura, evidencia y comprensión.

Si la copia no levanta siguiendo README, el PDF limita C2 a Insuficiente y B3/B5/B6 a un máximo del 50 %. Por eso la comprobación del paquete es un requisito de cierre, no una formalidad.
