# Bitácora de prompts

Cuatro ejemplos reales de la conversación del proyecto, revisados el 2 de noviembre de 2026. Los extractos entre comillas son literales; los planes, ajustes y resultados se sintetizan por separado. Una solicitud de trabajo no se presenta como aprobación de cada detalle técnico posterior.

La fuente primaria es el hilo `01a19a46-1aaa-7072-88b8-67a0a518800d`. Los identificadores de mensaje corresponden a su campo `ordinal`; permiten localizar los intercambios sin incluir la sesión privada en la entrega. Se revisaron solo mensajes de usuario y asistente, excluyendo íntegramente los que contenían credenciales. Los recibos acreditan ejecuciones; no sustituyen aprobaciones previas.

## 1. Sustituir gasolineras y reducir la primera etapa

**Solicitud real:** Fernando descartó gasolineras y pidió un motor inmobiliario. Después delimitó: «Tú crea los contratos ficticios. Todo debe de ser ficticio, nada debe de ser real» y «Ahora conversar con el agente y todo esto, sí, sí es la idea, pero ese es el paso dos».

**Plan mostrado antes del ajuste:** cargar PDF/TXT, extracción y OCR por página, PostgreSQL con pgvector, agente y fuentes. La primera porción proponía FastAPI, Docling sujeto a compatibilidad, dos tablas y unas 350 a 550 líneas. Era una propuesta, no el diseño final implementado.

**Alcance y formato de salida:** primera porción del motor, contratos ficticios y demostración de recuperación con archivo y página; conversación pospuesta. El plan y sus límites se presentaron en texto antes de construir esa porción.

**Revisión y motivo:** Fernando separó recuperación de conversación para comprobar primero una capacidad que todavía no había construido. Se pasó a contratos ficticios, consultas ejecutadas por el asistente y ninguna conexión con Luna. Al leer la rúbrica aparecieron cuatro tablas, CRUD, seguridad y tres contenedores; esa ampliación fue posterior y distinta del presupuesto inicial.

**Autorización conservada:** «Entonces, hagámoslo, por favor». Autoriza el MVP con las restricciones del mismo mensaje. No acredita por sí sola la aprobación previa e íntegra de todas las piezas añadidas después de leer la rúbrica.

**Resultado comprobable:** seis contratos, doce páginas, extracción nativa/OCR y recuperación sin LLM. Ver [emulación](../07_Evidencias/emulacion.md) y [recibo Tesseract](../07_Evidencias/recuperacion_tesseract.json).

**Referencia del chat:** mensajes 11, 196 y 203; lectura de rúbrica comunicada en el 304. Se conserva plan y ajuste de alcance, pero no un registro íntegro de revisión y aprobación de la ampliación académica. Este antecedente no se usa para acreditar esa aprobación.

## 2. Ampliar la prueba y repetirla en OpenAI

**Solicitud real:** probar muchos documentos en español, digitales, escaneados y mixtos, antes de conectar un agente. Fernando precisó después: «Es más, hagamos lo siguiente, no inventemos, carga exactamente ya las mismas pruebas».

**Plan comunicado:** generar 240 documentos ficticios, usar la API existente y medir archivo, página y cita por separado. Para OpenAI se fijaron los mismos originales y preguntas, sin agente conversacional, comprobando primero acceso y condiciones de ejecución. Tras recibir ese plan, Fernando facilitó la pestaña del Store para la evaluación.

**Alcance y formato de salida:** prueba comparativa de recuperación, sin respuestas de un agente. Resultados por consulta, recibos JSON/TSV y matriz de capacidades con ventajas, desventajas y límites, como pidió Fernando.

**Revisión y motivo:** se sustituyó una demostración de seis archivos por un corpus con distractores y respuestas conocidas. Se conservaron hashes, preguntas, citas esperadas y respuestas reales para no escoger ejemplos después de conocer los resultados. Los modos locales no tienen equivalencia directa en OpenAI: allí se repitió la misma configuración, sin reescritura, en las tres filas de referencia local. La API evaluada tampoco aportó un campo nativo de página.

**Autorización conservada:** la petición de repetir exactamente las pruebas y la continuación mediante la pestaña del Store constan en los mensajes 3525 y 3539, con el plan de comparación entre ambas. No hay registro íntegro de aprobación separada del presupuesto y de cada pieza del generador del corpus; no se reconstruye retrospectivamente.

**Resultado comprobable:** 240 originales, 68 casos anotados sobre 16 documentos y tres formulaciones por caso: **204 consultas distintas**. Al cruzarlas con tres modos locales se obtienen **612 peticiones**; OpenAI ejecutó 612 búsquedas con la misma configuración y 612 request IDs distintos. Los otros 224 documentos funcionaron como distractores. Los seis controles sin evidencia son adicionales.

En preguntas libres, el híbrido local recuperó el documento en 67/68 casos y la cita literal completa en 56/68; OpenAI obtuvo 43/68 en ambas medidas. OpenAI recuperó 17/17 citas de TXT frente a 9/17 locales. Son resultados del corpus sintético y de esta configuración, no una superioridad general ni una comparación de respuestas de agentes.

Ver [evaluación ampliada](../10_evaluacion_ampliada.md), [comparación](../12_comparacion_openai.md), [método y procedencia](../07_Evidencias/comparacion_openai/metodo_y_procedencia.json) y [recibos por respuesta](../07_Evidencias/comparacion_openai/recibos_respuestas.tsv).

**Referencia del chat:** solicitud de corpus 2188; planes 2191, 2227 y 2333; petición de igualdad 3525; plan de comparación 3530 y continuación 3539. Las cifras finales proceden de los recibos, no de la estimación inicial.

## 3. Corregir el OCR dentro de una página mixta

**Problema observado:** cuatro PDF tenían encabezado digital y cuerpo en imagen. El extractor consideraba suficiente el encabezado y omitía las cláusulas. La medición inicial se conservó antes de cambiarlo.

**Plan presentado para aprobación:** «El cambio afecta solo backend/app/extraccion.py, unas 15 líneas: detecta imágenes grandes y usa OCR parcial cuando también hay texto digital. Después reindexaría los cuatro PDF ficticios afectados y compararía los resultados».

**Alcance y formato de salida:** cambio acotado del extractor y comparación antes/después de los cuatro PDF. Se conservan la medición inicial y los recibos de integridad, sin extender el esquema ni modificar los demás documentos.

**Aprobación literal de Fernando:** «Sí, aplicar y verificar la corrección».

**Ajuste y motivo:** detectar imágenes visibles que ocupan al menos el 25 % de la página y aplicar OCR parcial cuando existe texto nativo. Se mantuvieron fragmentación, embeddings, esquema y contratos HTTP. La estimación de 15 líneas corresponde al extractor, no a toda la reindexación y documentación.

**Resultado comprobable:** se reindexaron los cuatro PDF y se recuperaron 16 páginas antes omitidas. Las páginas OCR pasaron de 464 a 480; en preguntas libres híbridas, página correcta@5 pasó de 63/68 a 67/68 y cita literal completa@5 de 52/68 a 56/68. Se repitieron las mismas 612 consultas. Los otros 236 documentos conservaron su contenido y pasaron 78/78 comprobaciones HTTP.

Ver [SC-001](../05_Cambios/solicitudes_cambio.md), [verificación posterior](../07_Evidencias/corpus_amplio/verificacion_ocr_parcial.md), [comparación antes/después](../07_Evidencias/corpus_amplio/comparacion_ocr_parcial.json) e [integridad](../07_Evidencias/corpus_amplio/integridad_ocr_parcial.json).

**Referencia del chat:** el mensaje 3029 conserva la pregunta completa con archivo, alcance, estimación, reindexación y comparación, seguida de la respuesta explícita. El 3032 comunica el inicio después de aprobarse; el 3471 informa el resultado. Este ejemplo conserva plan y aprobación verificables.

## 4. Conectar el chat MVP con Luna

**Solicitud real actual:** Fernando pidió convertir Nuxt en un chat funcional con el agente de OpenAI, basándose en documentación oficial y reutilizando el sistema, como MVP. También pidió trabajo en paralelo por áreas.

**Plan presentado antes de aprobarse:** GPT-6 Luna mediante Responses, herramienta `buscar_documentos` sobre la búsqueda local con pgvector y un `POST /chat`. Límite de una búsqueda y dos llamadas a Responses por turno; sin nuevas tablas ni otro Store. Presupuesto de 450 a 650 líneas entre backend y frontend.

**Piezas incluidas en el plan:** `backend/app/chat.py`, `chat_contratos.py`, ajustes de `main.py`, configuración y errores, SDK y secreto de Compose. En frontend: `app.vue`, componente de chat, tipos y ruta BFF. La credencial permanece en backend y fuera del código y la entrega.

**Alcance y formato de salida:** chat MVP y fuentes comprobables, sin nuevas tablas ni carga al Store gestionado. El contrato implementado devuelve `respuesta`, `resultado` y `modelo`; la entrega conserva código, documentación y evidencia separada de la aprobación.

**Aprobación literal de Fernando:** «Sí, implementar y probar el MVP».

**Ajuste y motivo:** adelantar la segunda etapa por petición expresa, reutilizando la recuperación existente como herramienta. El modelo redacta a partir de fuentes locales; recuperar un pasaje y generar una respuesta requieren verificaciones distintas. En la ejecución inicial formuló una consulta demasiado larga para SIM0170 y recuperó otros contratos. Se ajustaron las instrucciones a folio y concepto en una consulta breve, conservando el caso fallido y repitiéndolo.

**Estado real:** implementado y verificado mediante HTTP y Chrome. Cinco casos documentales recuperaron la fuente y página esperadas; se comprobó seguimiento y una pregunta sin evidencia. Hubo un 503 en la conexión con Luna antes del reintento manual de esta última, conservado en el recibo; su causa no se identificó. También se comprobó una instalación sin clave y recuperación local disponible. La prueba pequeña no demuestra fidelidad universal ni disponibilidad perfecta. Ver [evidencia del MVP](../07_Evidencias/luna_mvp.md).

**Referencia del chat:** solicitud en mensajes 5060, 5062 y 5064, y organización en el 5067. El plan concreto y su respuesta se conservan en la pregunta de aprobación del turno actual. No se asigna un ordinal que aún no se haya cotejado con el registro.

## Cierre documental de C3

Hay cuatro ejemplos con propósito, plan disponible, ajuste, motivo, autorización y resultado. Los ejemplos 2, 3 y 4 permiten revisar respectivamente la comparación, el cambio OCR y el MVP conversacional; el primero conserva el antecedente y sus límites. Los vacíos históricos permanecen explícitos. La bitácora queda preparada para revisión académica; la exposición y la aceptación del profesor se acreditan por separado.
