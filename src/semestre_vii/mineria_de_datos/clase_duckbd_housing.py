import subprocess

import duckdb
import polars as pl

from semestre_vii.mineria_de_datos.descargar_datos import asegurar

# limpiar

subprocess.run("clear && clear", shell=True, check=False)

path = asegurar("USA_Housing.csv")



df = pl.read_csv(path)

archivo = path
print(f"Archivo: {archivo}")

tamaño_mb = round(df.estimated_size("mb"), 2)
print(f"Tamaño del DataFrame: {tamaño_mb} MB")

duckdb_version = duckdb.__version__
print(f"Versión de DuckDB: {duckdb_version}")


# Conexión a DuckDB 
con = duckdb.connect()

con.sql(f"CREATE TABLE casas AS SELECT * FROM read_csv('{path}')")

df_house = con.sql("SELECT * FROM casas LIMIT 20").pl()




columnas = {
    "Avg. Area Income": "ingreso",
    "Avg. Area House Age": "antiguedad",
    "Avg. Area Number of Rooms": "habitaciones",
    "Avg. Area Number of Bedrooms": "dormitorios",
    "Area Population": "poblacion",
    "Price": "precio",
    "Address": "direccion",
}

df_house = df_house.rename(columnas)

print(df_house)
print(df_house.dtypes)


df_house = df_house.drop(["poblacion"])
print(df_house)

# Ingreso promedio
ingreso_promedio = df_house["ingreso"].mean()
print(f"Ingreso promedio: {ingreso_promedio:.2f}")


df_ingreso = df_house.filter(pl.col("ingreso") > 70_000)
print(df_ingreso)



