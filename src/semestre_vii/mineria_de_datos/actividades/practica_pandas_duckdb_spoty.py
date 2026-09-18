import subprocess

import duckdb
import polars as pl

from semestre_vii.mineria_de_datos import DATA_DIR

subprocess.run(["clear && clear"], shell=True, check=False)


path = DATA_DIR / "spotify.csv"

df = pl.read_csv(path)

archivo = path
print(f"Archivo: {archivo.name}")

tamaño_mb = round(df.estimated_size("mb"), 2)
print(f"Tamaño del DataFrame: {tamaño_mb} MB")


# CARGA EN DUCKDB

con = duckdb.connect()

con.sql(f"CREATE TABLE spotify AS SELECT * FROM read_csv('{path}')")


# LIMPIEZA DE x?

reemplazar_x = """REPLACE("x?", '(x', '')"""
reemplazar_parentesis = f"""REPLACE({reemplazar_x}, ')', '')"""

con.sql(f"""
    UPDATE spotify
    SET "x?" = {reemplazar_parentesis}
""")


# DUCKDB -> DATAFRAME

df_spotify = con.sql("SELECT * FROM spotify").pl()


# CAMBIO DE NOMBRE DE COLUMNAS

columnas = {
    "artist and title": "artista_titulo",
    "wks": "semanas_en_lista",
    "t10": "semanas_top_10",
    "pk": "posicion_pico",
    "x?": "semanas_en_pico",
    "PkStreams": "streams_pico",
    "total": "streams_totales",
    "artist name": "artista",
    "song name": "cancion",
    "lyrics": "letra",
}

df_spotify = df_spotify.rename(columnas)


# CASTEO DE COLUMNAS NUMÉRICAS

df_spotify = df_spotify.with_columns(
    pl.col("semanas_en_pico").cast(pl.Int64)
)


# MOSTRAR TIPOS

for columna, tipo in zip(df_spotify.columns, df_spotify.dtypes):
    print(f"C: {columna}, T: {tipo}")


# LAS 20 CANCIONES CON MÁS STREAMS

df_top_canciones = df_spotify.sort("streams_totales", descending=True).head(20)

print("Las 20 canciones con más reproducciones:")
print(df_top_canciones)

# LOS 20 ARTISTAS CON MÁS STREAMS
df_top_artistas = (
    df_spotify
    .group_by("artista")
    .agg(pl.col("streams_totales").sum())
    .sort("streams_totales", descending=True)
    .head(20)
)

print("Los 20 artistas con más reproducciones:")
print(df_top_artistas)



# LAS 10 CANCIONES QUE MÁS TIEMPO ESTUVIERON EN EL TOP 10
df_top_10 = (
    df_spotify
    .sort("semanas_top_10", descending=True, nulls_last=True)
    .head(10)
    .select(["artista", "cancion", "semanas_top_10"])
)

print("Las 10 canciones que más tiempo estuvieron en el top 10:")
print(df_top_10)


# LAS TRES CANCIONES QUE MÁS VECES SE REPITE EL NOMBRE

df_canciones = (
    df_spotify
    .group_by("cancion")
    .agg(pl.len().alias("veces_repetido"))
    .sort("veces_repetido", descending=True)
    .head(3)
)

print("Las 3 canciones que más veces se repiten:")
print(df_canciones)

# LAS TRES CANCIONES CON MÁS TIEMPO EN EL NÚMERO 1

df_top_uno = (
    df_spotify
    .filter(pl.col("posicion_pico") == 1)
    .sort("semanas_en_pico", descending=True, nulls_last=True)
    .head(3)
    .select(["artista", "cancion", "semanas_en_pico"])
)

print("Las 3 canciones con más tiempo en el número 1:")
print(df_top_uno)