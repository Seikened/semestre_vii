# Evaluación ampliada sin LLM

## Propósito

Medir recuperación y fidelidad de citas con un archivo mayor, antes de conectar GPT-6 Luna. La carga usa HTTP y PostgreSQL reales. La verdad de referencia se genera antes de extraer los documentos.

## Corpus

240 documentos completamente ficticios, semilla `20261102`:

| Formato | Documentos | Páginas lógicas |
| --- | --- | --- |
| PDF digital | 120 | 960 |
| PDF escaneado | 40 | 320 |
| PDF mixto | 40 | 320 |
| TXT UTF-8 | 40 | 40 |
| Total | 240 | 1640 |

Cada PDF tiene ocho páginas. Los TXT son archivos continuos, por lo que la API los identifica como página 1. Se incluyen arrendamientos, compraventas, administración y escrituras simuladas. Nombres, propiedades, cantidades y operaciones del corpus son ficticios; Fernando León Franco y Fabián León Franco participan exclusivamente como personajes de la simulación solicitada.

Los distractores incluyen propiedades con nombres similares, cambios de roles y cláusulas con importes y plazos diferentes. Hay escaneos a 110 dpi y cuatro PDF mixtos con encabezado digital y cuerpo en imagen. Los restantes escaneos se generan a 160 dpi. No se simulan todas las condiciones de una digitalización real.

Los archivos y su manifiesto se conservan en `data/desarrollo_de_aplicaciones/evaluacion_documental/`, fuera de Git por ser reconstruibles. Los scripts viven en `demo/`. El corpus generado ocupa aproximadamente 67 MB.

## Referencias investigadas

[3CEL](https://arxiv.org/abs/2501.15990) aporta 373 licitaciones anotadas en español y 19 categorías. [RISC](https://github.com/GRAAL-Research/risc) genera contratos sintéticos de seguros en francés e inglés. Son referencias de investigación útiles. Para este experimento se utiliza texto propio en español, completamente ficticio y con respuestas conocidas.

No se copiaron sus contratos ni se incorporaron expedientes reales.

## Diseño de la evaluación

68 casos sobre 16 de los 240 documentos, con 17 casos por formato. El resto funciona como distractor. No son 240 contratos con relevancia anotada por una persona independiente.

Cada caso se consulta de tres formas:

1. Libre: pregunta por la propiedad y el tema, sin folio.
2. Natural con folio: la misma pregunta identifica además el expediente.
3. Precisa: folio y título de la cláusula. Es una consulta dirigida con conocimiento del documento; no representa descubrimiento libre.

Se ejecutan los modos textual, vectorial e híbrido, con límite 5. En total son 612 consultas. Los casos y sus variantes quedan fijados antes de medir la recuperación.

## Qué mide cada resultado

- Documento@5: el archivo esperado aparece entre los cinco primeros pasajes.
- Página@5: aparecen archivo y página esperados.
- Cita completa en un pasaje@5: un pasaje de esa página conserva toda la cita esperada.
- Cita disponible en la página: la extracción completa conserva la cita, aunque la fragmentación la haya separado.
- MRR página@5: promedio del inverso de la posición de la página esperada, con cero si no aparece en los primeros cinco.
- p50 y p95: latencia de solicitudes seriales a la API interna, sin LLM. No representan concurrencia ni tiempos de WhatsApp.

La comparación literal conserva mayúsculas, acentos y puntuación; solo unifica espacios. La comparación normalizada elimina además diferencias de mayúsculas, acentos y puntuación. Esta última no demuestra identidad literal ni exactitud jurídica de una cifra.

Para revisar extracción se comprueban los párrafos completos de cada página. Cada párrafo contiene una referencia de control única; no se cuentan como cláusulas preservadas varias copias de una frase genérica. Esto se distingue de los 68 controles breves de datos relevantes.

## Hallazgos de la revisión previa

La auditoría verificó los 240 hashes y la pertenencia de las 68 citas a sus cláusulas fuente. Encontró seis citas de TXT que existen en su página, pero cruzan el límite de fragmento de 900 caracteres. Se mantienen en el experimento como fallos de la unidad de recuperación actual, sin atribuirlos a OCR.

Un piloto de `SIM0170`, página 4, se clasificó como texto nativo y conservó solo 198 caracteres del encabezado. La cláusula de reparaciones quedó ausente. Un ensayo separado de OCR parcial recuperó 2338 caracteres y el importe ficticio de 5100 pesos. Este hallazgo motivó la corrección posterior autorizada por Fernando; la medición inicial se conserva intacta.

## Ejecución reproducible

Para reconstruir el experimento en una instalación nueva, con el servicio levantado, desde la raíz del producto:

```bash
docker compose exec api uv run --project backend --frozen --group demo python demo/generar_corpus_amplio.py /tmp/corpus_amplio
docker compose exec api python demo/evaluar_corpus.py /tmp/corpus_amplio
```

El primer comando añade las dependencias de generación definidas en el grupo demo y genera los archivos. El segundo carga una colección mediante la API existente y evalúa el resultado. No necesita una clave de OpenAI; la clave interna se lee dentro del contenedor. Para conservar los resultados, usar `docker compose cp` antes de recrear el contenedor.

La carga registra el archivo pendiente antes de enviarlo y conserva los tiempos originales de los recibos. Si pierde una respuesta y el documento aún no aparece, exige reconciliación antes de reenviar. Una comprobación posterior de hashes tiene su propio tiempo y no sustituye el tiempo de ingesta.

## Resultados de la medición inicial

240 documentos cargados mediante HTTP, 1640 páginas lógicas y 5527 fragmentos de 384 dimensiones. La carga serial tardó 1010,3 segundos, aproximadamente 16 minutos y 50 segundos. Se conservaron los 240 tiempos originales al volver a verificar sus hashes. La base PostgreSQL completa ocupó 32 MB; los archivos originales se almacenan aparte.

| Consulta y modo | Página correcta primera | Página correcta en top 5 | Cita literal completa en un pasaje, top 5 |
| --- | --- | --- | --- |
| Libre, híbrida | 54/68 | 63/68 | 52/68 |
| Natural con folio, híbrida | 56/68 | 63/68 | 52/68 |
| Precisa, textual | 64/68 | 64/68 | 54/68 |
| Precisa, híbrida | 54/68 | 64/68 | 54/68 |

La mediana de latencia de las consultas libres híbridas fue de 47,2 ms y el p95 de 76,1 ms, sobre el servicio local ya iniciado. El [resumen completo](07_Evidencias/corpus_amplio/resumen_base.md) incluye los tres modos y las tres variantes.

En preguntas libres híbridas, los 68 casos se explican así:

| Resultado de la cita literal | Casos |
| --- | --- |
| Cita completa recuperada | 52 |
| Texto ausente por extracción incompleta | 4 |
| Diferencia literal introducida por OCR | 1 |
| Cita dividida entre fragmentos | 9 |
| Cita disponible en un fragmento, pero fuera del top 5 | 2 |

Este diagnóstico reconstruyó la regla de fragmentación de 900 caracteres sobre las páginas extraídas. Distingue capacidad de extracción, unidad de recuperación y ranking. No se quitaron los fallos del denominador.

## Extracción y OCR

| Formato | Párrafos completos de control | Conservados con comparación normalizada | Conservados literalmente |
| --- | --- | --- | --- |
| PDF digital | 3840 | 3840 | 3840 |
| PDF escaneado | 1280 | 1074 | 775 |
| PDF mixto | 1280 | 1129 | 1009 |
| TXT | 1280 | 1280 | 1280 |

Una diferencia de un carácter, acento o puntuación puede hacer fallar la comparación literal de un párrafo largo; esta tabla no es una tasa de error por palabra. Los PDF mixtos también incluyen páginas digitales, por lo que sus porcentajes no constituyen una comparación directa entre motores OCR.

De las 68 citas breves de datos relevantes, 64 se conservaron con comparación normalizada en la página y 63 literalmente. Se esperaban 480 páginas con OCR; el servicio registró 464. Las 16 restantes pertenecen a los cuatro PDF con encabezado digital y cuerpo en imagen.

## Gestión y falta de evidencia

El recorrido CRUD y de errores se repitió después de la carga: 78/78 comprobaciones correctas. Dos preguntas sin evidencia, ejecutadas en tres modos (seis peticiones), dieron cero coincidencias en textual y cinco vecinos en vectorial e híbrida. No se mide una respuesta generada ni se atribuye abstención al motor.

La prueba demuestra capacidad sobre este corpus sintético y deja defectos concretos antes de conectar Luna. No acredita equivalencia con OpenAI File Search ni precisión general en documentos reales.

## Corrección del OCR intrapágina verificada

Fernando autorizó aplicar y verificar el cambio. El extractor conserva OCR completo para páginas con menos de 60 caracteres nativos. Cuando hay texto digital y una imagen visible ocupa al menos el 25 % del área de la página, utiliza OCR parcial de PyMuPDF (`full=False`). Las imágenes menores quedan fuera de esta heurística.

Se reconstruyó únicamente la API y se reindexaron `SIM0170`, `SIM0180`, `SIM0190` y `SIM0200` mediante baja lógica y carga de los mismos PDF. Los recibos conservan identificadores anteriores y nuevos. Se comprobaron los hashes de los cuatro originales, la identidad de los otros 236 detalles completos y la igualdad literal de las 16 páginas nativas de los documentos reindexados. Las otras 16 páginas ahora utilizan OCR.

La colección mantiene 240 documentos y 1640 páginas. Registra 480 páginas OCR y 5559 fragmentos de 384 dimensiones. Se repitieron exactamente las mismas 612 consultas y el mismo manifiesto, sin modificar preguntas ni citas esperadas.

| Medida | Inicial | Con corrección |
| --- | --- | --- |
| Libre híbrida: página correcta primera | 54/68 | 57/68 |
| Libre híbrida: página correcta en top 5 | 63/68 | 67/68 |
| Libre híbrida: cita literal completa en un pasaje, top 5 | 52/68 | 56/68 |
| Natural con folio híbrida: página correcta en top 5 | 63/68 | 67/68 |
| Precisa textual: página correcta primera | 64/68 | 68/68 |
| Precisa textual: cita literal completa en un pasaje, top 5 | 54/68 | 58/68 |
| Citas breves conservadas en la página, normalizadas | 64/68 | 68/68 |
| Citas breves conservadas literalmente en la página | 63/68 | 67/68 |

Los PDF mixtos pasaron de 1129 a 1168 párrafos completos normalizados y de 1009 a 1048 literales, sobre 1280 controles. Las cifras de los otros formatos permanecen iguales. Detectar correctamente el método de extracción no significa que todos los caracteres reconocidos sean correctos.

La comparación pareada no encontró pérdidas de página correcta o cita literal dentro del top 5. Hubo una variación adversa de posición: `SIM0017-C13`, consulta precisa vectorial, pasó de tercero a cuarto. La mejora agregada no implica que todos los rankings individuales mejoren.

La mediana de consultas libres híbridas fue de 50,3 ms y el p95 de 88,0 ms. Son observaciones de ejecuciones locales distintas, sin aislamiento de rendimiento; no demuestran una mejora o regresión de velocidad causada por el cambio.

Evidencia: [comparación](07_Evidencias/corpus_amplio/comparacion_ocr_parcial.json), [integridad](07_Evidencias/corpus_amplio/integridad_ocr_parcial.json), [resumen posterior](07_Evidencias/corpus_amplio/resumen_ocr_parcial.md) y [conteos PostgreSQL](07_Evidencias/corpus_amplio/postgres_ocr_parcial.txt). Chrome recuperó `SIM0170`, página 4, con la cláusula de 5100 pesos ficticios y la referencia al original. El recorrido HTTP posterior volvió a superar 78/78 comprobaciones. La extracción nueva de los seis contratos iniciales conservó sus ocho controles OCR y seis fuentes esperadas en top 5; su [recibo separado](07_Evidencias/corpus_amplio/recuperacion_tesseract_ocr_parcial.json) no reemplaza el histórico.

Permanecen las limitaciones de fragmentación, ranking, errores de OCR y falta de abstención. La conexión de Luna sigue fuera de esta etapa.

[Guía de consultas verificadas](11_guia_consultas.md).
