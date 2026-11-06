# Interfaz de consulta

**Estado:** incremento A* implementado en `../frontend/`. La [referencia visual](17_diseno_a_asterisco.md) y el [cierre B5](07_Evidencias/b5_final/README.md) registran los recorridos reales y sus límites. La [evidencia anterior](07_Evidencias/ui_pulida.md) conserva su alcance histórico.

El proyecto declara y utiliza `@nuxt/ui` 4.12.0. Las APIs se contrastan con el [código oficial de esa versión](https://github.com/nuxt/ui/tree/v4.12.0/src/runtime/components), no solo con documentación de versiones posteriores.

## Pantalla

La marca visible es A*, tanto en la biblioteca como en el chat. La interfaz utiliza los colores neutros observados en ChatGPT y tokens de hover, bordes, foco, radios y estados del sistema público OpenAI Apps SDK UI, adaptados a Nuxt UI. Permite alternar tema claro y oscuro. GPT-6 Luna se conserva como nombre técnico del modelo conversacional.

Una biblioteca lateral organiza colecciones y documentos. La zona principal recibe consultas y presenta fragmentos, contrato, página y acceso al original. El compositor permite adjuntar un archivo y toda la aplicación recibe el arrastre de documentos.

## Carga de documentos

- Admitir un PDF o TXT por operación, no vacío y de hasta 10 MiB. Rechazar la selección múltiple sin enviar archivos.
- Completar el título con el nombre del archivo sin extensión; conservar la posibilidad de editarlo.
- Con una colección seleccionada, iniciar la indexación del archivo válido. En **Todas las colecciones**, hacer lo mismo únicamente si existe un solo destino.
- Si hay varios destinos en **Todas las colecciones**, solicitar la colección y esperar **Indexar documento**. Si no hay ninguna, pedir crear una colección.
- Bloquear nuevos envíos durante una operación y conservar los datos ante errores para corregirlos o reintentar.

La selección de destino es estado de interfaz. La carga sigue usando el contrato HTTP existente y la API mantiene la validación autoritativa.

## Componentes

- `UChatPrompt` y `UChatPromptSubmit` para la consulta.
- `UChatMessages` y `UChatMessage` para mantener el historial de consultas y evidencias.
- `UModal`, `UForm` y `UFormField` para gestión y validación.
- `UFileUpload`, `UInput`, `USelect`, `UCheckbox`, `UButton`, `UProgress`, `UAlert` y `UAccordion` para carga, edición, actividad, avisos y detalle por página.

La búsqueda directa conserva los fragmentos recuperados sin generación. El modo A* utiliza el chat opcional de GPT-6 Luna mediante Responses y devuelve respuesta y fuentes del mismo motor. Ambos modos utilizan texto escapado. Este incremento no cambia agente, backend, HTTP, esquema ni modelo; la UI no requiere AI SDK ni streaming para el contrato JSON actual.

## Estados

Carga y procesamiento, documento disponible, biblioteca vacía, búsqueda sin coincidencias y error recuperable. Un fallo conserva la última información válida y permite reintentar sin fingir que el envío funcionó.

La indexación es síncrona: el servicio no informa porcentajes ni etapas parciales. Mostrar una animación indeterminada solo durante la petición real. El pipeline estático «Texto y OCR, Fragmentos, Embeddings, Índice vectorial» explica las operaciones y su almacenamiento en PostgreSQL y pgvector, sin marcar una etapa como activa mediante temporizadores. El éxito se comunica únicamente al recibir el documento indexado y sus datos reales. Respetar la preferencia de movimiento reducido.

## Frontera

El servidor Nuxt llama a la API mediante configuración privada. El navegador no recibe API keys, rutas internas ni acceso directo a la base. La interfaz consume el contrato HTTP y no reconstruye reglas del motor.

## Verificación del incremento A*

Se verificaron carga TXT y PDF mixto, título manual conservado, rechazo de archivo vacío y PDF inválido, biblioteca vacía, consulta sin coincidencias, error real de servicio y reintento. La búsqueda recuperó la página OCR y abrió el original en la página 2. Se corrigieron un aviso de archivo obsoleto y la pérdida de la biblioteca al fallar una actualización. Ver [capturas y resultados B5](07_Evidencias/b5_final/README.md).

Fernando confirmó el arrastre simple con indexación al soltar; también se observó el PDF indexado sin pulsar Indexar. No se atribuye ese resultado a un gesto automatizado. Arrastre múltiple y segundo arrastre durante carga siguen sin verificación física. La selección por extensión de Chrome requiere un permiso que no se cambió; el selector nativo permitió las cargas verificadas.
