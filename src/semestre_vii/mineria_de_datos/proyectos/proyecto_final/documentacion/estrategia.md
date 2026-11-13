# Estrategia técnica

## A. Primer prototipo (implementado)

1. Conservar bytes UTF-8 exactos de la URL validada, **sin normalizar** ni eliminar información.
2. Sustituir solo prefijos explícitos por un identificador (`https://www.`, `https://`, `http://www.`, `http://`; fallback literal).
3. Compactar el cuerpo mediante DEFLATE si es más pequeño; de lo contrario, usar cuerpo literal.
4. Construir cabecera binaria `versión=01` + `modo` (bit 7=DEFLATE, bits 0–6=índice del prefijo). Rechazar versiones y modos desconocidos.
5. Codificar el mismo binario como `u` + Base64 URL-safe sin padding o `Q` + Base32 mayúscula sin padding. Ambos incluyen etiqueta de alfabeto y deben ser reversibles.
6. Evaluar **enlaces completos simulados** con los dos alfabetos; medir tamaño y QR (ECC M, modo único). El QR alfanumérico exige que todos los caracteres, incluido host y ruta, estén en su alfabeto.

## B. Investigación futura (no implementada)

Corpus trazable y sanitizado → análisis de frecuencia por componente (esquema, host, TLD, segmentos, query) → tokenizador y diccionario estable versionado → algoritmo estadístico (Huffman primero; ANS opcional) → evaluación de entropía, overhead, latencia y resultado QR. Diseñar un fallback cuando comprimir aumente la longitud.

**Regla:** mejoras tienen que compararse con el baseline en datos no utilizados para construir el diccionario, sin romper `round-trip`. La longitud del token **no basta**: el dominio y la ruta simulados también cuentan.
