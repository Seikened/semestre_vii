import pandas as pd
from prefixspan import PrefixSpan

from semestre_vii.mineria_de_datos import DATA_DIR

path = DATA_DIR / "compras.csv"


df = pd.read_csv(path)


df['fecha_compra'] = pd.to_datetime(df['Fecha_Compra'])

df_ordenado = df.sort_values(by=['Cliente_ID', 'fecha_compra'])

secuencias = df_ordenado.groupby('Cliente_ID')['Producto'].apply(list)

#print(secuencias)

ps = PrefixSpan(secuencias.tolist())


clientes_min = 20
patrones_frecuentes = ps.frequent(minsup=clientes_min)

conteo_patrones = {tuple(p[1]): p[0] for p in patrones_frecuentes}

for patron, conteo in conteo_patrones.items():
    if len(patron) == 3:
        antecedente = (patron[0],)
        consecuente = patron[1]
        
        freq_ant = conteo_patrones.get(antecedente, 0)
        if freq_ant > 0:
            confianza = conteo / freq_ant
            
            if confianza >= 0.7:
                print(f"Regla de asociación: {antecedente} -> {consecuente}, Confianza: {confianza:.2f}")
