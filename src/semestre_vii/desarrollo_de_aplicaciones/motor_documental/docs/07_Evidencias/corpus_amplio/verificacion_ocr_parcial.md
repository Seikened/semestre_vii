# Verificación de la corrección OCR intrapágina

Ejecución local del 2 de noviembre de 2026, después de autorización expresa de Fernando.

| Comprobación | Resultado |
| --- | --- |
| `uv lock --check` desde la raíz | Correcto, 87 paquetes. |
| `uv run ruff check .` desde la raíz | Correcto. |
| `uv build` desde la raíz | sdist y wheel construidos. |
| `uv lock --project backend --check` desde el producto | Correcto, 127 paquetes. |
| `uv build --project backend` desde el producto | sdist y wheel construidos. |
| `docker compose up -d --build api` | Imagen reconstruida y API saludable; PostgreSQL y web conservados. |
| Reindexación por HTTP | Solo cuatro PDF previstos; 16 páginas antes omitidas procesadas con OCR. |
| Evaluación ampliada | Mismo manifiesto y mismas 612 consultas; ver comparación e informes separados. |
| Integridad por HTTP | 236 detalles idénticos, 16 páginas nativas idénticas y cuatro hashes originales correctos. |
| `demo/verificar_servicio.py` | 78/78 comprobaciones, recibo separado. |
| `demo/verificar_motor.py`, función verificar con Tesseract y destino separado | Ocho controles OCR y seis fuentes esperadas en top 5, con nueva extracción de los seis PDF iniciales. |
| Chrome | Consulta textual SIM0170, cláusula de reparaciones: 5100 pesos ficticios, página 4, OCR y vínculo al original. |

La revisión independiente se registra en `../../revision_codigo.md`. No se conectó un LLM ni se modificaron fragmentación, embeddings, contratos HTTP o esquema de datos.
