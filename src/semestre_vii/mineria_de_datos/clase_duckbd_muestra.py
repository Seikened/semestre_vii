import polars as pl
import duckdb

from semestre_vii.mineria_de_datos import DATA_DIR

path = DATA_DIR / "USA_Housing.csv"




df = pl.read_csv(path)

archivo = path
print(f"Archivo: {archivo}")

tamaño_mb = round(df.estimated_size("mb"), 2)
print(f"Tamaño del DataFrame: {tamaño_mb} MB")

duckdb_version = duckdb.__version__
print(f"Versión de DuckDB: {duckdb_version}")


# Conexión a DuckDB 
con = duckdb.connect()

result = con.sql(f"select * from read_csv('{path}') limit 20")
print(result)
