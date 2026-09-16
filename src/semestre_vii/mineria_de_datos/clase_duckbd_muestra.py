from duckdb import connect

db = connect(":memory:")
mensaje = db.execute("SELECT 'DuckDB listo'").fetchone()[0]
print(mensaje)
db.close()
