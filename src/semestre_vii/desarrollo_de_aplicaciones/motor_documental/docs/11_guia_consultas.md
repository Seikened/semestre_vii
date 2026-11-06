# Probar las consultas sin agente

Abrir http://localhost:3000, elegir **Buscar fragmentos** y seleccionar **Evaluación ampliada, 240 ficticios**. Esta colección ya está cargada en la instancia local. No hace falta volver a indexarla para hacer estas pruebas. El [chat opcional de Luna](16_chat_luna_mvp.md) tiene una verificación distinta.

## Primera prueba, pregunta natural

Elegir **Búsqueda híbrida** y escribir:

> En el arrendamiento de Villa Jacaranda entre Fernando León Franco y Fabián León Franco, ¿en cuántos días se devuelve la garantía?

Resultado verificado: la primera fuente es `SIM0001_digital.pdf`, página 5. El pasaje contiene la cláusula 18:

> La garantía se devuelve dentro de 37 días naturales después de entregar las llaves y firmar el inventario, descontando solo daños documentados.

Abrir la flecha del resultado lleva al PDF original en la página 5. La página 1 identifica a Fernando como parte cedente y a Fabián como parte receptora, exclusivamente en esta simulación. Existen distractores llamados Villa Jacaranda Norte, Sur y Anexo; comprobar el nombre completo del inmueble y el folio.

Captura real: `07_Evidencias/corpus_pregunta_natural.png`.

## Cuando ya conoces el documento

Elegir **Búsqueda textual**. Estas consultas se ejecutaron y devolvieron una fuente cada una:

| Escribir | Archivo y ubicación | Contenido esperado |
| --- | --- | --- |
| `SIM0001 "Devolución de garantía"` | `SIM0001_digital.pdf`, página 5, cláusula 18 | 37 días naturales; entrega de llaves e inventario firmado. |
| `SIM0121 "Devolución de garantía"` | `SIM0121_escaneado.pdf`, página 5, cláusula 18 | 43 días naturales. La página fue extraída con OCR. |
| `SIM0161 "Terminación anticipada"` | `SIM0161_mixto.pdf`, página 6, cláusula 21 | Aviso de 80 días y compensación de 3 mensualidades ficticias. |
| `SIM0201 "Devolución de garantía"` | `SIM0201_txt.txt`, página lógica 1, cláusula 18 | 41 días naturales. |

Las citas y las respuestas HTTP completas están en `07_Evidencias/corpus_amplio/consultas_demostracion_base.json`.

## Cómo formular la búsqueda

1. Si recuerdas el concepto, usar híbrida e incluir tipo de contrato, propiedad y, cuando ayude, las partes. No hace falta copiar las palabras de la cláusula.
2. Si conoces el folio, usar textual con folio y tema o frase entre comillas.
3. Verificar archivo y página antes de usar un importe o plazo. En búsqueda híbrida pueden aparecer otros documentos como resultados adicionales, aunque el folio esté en la consulta: ese texto ayuda al ranking, no es un filtro estricto por documento.

Cada mensaje se busca por separado. El historial visual todavía no interpreta expresiones como “ese contrato” o “¿y ahora su depósito?”. Repetir el inmueble o el folio en cada consulta. Resolver referencias conversacionales corresponde a la futura integración del agente.

## Prueba de una limitación real

En búsqueda textual, escribir:

> SIM0201 "Límite de reparaciones"

El documento correcto aparece, pero la oración de la cláusula 13 cruza el límite entre fragmentos. El importe es de 5400 pesos ficticios por evento y un gasto mayor requiere aprobación escrita; para leer la oración completa, abrir el original o el detalle del documento. El TXT completo conserva la frase. El buscador actual no une automáticamente los fragmentos adyacentes.

## Comprobar el OCR dentro de una página mixta

En búsqueda textual, escribir:

> SIM0170 "Límite de reparaciones"

Resultado verificado en Chrome después de la corrección: `SIM0170_mixto.pdf`, página 4, método OCR. El pasaje contiene el límite de **5100 pesos ficticios por evento** y la obligación de aprobación escrita para un gasto mayor. La flecha abre el original en esa página.

Este PDF combina encabezado digital y cuerpo en imagen en la misma página. Antes solo se recuperaba el encabezado; ahora el OCR parcial incorpora el cuerpo. La captura está en `07_Evidencias/corpus_ocr_intrapagina_corregido.png` y la comparación completa en [la evaluación](10_evaluacion_ampliada.md).

## Prueba sin evidencia

Escribir `Contrato INEXISTENTEZZQ9999 del castillo lunar`:

- En búsqueda textual no hubo coincidencias.
- En vectorial e híbrida se devolvieron cinco vecinos, aunque el contrato no existe.

El motor ordena pasajes cercanos; todavía no decide por sí mismo si una pregunta tiene respuesta. Un resultado cercano no acredita el documento solicitado. El agente futuro deberá comprobar identidad y evidencia antes de responder.

## Qué demuestra esta prueba

Carga, OCR, vectores, búsqueda, procedencia y apertura del original funcionan sin un LLM. La muestra ampliada también deja visibles los fallos de OCR, fragmentación y ranking. Los resultados completos y sus límites están en [la evaluación](10_evaluacion_ampliada.md).
