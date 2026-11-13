# Resultados del laboratorio

El primer entregable establece el ejecutable local y las métricas, pero **no declara superioridad estadística** sobre otros compresores. Registrar cada experimento con fecha, muestras, parámetros, resultado de recuperación, caracteres, bytes y versión QR de original/Base64/Base32.

## Limitaciones de medición

El estimador QR usa capacidad de datos por versión ISO/IEC 18004 para nivel de corrección M, y selecciona **un solo modo** (alfanumérico si todos los caracteres caben; de lo contrario byte UTF-8), sin optimización de segmentos mixtos ni ECI. Si excede la capacidad de la versión 40, reporta valores nulos de versión y módulos. Esto aproxima el tamaño de símbolos sin generar QR físicos; la siguiente iteración debe contrastar con un codificador completo. Las rutas `/c/` o `/C/` mostradas son simuladas.

## Próxima evaluación

Construir un conjunto con URLs reales públicas anonimizadas y muestras adversas. Mantener separados entrenamiento de diccionarios y evaluación. Medir percentiles y porcentaje de casos donde el enlace resultante crece.

## Primera ejecución local — 12 de noviembre de 2026

Entrada: `https://www.example.com/productos?id=12345`.

| Representación | Caracteres | Bytes UTF-8 | QR M (un modo) |
| --- | ---: | ---: | --- |
| Original | 42 | 42 | v3, 29×29, byte |
| Enlace simulado Base64 URL-safe | 69 | 69 | v5, 37×37, byte |
| Enlace simulado Base32 QR | 78 | 78 | v4, 33×33, alfanumérico |

Los dos tokens recuperaron exactamente la entrada. **En este caso el baseline expande el enlace**: es un resultado válido e importante. El overhead de dominio, ruta, cabecera y alfabeto aún supera el ahorro. En una verificación local adicional pasaron 418 reconstrucciones de muestra y 500 comparaciones de versión QR frente a un generador que forzó el mismo modo; falta correr los gates del repositorio completo en su entorno académico.
