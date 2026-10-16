import pandas as pd
from mlxtend.frequent_patterns import association_rules, fpgrowth

raw_data = {
    'Edad': [22, 28, 45, 30, 52, 26, 33, 41, 24, 29, 48, 55, 23, 31, 42, 60, 27, 34, 50, 21],
    'Dia_Semana': ['Viernes', 'Viernes', 'Lunes', 'Viernes', 'Lunes', 'Viernes', 'Sabado', 'Lunes','Viernes', 'Sabado', 'Lunes', 'Lunes', 'Viernes', 'Viernes', 'Lunes', 'Lunes', 'Sabado', 'Viernes', 'Lunes', 'Viernes'],
    'Monto_Gasto': [1200, 1500, 150, 1100, 200, 1300, 950, 180, 1400, 1150, 120, 210, 1350, 1250, 190, 160, 980, 1600, 220, 1050],
    'Producto_Principal': ['Laptop', 'Laptop', 'Cafe', 'Laptop', 'Cafe', 'Laptop', 'Laptop', 'Cafe', 'Laptop', 'Laptop', 'Cafe', 'Cafe', 'Laptop', 'Laptop', 'Cafe', 'Cafe', 'Laptop', 'Laptop', 'Cafe', 'Laptop'],
    'Accesorio_Comprado': ['Funda', 'Funda', 'Pan', 'Funda', 'Pan', 'Mouse', 'Funda', 'Ninguno', 'Funda', 'Funda', 'Pan', 'Pan', 'Mouse', 'Funda', 'Pan', 'Ninguno', 'Mouse', 'Funda', 'Pan', 'Funda']
}


df = pd.DataFrame(raw_data)


df["Rango_edad"] = pd.cut(df["Edad"], bins = [18,35,65], labels = ["Joven", "Adulto"])

df["Rango_gasto"] = pd.cut(df["Monto_Gasto"], bins = [0, 500, 2000], labels = ["Bajo", "Alto"])

df_transformada = df.drop(columns=["Edad", "Monto_Gasto"])

df_bin = pd.get_dummies(df_transformada)

print("DataFrame transformada y binarizada:")
print(df_bin.head(3))




soporte = 0.5
elementos_frecuentes = fpgrowth(df_bin, min_support=soporte, use_colnames=True)

reglas = association_rules(elementos_frecuentes, metric="lift", min_threshold=1.2)

nombre_columnas = {
    'antecedents': 'Antecedente(X)',
    'consequents': 'Consecuente(Y)',
    'support': 'Soporte',
    'confidence': 'Confianza',
    'lift': 'Metrica Lift'
}

reglas = reglas.rename(columns=nombre_columnas)
filtrado = reglas[['Antecedente(X)', 'Consecuente(Y)', 'Soporte', 'Confianza', 'Metrica Lift']]
ordenar_reglas = reglas[filtrado.columns].sort_values(by='Metrica Lift', ascending=False)

print("\nReglas de asociación:")
print(ordenar_reglas)


# for idx, row in ordenar_reglas.iterrows():
#     ant = list(row['Antecedente(X)'])
#     cons = list(row['Consecuente(Y)'])
#     print(f"\nRegla: {ant} -> {cons}")
#     print(f"Soporte: {row['Soporte']:.2f}")
#     print(f"Confianza: {row['Confianza']:.2f}")