from contextlib import contextmanager
from uuid import UUID, uuid4

import psycopg
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row

from app.contratos import Coleccion, DetalleDocumento, Documento, EditarDocumento
from app.embeddings import MODELO, REVISION
from app.errores import AppError, CodigoError
from app.indexacion import DocumentoIndexado
from app.modelos import PaginaExtraida


class BaseDocumental:
    def __init__(self, conexion: str):
        self._conexion = conexion

    @contextmanager
    def conectar(self):
        try:
            with psycopg.connect(self._conexion, row_factory=dict_row) as conexion:
                register_vector(conexion)
                yield conexion
        except psycopg.errors.UniqueViolation as error:
            raise AppError(CodigoError.COLECCION_DUPLICADA, "La colección ya existe.") from error
        except psycopg.errors.ForeignKeyViolation as error:
            raise AppError(CodigoError.COLECCION_NO_ENCONTRADA, "La colección no existe.") from error
        except psycopg.OperationalError as error:
            raise AppError(CodigoError.BD_NO_DISPONIBLE, "La base de datos no está disponible.") from error

    def colecciones(self) -> list[Coleccion]:
        with self.conectar() as conexion:
            filas = conexion.execute("SELECT * FROM colecciones ORDER BY nombre").fetchall()
        return [Coleccion.model_validate(fila) for fila in filas]

    def crear_coleccion(self, nombre: str, identificador: UUID | None = None) -> Coleccion:
        with self.conectar() as conexion:
            fila = conexion.execute(
                "INSERT INTO colecciones(id,nombre) VALUES (%s,%s) RETURNING *",
                (identificador or uuid4(), nombre),
            ).fetchone()
        return Coleccion.model_validate(fila)

    def documentos(self, coleccion_id: UUID | None = None) -> list[Documento]:
        with self.conectar() as conexion:
            filas = conexion.execute(
                "SELECT * FROM documentos_disponibles WHERE (%s::uuid IS NULL OR coleccion_id=%s) "
                "ORDER BY creado_en DESC", (coleccion_id, coleccion_id),
            ).fetchall()
        return [Documento.model_validate(fila) for fila in filas]

    def detalle(self, identificador: UUID) -> DetalleDocumento:
        with self.conectar() as conexion:
            fila = conexion.execute(
                "SELECT * FROM documentos_disponibles WHERE id=%s", (identificador,),
            ).fetchone()
            if fila is None:
                raise AppError(CodigoError.DOCUMENTO_NO_ENCONTRADO, "El documento no está disponible.")
            paginas = conexion.execute(
                "SELECT numero,texto,metodo FROM paginas WHERE documento_id=%s ORDER BY numero",
                (identificador,),
            ).fetchall()
        return DetalleDocumento(
            documento=Documento.model_validate(fila),
            paginas=[PaginaExtraida.model_validate(pagina) for pagina in paginas],
        )

    def editar(self, identificador: UUID, cambio: EditarDocumento) -> DetalleDocumento:
        with self.conectar() as conexion:
            fila = conexion.execute(
                "UPDATE documentos SET titulo=coalesce(%s,titulo), "
                "coleccion_id=coalesce(%s,coleccion_id) WHERE id=%s AND activo RETURNING id",
                (cambio.titulo, cambio.coleccion_id, identificador),
            ).fetchone()
            if fila is None:
                raise AppError(CodigoError.DOCUMENTO_NO_ENCONTRADO, "El documento no está disponible.")
        return self.detalle(identificador)

    def retirar(self, identificador: UUID) -> None:
        with self.conectar() as conexion:
            fila = conexion.execute(
                "UPDATE documentos SET activo=false WHERE id=%s AND activo RETURNING id",
                (identificador,),
            ).fetchone()
            if fila is None:
                raise AppError(CodigoError.DOCUMENTO_NO_ENCONTRADO, "El documento no está disponible.")

    def incorporar(self, indexado: DocumentoIndexado) -> None:
        with self.conectar() as conexion:
            conexion.execute(
                "INSERT INTO documentos(id,coleccion_id,titulo,nombre_original,extension,modelo) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (indexado.id, indexado.coleccion_id, indexado.titulo, indexado.extraido.nombre,
                 indexado.extraido.nombre.rsplit(".", 1)[1].lower(), f"{MODELO}@{REVISION}"),
            )
            paginas = {}
            for pagina in indexado.extraido.paginas:
                pagina_id = uuid4()
                paginas[pagina.numero] = pagina_id
                conexion.execute(
                    "INSERT INTO paginas(id,documento_id,numero,texto,metodo) VALUES (%s,%s,%s,%s,%s)",
                    (pagina_id, indexado.id, pagina.numero, pagina.texto, pagina.metodo.value),
                )
            with conexion.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO fragmentos(id,pagina_id,orden,texto,embedding) VALUES (%s,%s,%s,%s,%s)",
                    [(uuid4(), paginas[f.pagina], f.orden, f.texto, vector)
                     for f, vector in zip(indexado.fragmentos, indexado.vectores, strict=True)],
                )
