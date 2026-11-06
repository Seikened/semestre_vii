# Emulación de consulta

El asistente ejecutó el verificador y revisó las fuentes devueltas. No se conectó GPT-6 Luna ni otro modelo conversacional. La recuperación utiliza embeddings locales reales.

## Salida anticipada del local Cedro

**Consulta:** ¿Qué debo pagar si desocupo antes de tiempo el local Cedro?

El motor recuperó `FIC-003_mixto.pdf`, página 2, en segunda posición. La evidencia dice: “Salida anticipada: debe avisarse con sesenta días naturales de anticipación. La penalización equivale a dos mensualidades de renta”.

**Respuesta sustentada en el contrato ficticio:** la cláusula indica una penalización de dos mensualidades y un aviso de sesenta días naturales. Esta lectura procede del fragmento recuperado, no de una respuesta predefinida dentro del buscador.

## Retraso de entrega de Bruma

**Consulta:** ¿Qué multa corresponde si se entrega tarde el departamento Bruma?

El motor recuperó `FIC-002_escaneado.pdf`, página 2, en primera posición. La cláusula fija 1500 pesos ficticios por día de retraso, hasta veinte días.

## Apartado de Estela

**Consulta:** ¿Se recupera el apartado de Estela si hay problemas con los papeles de propiedad?

El motor recuperó `FIC-005_escaneado.pdf`, página 2, en primera posición. La cláusula indica devolución íntegra si la documentación de propiedad presenta inconsistencias antes del vencimiento.

## Alcance de la evidencia

Todos los documentos, partes, inmuebles e importes son inventados. El informe `recuperacion_tesseract.json` conserva las seis consultas y los fragmentos devueltos. La verificación no acredita todavía una conversación conectada, una API ni consultas sobre documentos reales.
