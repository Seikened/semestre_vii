# Solicitudes de cambio

## SC-001: identificación del método de extracción

**Descripción:** ampliar la ingesta de PDF con texto para admitir documentos escaneados y mixtos, identificando el método de extracción por página.

**Motivo:** los contratos de una inmobiliaria pueden llegar como escaneos; la búsqueda requiere texto recuperable y procedencia verificable.

| Capa | Impacto |
| --- | --- |
| Datos | Conservar texto, número de página y método de extracción. |
| API | Procesar OCR cuando corresponda y devolver el desglose de métodos. |
| Frontend | Mostrar si un documento utilizó extracción nativa, OCR o ambas. |

**Estado:** extracción por página, persistencia, API e interfaz implementadas. El recorrido HTTP comprueba la carga de un escaneo y el detalle expone los métodos por página; la evidencia de ejecución se conserva por separado.

**Aceptación:** cargar un PDF mixto, comprobar extracción nativa en la primera página y OCR en la segunda, encontrar una cláusula de cada página y abrir su original.

**Ampliación verificada el 2 de noviembre de 2026:** Fernando autorizó corregir páginas con encabezado digital y cuerpo en imagen. Se añadió detección de imágenes visibles que ocupan al menos el 25 % de la página y OCR parcial cuando también existe texto nativo. Cuatro PDF ficticios reindexados recuperaron las 16 páginas omitidas. La colección ampliada registra las 480 páginas OCR esperadas; las mismas 612 consultas y 78 comprobaciones HTTP se repitieron. Ver `../10_evaluacion_ampliada.md` y los recibos `../07_Evidencias/corpus_amplio/*ocr_parcial*`.

## Cambio de proyecto

Fernando descartó el proyecto de gasolineras y definió el motor documental inmobiliario como sustituto. Se conserva el scaffold histórico y se implementó una interfaz nueva. El 2 de noviembre de 2026 Fernando confirmó expresamente que el profesor aceptó la sustitución. La aceptación del cambio de dominio queda cerrada; la calidad funcional de la nueva interfaz se verifica por separado contra B5.
