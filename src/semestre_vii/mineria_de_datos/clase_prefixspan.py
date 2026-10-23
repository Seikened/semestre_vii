import pandas as pd
from prefixspan import PrefixSpan

datos = {
    'Cliente_ID': [101, 101, 101, 102, 102, 103, 103, 103, 104, 104, 105, 105, 106, 106, 106],
    'Fecha_Compra': [
        '2026-01-01', '2026-01-08', '2026-02-15',  # Cliente 101
        '2026-01-05', '2026-01-10',                # Cliente 102
        '2026-01-03', '2026-01-04', '2026-01-20',  # Cliente 103
        '2026-01-12', '2026-01-18',                # Cliente 104
        '2026-02-01', '2026-02-10',                # Cliente 105
        '2026-01-04', '2026-01-01', '2026-02-01'   # Cliente 106
    ],
    'Producto': [
        'Laptop', 'Funda', 'Mochila',
        'Laptop', 'Funda',
        'Smartphone', 'Funda', 'Cargador',
        'Laptop', 'Mouse',
        'Laptop', 'Funda',
        'Funda', 'Smartphone', 'Protector'
    ]
}

df = pd.DataFrame(datos)


df['fecha_compra'] = pd.to_datetime(df['Fecha_Compra'])

df_ordenado = df.sort_values(by=['Cliente_ID', 'fecha_compra'])

secuencias = df_ordenado.groupby('Cliente_ID')['Producto'].apply(list)

print(secuencias)

ps = PrefixSpan(secuencias.tolist())

patrones_frecuentes = ps.frequent(minsup=2)

conteo_patrones = {tuple(p[1]): p[0] for p in patrones_frecuentes}

for patron, conteo in conteo_patrones.items():
    if len(patron) == 2:
        antecedente = (patron[0],)
        consecuente = patron[1]
        
        freq_ant = conteo_patrones.get(antecedente, 0)
        if freq_ant > 0:
            confianza = conteo / freq_ant
            print(f"Regla de asociación: {antecedente} -> {consecuente}, Confianza: {confianza:.2f}")