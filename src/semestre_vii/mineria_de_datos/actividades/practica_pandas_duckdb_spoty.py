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

con = duckdb.connect()

con.register("spotify_df", df)

df_spotify = con.sql("SELECT * FROM spotify_df").pl()





print(df_spotify.select(["x?"]))


