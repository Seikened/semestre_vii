# Cierre de los recorridos de interfaz

Verificación real en Google Chrome del 2 de noviembre de 2026, con la aplicación local y datos ficticios. No se utilizaron respuestas simuladas. Esta evidencia complementa los recibos históricos del backend y de Luna.

## Implementación

Nuxt UI 4.12.0: `UChatMessages`, `UChatMessage`, `UChatPrompt` y `UChatPromptSubmit`. La biblioteca y la gestión utilizan `UModal`, `UForm`, `UFormField`, `UInput`, `USelect`, `UFileUpload`, `UProgress`, `UAlert`, `UAccordion`, `UCheckbox` y botones de la misma librería. Se contrastaron sus contratos con el [código oficial de la versión](https://github.com/nuxt/ui/tree/v4.12.0/src/runtime/components).

Los formularios tienen controles y valores legibles, validación visible y bloqueo del doble envío. La indexación muestra actividad indeterminada durante la petición real, sin inventar porcentajes. La preferencia de movimiento reducido se respeta en CSS. Las citas abren su fuente y permiten acceder al original.

## Recorridos ejecutados

| Acción | Resultado observado |
| --- | --- |
| Crear colección sin nombre | Mensaje visible de campo requerido. |
| Crear `Demo de Fernando` | Colección disponible en el selector; biblioteca inicialmente vacía. |
| Enviar carga con título pero sin archivo | Mensaje `Selecciona un PDF o TXT.`, conservando título y colección. |
| Cargar `Desktop/test.txt` | Documento disponible, una página, cero páginas OCR. |
| Consultar el detalle del TXT | Texto exacto: `Hola, soy Fernando. Esta es una prueba para la materia de aplicaciones.` |
| Editar título del TXT | `Fernando · Prueba TXT` persistido y biblioteca actualizada. |
| Modificar de nuevo el campo después de guardar | El aviso `Cambios guardados` desaparece. |
| Cargar `Desktop/test.pdf` | `Fernando · Prueba PDF`, una página, cero páginas OCR. |
| Cargar `FIC-003_mixto.pdf` | Dos páginas, una OCR; controles bloqueados durante el procesamiento. |
| Abrir página 2 del PDF mixto | Texto OCR de cláusulas 3 y 4, incluida penalización de dos mensualidades y aviso de sesenta días. |
| Enviar un TXT vacío | Error recuperable; título, colección y archivo permanecen visibles. |
| Reemplazar el archivo vacío por un TXT válido | Carga completada sin reconstruir el formulario. |
| Retirar la copia desechable de recuperación | Confirmación previa y baja lógica; permanecen los tres documentos de la demo. |
| Preguntar a Luna por la prueba de Fernando | Respuesta literal correcta con una fuente, `test.pdf`, página 1. El estado pendiente estuvo visible. |
| Preguntar a Luna por la salida anticipada de Cedro | Aviso de sesenta días naturales y penalización de dos mensualidades, con cita a la página 2 OCR del PDF mixto. |
| Plegar fuentes y pulsar la cita `[1]` | Acordeón abierto y fragmento accesible. |
| Abrir el original desde la cita | Visor PDF de Chrome con el texto esperado, página 1 de 1. |
| Buscar penalización de Cedro en modo híbrido | Primer resultado: `FIC-003_mixto.pdf`, página 2, OCR, cláusula esperada. |
| Buscar `expedienteinexistentexyzq123` en modo textual | Cero fuentes, estado `Sin coincidencias` y sugerencia de reformular. |
| Cambiar a una colección vacía | Se retiraron los resultados anteriores; carga de biblioteca seguida de estado vacío. |
| Vista móvil de 390 por 844 | Biblioteca desplegable, fuentes, original, mensaje y envío accesibles. Modal y errores requeridos visibles con botones completos. |
| Consola del recorrido | Sin mensajes de error ni advertencia capturados por Chrome. |

La selección mediante la extensión necesitaba un permiso local adicional. Se utilizó el selector nativo de macOS sin cambiar permisos de Chrome. Esto no requirió modificar la aplicación.

## Capturas

- [Chat con fuente verificable](ui_chat_fuente.jpg).
- [Luna responde con una fuente OCR](ui_luna_ocr.jpg).
- [Original abierto desde la cita](ui_pdf_original.jpg).
- [Procesamiento OCR real](ui_procesamiento_ocr.jpg).
- [Detalle OCR por página](ui_detalle_ocr.jpg).
- [Edición y extracción TXT](ui_detalle_txt.jpg).
- [Error con datos conservados](ui_error_recuperable.jpg).
- [Búsqueda del texto OCR](ui_busqueda_ocr.jpg).
- [Sin coincidencias](ui_sin_coincidencias.jpg).
- [Colección vacía](ui_coleccion_vacia.jpg).
- [Chat móvil](ui_chat_movil.jpg).
- [Formulario y validación móvil](ui_modal_movil.jpg).

## Alcance y límites

Lint, typecheck y build aprobados. Auditor independiente revisó contratos, validación, contraste, estados de carga/error y limpieza de contexto. El último ajuste oscurece el texto de error a `#b42318`, con contraste calculado de 6,38:1 sobre el fondo principal.

Los recorridos acreditan los escenarios enumerados. No constituyen certificación de accesibilidad, validación sobre todos los navegadores, evaluación masiva de respuestas de Luna ni garantía de ausencia de fallos. La revisión del código cubrió el reintento de detalle fallido; ese caso concreto no se forzó en Chrome. No se modificaron backend, esquema, endpoints ni resultados del benchmark.

La colección de esta sesión permanece en la instalación local. La entrega reproducible inicia con los seis contratos ficticios originales, sin clave de Luna ni archivos privados.
