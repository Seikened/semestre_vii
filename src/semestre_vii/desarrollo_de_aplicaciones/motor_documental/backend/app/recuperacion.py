import numpy as np

from app.contratos import Coincidencia, Consulta, ModoBusqueda, ResultadoBusqueda
from app.embeddings import MODELO, REVISION
from app.persistencia import BaseDocumental

BASE = """
WITH base AS (
    SELECT f.id, f.embedding, f.busqueda, f.texto, p.numero AS pagina, p.metodo,
           d.id AS documento_id, d.titulo, d.nombre_original
    FROM fragmentos f JOIN paginas p ON p.id=f.pagina_id
    JOIN documentos d ON d.id=p.documento_id
    WHERE d.activo AND d.modelo=%s AND (%s::uuid IS NULL OR d.coleccion_id=%s)
)
"""
CAMPOS = "documento_id,titulo,nombre_original,pagina,metodo,texto"


def recuperar(base: BaseDocumental, consulta: Consulta, vector: np.ndarray | None) -> ResultadoBusqueda:
    parametros = [f"{MODELO}@{REVISION}", consulta.coleccion_id, consulta.coleccion_id]
    match consulta.modo:
        case ModoBusqueda.TEXTO:
            sql = BASE + f"""
            SELECT {CAMPOS}, ts_rank_cd(busqueda,websearch_to_tsquery('spanish',%s)) AS puntuacion
            FROM base WHERE busqueda @@ websearch_to_tsquery('spanish',%s)
            ORDER BY puntuacion DESC,id LIMIT %s
            """
            parametros.extend([consulta.texto, consulta.texto, consulta.limite])
        case ModoBusqueda.VECTOR:
            sql = BASE + f"""
            SELECT {CAMPOS}, 1-(embedding <=> %s) AS puntuacion FROM base
            ORDER BY embedding <=> %s,id LIMIT %s
            """
            parametros.extend([vector, vector, consulta.limite])
        case ModoBusqueda.HIBRIDA:
            sql = BASE + f"""
            , semantica AS (
                SELECT id,row_number() OVER (ORDER BY embedding <=> %s,id) AS posicion
                FROM base ORDER BY embedding <=> %s,id LIMIT 40
            ), lexica AS (
                SELECT id,row_number() OVER (
                    ORDER BY ts_rank_cd(busqueda,websearch_to_tsquery('spanish',%s)) DESC,id
                ) AS posicion FROM base WHERE busqueda @@ websearch_to_tsquery('spanish',%s)
                ORDER BY posicion LIMIT 40
            ), fusion AS (
                SELECT id,sum(1.0/(60+posicion)) AS puntuacion FROM (
                    SELECT * FROM semantica UNION ALL SELECT * FROM lexica
                ) candidatos GROUP BY id
            )
            SELECT {','.join('b.' + campo for campo in CAMPOS.split(','))},fusion.puntuacion
            FROM base b JOIN fusion USING(id) ORDER BY fusion.puntuacion DESC,b.id LIMIT %s
            """
            parametros.extend([vector, vector, consulta.texto, consulta.texto, consulta.limite])
    with base.conectar() as conexion:
        filas = conexion.execute(sql, parametros).fetchall()
    return ResultadoBusqueda(
        consulta=consulta.texto, modo=consulta.modo,
        coincidencias=[Coincidencia.model_validate(fila) for fila in filas],
    )
