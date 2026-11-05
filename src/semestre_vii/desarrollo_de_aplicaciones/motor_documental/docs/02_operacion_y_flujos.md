# Operación y flujos

## Ingesta

1. Seleccionar colección y cargar PDF o TXT.
2. Validar formato y tamaño.
3. Conservar el original con un identificador interno.
4. Extraer texto por página. En PDF mixtos, decidir el tratamiento por página.
5. Aplicar OCR cuando la extracción nativa sea insuficiente.
6. Dividir el texto conservando documento, página y orden.
7. Generar y guardar embeddings junto con los fragmentos.
8. Declarar el documento disponible únicamente si la indexación terminó.

Una detección basada en cantidad de texto es una heurística, no una garantía de calidad. Debe contrastarse con el corpus ficticio.

## Consulta

El usuario escribe una pregunta. El motor recupera fragmentos usando el modo elegido y devuelve referencias. La interfaz permite leer los fragmentos y abrir el original. La respuesta de recuperación no equivale a una interpretación jurídica.

## Gestión

Organizar por colección, consultar información, editar el título y retirar documentos de la búsqueda. Un documento retirado no puede aparecer en resultados ni abrirse por la API pública de consulta.

## Verificación negativa

Probar archivo incompatible, documento vacío, acceso sin API key y un identificador inexistente. Cada caso debe recibir un error seguro y un código HTTP coherente.
