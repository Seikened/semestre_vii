import duckdb
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

from semestre_vii.mineria_de_datos import DATA_DIR

path = DATA_DIR / "popularity.csv"


columnas = ["streams_total", "streams_unified"]


con = duckdb.connect()

con.query(
    f"""
    CREATE TABLE popularity AS
    SELECT {', '.join(columnas)} FROM '{path}'
    WHERE streams_total IS NOT NULL AND streams_unified IS NOT NULL
    """
)
POPULARITY = con.table("popularity")



streams_total_size = con.sql("SELECT COUNT(streams_total) AS streams_total_size FROM popularity").fetchone()[0]
streams_unified_size = con.sql("SELECT COUNT(streams_unified) AS streams_unified_size FROM popularity").fetchone()[0]

print(f"Datos completos: {streams_total_size:,} en streams_total y {streams_unified_size:,} en streams_unified")

streams_total = con.sql("SELECT streams_total FROM popularity").fetchall()
streams_unified = con.sql("SELECT streams_unified FROM popularity").fetchall()

X = np.array([x[0] for x in streams_total]).reshape(-1, 1)
y = np.array([y[0] for y in streams_unified])


w = LinearRegression().fit(X, y).coef_[0]

y_hat = LinearRegression().fit(X, y).predict(X)

r2 = LinearRegression().fit(X, y).score(X, y)


fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
ax.scatter(X, y, color="#374151", s=45, zorder=3, label="Datos")
ax.plot(X, y_hat, color="#0D9488", linewidth=2, label=f"ŷ = {w:.2f}x")
ax.set(xlabel="Streams Total", ylabel="Streams Unified")
ax.set_title("Regresión lineal", loc="left", pad=16)
ax.spines[["top", "right"]].set_visible(False)
ax.spines[["left", "bottom"]].set_color("#D1D5DB")
ax.tick_params(colors="#6B7280", length=0)
ax.margins(x=0.08, y=0.12)
ax.legend(frameon=False)
plt.show()

print("Coneficientes y predicciones:")
print(f"Coeficiente: {w:.2f}")
print(f"Predicciones: {y_hat[:5]}")
print(f"R^2: {r2:.4f}")
