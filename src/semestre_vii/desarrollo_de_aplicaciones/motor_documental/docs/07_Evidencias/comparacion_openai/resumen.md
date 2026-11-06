# Comparación de recuperación con OpenAI

Fecha: 2026-11-02T17:21:56.632605-06:00.

Mismos 240 originales y mismas 612 consultas. OpenAI usa búsqueda predeterminada en las tres repeticiones; modo local identifica la referencia comparada. Página@5 de OpenAI: no disponible.

| Formulación | Referencia local | Formato | Casos | Documento@5 local | Documento@5 OpenAI | Cita literal@5 local | Cita literal@5 OpenAI | p50 local ms | p50 OpenAI ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| libre | texto | todos | 68 | 4 | 43 | 3 | 43 | 10.1 | 1332.5 |
| libre | vector | todos | 68 | 67 | 43 | 56 | 43 | 47.1 | 1344.6 |
| libre | hibrida | todos | 68 | 67 | 43 | 56 | 43 | 50.3 | 1321.6 |
| natural_con_folio | texto | todos | 68 | 4 | 50 | 3 | 43 | 9.7 | 1393.9 |
| natural_con_folio | vector | todos | 68 | 67 | 49 | 56 | 43 | 45.3 | 1369.6 |
| natural_con_folio | hibrida | todos | 68 | 67 | 50 | 56 | 43 | 50.1 | 1394.9 |
| precisa | texto | todos | 68 | 68 | 48 | 58 | 43 | 9.2 | 1342.1 |
| precisa | vector | todos | 68 | 34 | 49 | 26 | 43 | 41.3 | 1290.0 |
| precisa | hibrida | todos | 68 | 68 | 48 | 58 | 43 | 47.0 | 1300.9 |
| libre | hibrida | digital | 17 | 17 | 17 | 17 | 17 | 55.0 | 1358.8 |
| libre | hibrida | escaneado | 17 | 17 | 0 | 15 | 0 | 48.1 | 1363.7 |
| libre | hibrida | mixto | 17 | 17 | 9 | 15 | 9 | 48.6 | 1293.0 |
| libre | hibrida | txt | 17 | 16 | 17 | 9 | 17 | 51.1 | 1290.4 |

Cita completa dentro de un solo pasaje o bloque devuelto del archivo esperado. Las unidades de recuperación y tamaños de fragmento pueden diferir entre proveedores. Los tiempos comparan API local con servicio remoto, no hardware ni condiciones idénticas.

Corpus sintético, 68 casos sobre 16 documentos. Sin respuestas generadas, sin medición de razonamiento jurídico y sin extrapolación a expedientes reales.
