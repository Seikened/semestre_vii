# Diccionario de datos

**Estado:** esquema implementado en `db/objetos_bd.sql` desde la raíz del producto. La inicialización se ejecuta únicamente al crear un volumen PostgreSQL nuevo.

| Tabla | Campo | Tipo | Nulo | Llave / restricción | Descripción |
| --- | --- | --- | --- | --- | --- |
| colecciones | id | uuid | No | PK | Identificador interno. |
| colecciones | nombre | varchar(120) | No | UNIQUE, texto no vacío | Grupo de contratos. |
| colecciones | creada_en | timestamptz | No | Fecha de creación | Instante de alta. |
| documentos | id | uuid | No | PK | Identificador del original. |
| documentos | coleccion_id | uuid | No | FK colecciones.id | Organización del archivo. |
| documentos | titulo | varchar(200) | No | Texto no vacío | Nombre de consulta editable. |
| documentos | nombre_original | varchar(200) | No | Longitud acotada | Nombre presentado al operador. |
| documentos | extension | varchar(4) | No | Valores pdf, txt | Formato admitido. |
| documentos | activo | boolean | No | Valor inicial verdadero | Disponibilidad de consulta y descarga. |
| documentos | modelo | varchar(150) | No | Modelo y revisión fijados | Procedencia del embedding. |
| documentos | creado_en | timestamptz | No | Fecha de creación | Instante de incorporación completa. |
| paginas | id | uuid | No | PK | Página extraída. |
| paginas | documento_id | uuid | No | FK documentos.id | Original al que pertenece. |
| paginas | numero | integer | No | Positivo, UNIQUE con documento_id | Página del PDF; TXT usa 1. |
| paginas | texto | text | No | Texto no vacío | Contenido de extracción. |
| paginas | metodo | varchar(10) | No | Valores texto, ocr | Procedimiento observado. |
| fragmentos | id | uuid | No | PK | Unidad recuperable. |
| fragmentos | pagina_id | uuid | No | FK paginas.id | Procedencia exacta. |
| fragmentos | orden | integer | No | No negativo, UNIQUE con pagina_id | Orden dentro de la página. |
| fragmentos | texto | text | No | Texto no vacío | Pasaje utilizado en búsqueda. |
| fragmentos | embedding | vector(384) | No | Dimensión del modelo E5 seleccionado | Representación semántica normalizada. |
| fragmentos | busqueda | tsvector | No | Derivado del texto | Representación de búsqueda textual en español. |

## Integridad

Solo guardar un documento como disponible después de completar extracción y vectorización. La baja lógica mantiene el original y sus derivados, pero los excluye de búsqueda y descarga. La búsqueda valida ese filtro en backend.

## Objetos implementados

Índice GIN sobre la representación textual, para las consultas léxicas. Vista de documentos disponibles con conteo de páginas y métodos, para la biblioteca. El SQL canónico vive en `db/objetos_bd.sql`; no se introducen migraciones destructivas automáticas.

`docs/02_Datos/objetos_bd.sql` es una copia para la entrega académica y debe coincidir con el archivo canónico de `db/`; no es otra migración.
