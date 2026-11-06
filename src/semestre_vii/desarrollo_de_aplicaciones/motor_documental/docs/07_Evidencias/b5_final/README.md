# Cierre B5: interfaz conectada, vacío y error

Recorrido en Chrome del 2 de noviembre de 2026, America/Mexico_City. Se utilizó la copia Docker `motor-documental-c2-a-asterisco`, web 3100 y API 8100, sin clave ni llamadas a OpenAI. No se modificaron los documentos de la instalación principal. Los volúmenes se reutilizaron de la prueba C2 inicial; no se presenta este recorrido como un nuevo arranque desde cero.

## Resultados observados

| Caso | Resultado | Captura |
| --- | --- | --- |
| Colección nueva | Cero documentos y mensaje de biblioteca vacía. | [01](01_biblioteca_vacia.jpg) |
| TXT de cero bytes | Rechazo local, datos conservados y ninguna indexación. | [02](02_archivo_vacio.jpg) |
| TXT válido y título manual | Petición real, una página digital y título conservado; el borrador de consulta permanece al cerrar. | [04](04_indexacion_txt.jpg), [05](05_txt_indexado.jpg) |
| PDF con carga automática | Se observó `04_prueba.pdf` indexado, una página digital, sin pulsar Indexar. Fernando confirmó que el arrastre simple indexa al soltar. No se atribuye a un gesto automatizado. | [06](06_pdf_arrastrado_indexado.jpg) |
| Búsqueda con API detenida | Aviso seguro, pregunta conservada y botón Reintentar. | [07](07_busqueda_error_pregunta_conservada.jpg) |
| API restablecida | Los botones de reintento recuperan biblioteca y consulta sin recargar la página. | [09](09_reintento_recuperado.jpg) |
| Consulta textual inexistente | Cero fuentes y estado Sin coincidencias, distinto del error de servicio. | [10](10_busqueda_sin_coincidencias.jpg) |
| Biblioteca con API detenida, versión corregida | Alerta de actualización fallida junto al nombre de la colección y los dos documentos previamente cargados. | [11](11_error_biblioteca_datos_conservados.jpg) |
| Detalle con API detenida y recuperada | Error con Reintentar apertura; al restaurar API el mismo botón carga páginas, edición y original. | [12](12_error_detalle_reintentar.jpg), [14](14_detalle_recuperado.jpg) |
| Error en móvil | A 390 por 700 se ven mensaje y acciones; después se restauró el viewport. | [13](13_error_detalle_movil.jpg) |
| Sustituir TXT vacío por válido | Desaparecen alerta y error de campo; título manual y colección se conservan. | [15](15_archivo_reemplazado_sin_aviso_obsoleto.jpg) |
| Falso PDF de 50 bytes | La API rechaza el contenido; aviso seguro, datos conservados y reintento habilitado. | [16](16_pdf_invalido_error_backend.jpg) |
| Sustituir por PDF mixto | El error desaparece y se procesa la petición: dos páginas, una OCR. | [17](17_indexacion_mixto.jpg), [18](18_mixto_indexado.jpg) |
| Procedencia y búsqueda híbrida | Página 1 digital, página 2 OCR. `Cedro salida anticipada` recupera el mixto con la cláusula de dos mensualidades y aviso de sesenta días. | [19](19_detalle_pagina_ocr.jpg), [20](20_busqueda_mixto_fuente_ocr.jpg) |
| Original citado | El enlace abre el PDF en la página 2; se contrastó la cláusula contra la imagen. | [21](21_original_pagina_2.jpg) |

La colección `Cierre B5, documentos ficticios` terminó con tres documentos; la copia aislada tiene nueve en total, incluidos los seis iniciales. [recorridos.json](recorridos.json) conserva las observaciones. `recorridos_parciales.json` es un registro intermedio anterior a las correcciones.

## Correcciones verificadas

- `frontend/app/components/DocumentoModal.vue`: volver a validar al cambiar el archivo limpia el aviso obsoleto. La [captura 03](03_aviso_obsoleto_antes.jpg) conserva el fallo anterior; la 15 muestra la corrección.
- `frontend/app/app.vue`: una actualización fallida conserva las últimas colecciones y documentos válidos, con su alerta. Solo se recuperan documentos si no cambió la colección durante la petición. La [captura 08](08_error_biblioteca_antes.jpg) conserva el fallo anterior; la 11 muestra la corrección.

Lint, typecheck y build de producción aprobaron ambos cambios. Se ejecutaron en la copia compilada. No se cambiaron API, BFF, base, procesamiento ni modelo, y no se añadió una suite de tests.

## Límites explícitos

Se verificaron los estados conectado, carga, éxito, vacío, error y recuperación que pide B5. Esto no equivale a cobertura total de la aplicación ni a una calificación otorgada.

No se logró observar la entrega de un arrastre múltiple ni un segundo arrastre durante una indexación. Sus guardas existen en el código, pero estos dos recorridos adicionales permanecen sin comprobar. Tampoco se ejecutaron en este cierre el límite de 10 MiB, una extensión no admitida o el caso de Todas las colecciones con un único destino.

La extensión de Chrome no permitió adjuntar por su API de archivos. No se cambió el permiso; las cargas verificadas utilizaron el selector nativo. Chrome cambió de sesión durante el recorrido y Fernando autorizó continuar cuando dejó libre la ventana. No se alteraron sus ajustes de privacidad ni seguridad.

La animación de indexación indica actividad real de la petición. La API síncrona no publica porcentaje ni etapa intermedia. La disponibilidad del chat con proveedor se verifica por separado; aquí se comprobó el motor local sin consumo de OpenAI.
