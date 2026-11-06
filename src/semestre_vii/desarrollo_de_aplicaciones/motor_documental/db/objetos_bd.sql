CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE colecciones (
    id uuid PRIMARY KEY,
    nombre varchar(120) NOT NULL UNIQUE CHECK (btrim(nombre) <> ''),
    creada_en timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE documentos (
    id uuid PRIMARY KEY,
    coleccion_id uuid NOT NULL REFERENCES colecciones(id),
    titulo varchar(200) NOT NULL CHECK (btrim(titulo) <> ''),
    nombre_original varchar(200) NOT NULL CHECK (btrim(nombre_original) <> ''),
    extension varchar(4) NOT NULL CHECK (extension IN ('pdf', 'txt')),
    activo boolean NOT NULL DEFAULT true,
    modelo varchar(150) NOT NULL,
    creado_en timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE paginas (
    id uuid PRIMARY KEY,
    documento_id uuid NOT NULL REFERENCES documentos(id),
    numero integer NOT NULL CHECK (numero > 0),
    texto text NOT NULL CHECK (btrim(texto) <> ''),
    metodo varchar(10) NOT NULL CHECK (metodo IN ('texto', 'ocr')),
    UNIQUE (documento_id, numero)
);
CREATE TABLE fragmentos (
    id uuid PRIMARY KEY,
    pagina_id uuid NOT NULL REFERENCES paginas(id),
    orden integer NOT NULL CHECK (orden >= 0),
    texto text NOT NULL CHECK (btrim(texto) <> ''),
    embedding vector(384) NOT NULL,
    busqueda tsvector GENERATED ALWAYS AS (to_tsvector('spanish', texto)) STORED,
    UNIQUE (pagina_id, orden)
);
-- Búsqueda textual: GIN indexa el tsvector para acotar candidatos por términos.
CREATE INDEX fragmentos_busqueda_gin ON fragmentos USING gin(busqueda);
CREATE INDEX documentos_coleccion_idx ON documentos(coleccion_id);
-- Biblioteca: unificar disponibilidad y conteos para no reconstruirlos en la UI.
CREATE VIEW documentos_disponibles AS
SELECT d.*, count(p.id)::integer AS paginas,
       count(p.id) FILTER (WHERE p.metodo = 'ocr')::integer AS paginas_ocr
FROM documentos d LEFT JOIN paginas p ON p.documento_id = d.id
WHERE d.activo
GROUP BY d.id;
