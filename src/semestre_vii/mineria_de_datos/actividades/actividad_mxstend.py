import pandas as pd
from mlxtend.frequent_patterns import association_rules, fpgrowth

from semestre_vii.mineria_de_datos import DATA_DIR

path = DATA_DIR / "dataset_reglas_asociacion.csv"



df = pd.DataFrame(pd.read_csv(path))


edad = "Edad"
monto_gastado = "Monto_Gastado"
dias_semana = "Dia_Semana"





def solo_antecedente(itemset):
    var_contexto = ('Rango_edad_', 'Dia_Semana_', 'Rango_gasto_')
    return all(item.startswith(var_contexto) for item in itemset)

def solo_producto(itemset):
    var_producto = ('Producto_Principal_', 'Accesorio_')
    return all(item.startswith(var_producto) for item in itemset)





df["Rango_edad"] = pd.cut(df[edad], bins = [18,25,40,70], labels = ["Joven", "Adulto", "Adulto Mayor"], include_lowest=True)

df["Rango_gasto"] = pd.cut(df[monto_gastado], bins = [0, 800, 2000,3500], labels = ["Bajo", "Medio", "Alto"])





df_transformada = df.drop(columns=[edad, monto_gastado])

df_bin = pd.get_dummies(df_transformada)

print("DataFrame transformada y binarizada:")
print(df_bin.head(3))




soporte = 0.1
treshold = 1.2
elementos_frecuentes = fpgrowth(df_bin, min_support=soporte, use_colnames=True)

reglas = association_rules(elementos_frecuentes, metric="lift", min_threshold=treshold)

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




reglas_recom = reglas[
    reglas['Antecedente(X)'].apply(solo_antecedente) &
    reglas['Consecuente(Y)'].apply(solo_producto)
].sort_values(by='Metrica Lift', ascending=False)



print ("\nReglas de recomendación:")
print(reglas_recom)

# for idx, row in reglas_recom.iterrows():
#     ant = list(row['Antecedente(X)'])
#     cons = list(row['Consecuente(Y)'])
#     print(f"\nRegla: {ant} -> {cons}")
#     print(f"Soporte: {row['Soporte']:.2f}")
#     print(f"Confianza: {row['Confianza']:.2f}")
