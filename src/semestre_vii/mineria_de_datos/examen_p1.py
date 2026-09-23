import duckdb

from semestre_vii.mineria_de_datos import DATA_DIR


conexion = duckdb.connect()


# =============================================================================
# 1. CARGAR LOS ARCHIVOS
# =============================================================================
# read_csv carga cada CSV como una relación de DuckDB.
# Después create_view deja cada archivo disponible para consultarlo con SQL.

albums = conexion.read_csv(str(DATA_DIR / "Albums.csv"))
artists = conexion.read_csv(str(DATA_DIR / "Artists.csv"))
features = conexion.read_csv(str(DATA_DIR / "Features.csv"))
popularity = conexion.read_csv(str(DATA_DIR / "Popularity.csv"))

albums.create_view("albums", replace=True)
artists.create_view("artists", replace=True)
features.create_view("features", replace=True)
popularity.create_view("popularity", replace=True)


# =============================================================================
# 2. MOSTRAR UNA DESCRIPCIÓN DE CADA ARCHIVO
# =============================================================================
# SUMMARIZE muestra información descriptiva de las columnas:
# tipo de dato, mínimo, máximo, valores únicos, nulos, promedio, etc.

print("\n=== ALBUMS ===")
conexion.sql("SUMMARIZE albums").show()

print("\n=== ARTISTS ===")
conexion.sql("SUMMARIZE artists").show()

print("\n=== FEATURES ===")
conexion.sql("SUMMARIZE features").show()

print("\n=== POPULARITY ===")
conexion.sql("SUMMARIZE popularity").show()
