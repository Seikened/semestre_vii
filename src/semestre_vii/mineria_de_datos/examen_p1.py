import duckdb
import polars as pl

from semestre_vii.aprendizaje_automatico_iii import DATA_DIR

path = DATA_DIR / "USA_Housing.csv"



df = pl.read_csv(path)