# Objetivos e hipótesis

**Objetivo general.** Diseñar y evaluar un códec autocontenido y reversible para URLs HTTP(S), independiente de cualquier servicio de redirección y basado en principios de minería de patrones y teoría de información.

**Dimensión 1 — longitud:** caracteres y bytes UTF-8 del enlace completo, comparando entrada y propuestas. **Dimensión 2 — QR:** versión mínima, lado en módulos y modo de codificación con ECC M y un método de medición constante entre candidatos.

**Hipótesis de investigación (no demostradas):** diccionarios extraídos de URLs, compactación de gramática y alfabetos QR pueden superar un baseline DEFLATE en ciertos grupos de enlaces. Ninguna compresión reversible reduce todas las entradas; medir expansión y casos adversos.

**Restricciones del laboratorio:** cero red, cero persistencia, sin almacenamiento de enlaces, sin FastAPI, sin secretos. Toda reconstrucción debe ser exacta. El producto y el despliegue se abordarán después de validar el algoritmo.
