import subprocess

import duckdb
import polars as pl

from semestre_vii.mineria_de_datos import DATA_DIR

# Limpiar terminal
subprocess.run("clear && clear", shell=True, check=False)

path = DATA_DIR / "2026-01.csv"

df = pl.read_csv(
    path,
    null_values="NULL",
    schema_overrides={"Edad_Usuario": pl.Float64},
)

archivo = path
print(f"Archivo: {archivo}")

tamaño_mb = round(df.estimated_size("mb"), 2)
print(f"Tamaño del DataFrame: {tamaño_mb} MB")

duckdb_version = duckdb.__version__
print(f"Versión de DuckDB: {duckdb_version}")

# Conexión a DuckDB
con = duckdb.connect()

con.register("bicis_df", df)
con.sql("CREATE TABLE bicis AS SELECT * FROM bicis_df")

df_bicis = con.sql("SELECT * FROM bicis LIMIT 200").pl()

columnas = {
    "Genero_Usuario": "genero",
    "Edad_Usuario": "edad",
    "Bici": "bici",
    "Ciclo_Estacion_Retiro": "origen",
    "Fecha_Retiro": "fecha_salida",
    "Hora_Retiro": "hora_salida",
    "Ciclo_EstacionArribo": "destino",
    "Fecha_Arribo": "fecha_llegada",
    "Hora_Arribo": "hora_llegada",
}

df_bicis = df_bicis.rename(columnas)

print(df_bicis)
print(df_bicis.dtypes)

# Edad promedio
edad = "edad"
edad_promedio = df_bicis[edad].mean()

if edad_promedio is not None:
    print(f"Edad promedio: {edad_promedio:.2f}")

# Usuarios mayores de 70 años
df_mayores = df_bicis.filter(pl.col(edad) > 60)

print(df_mayores)



"""
nota: la setencia sql con duckdb

ejercicio 1 (dataframe 1):

Agrupar por estacion retiro y contar cuantas personas salieron por estacion (groupby)

ejercicio 2 (dataframe 2):
- llevar a 2k de registros
- eliminar las edades mayores a 55 años
- eliminar las columnas de las fechas


ejercicio 3 (dataframe 3):
decir la edad promedio por estacion retiro

"""

# EJERCICIO 1
df_estacion = con.sql(
    """
    SELECT Ciclo_Estacion_Retiro, COUNT(*) AS cantidad_usuarios
    FROM bicis
    GROUP BY Ciclo_Estacion_Retiro
    ORDER BY cantidad_usuarios DESC
    """
).pl()
print(df_estacion)

# EJERCICIO 2
df_bicis_2k = df_bicis.head(2000)
df_bicis_2k = df_bicis_2k.filter(pl.col(edad) <= 55)
df_bicis_2k = df_bicis_2k.drop(["fecha_salida", "fecha_llegada"])
print(df_bicis_2k)


# EJERCICIO 3
df_edad_promedio = con.sql(
    """
    SELECT
        Ciclo_Estacion_Retiro,
        ROUND(AVG(Edad_Usuario), ) AS edad_promedio
    FROM bicis
    GROUP BY Ciclo_Estacion_Retiro
    ORDER BY edad_promedio DESC
    """
).pl()

print(df_edad_promedio)