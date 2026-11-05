# Datos

## Procedencia

El generador en `demo/generar_contratos.py` crea seis contratos totalmente ficticios. Incluye dos PDF digitales, dos escaneados y dos mixtos. Personas, propiedades, folios, importes y cláusulas fueron inventados para la demostración.

## Modelo implementado

| Tabla | Responsabilidad |
| --- | --- |
| colecciones | Agrupación comprensible de documentos. |
| documentos | Nombre, colección, archivo original y disponibilidad. |
| paginas | Texto y método de extracción por página. |
| fragmentos | Texto recuperable, orden, página y embedding. |

La relación es colección → documentos → páginas → fragmentos. PostgreSQL reúne el catálogo, texto y vectores. Los archivos originales tienen almacenamiento separado.

## Reproducibilidad

Conservar nombre y dimensión del modelo, configuración de fragmentación y corpus original. Un cambio de modelo requiere generar vectores compatibles para documentos y consultas. OCR y embeddings son derivados reconstruibles.

El diccionario se encuentra en `02_Datos/DDA.md` y el SQL canónico en `../db/objetos_bd.sql`. Un índice GIN soporta búsqueda textual y una vista resume documentos activos. La búsqueda vectorial es exacta; no se necesita HNSW para doce fragmentos.
