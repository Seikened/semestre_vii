# 01 · Problema y datos

## Unidad de observación

La representación principal será **long format**: una fila por estación, producto y semana.

Esquema mínimo esperado:

| Campo | Papel |
| --- | --- |
| `week` | inicio o identificador consistente de la semana |
| `station_id` | estación |
| `product` | Magna, Premium, Diésel u otra categoría válida |
| `liters` | variable objetivo |

Covariables candidatas, sólo cuando existan y sean confiables:

| Campo | Uso |
| --- | --- |
| `price` | precio histórico; futuro sólo si realmente es conocido o se modela como escenario |
| `holiday` | calendario conocido con anticipación |
| `promotion` | campaña conocida con anticipación |
| clima / movilidad | variable externa observada o pronosticada, si aporta señal |

No se debe usar una variable futura que en producción no estaría disponible. Eso produciría **data leakage**.

## Series relacionadas

Con 120 estaciones y tres combustibles principales existen aproximadamente 360 series relacionadas. El diseño parte de un **modelo global** capaz de aprender patrones compartidos, en lugar de obligar a mantener cientos de modelos independientes.

La estación y el producto identifican la serie. No deben convertirse automáticamente en una columna numérica ordinal: su representación dependerá del modelo.

## Resolución temporal

La frecuencia operativa es semanal. Primero deben detectarse:

- semanas faltantes;
- duplicados por estación/producto/semana;
- cambios de catálogo o identificadores;
- cierres temporales;
- valores imposibles o correcciones administrativas.

Una semana sin venta no equivale necesariamente a un dato faltante. Esa diferencia debe resolverse con la fuente antes de imputar.

## Capas de datos

`raw/` contiene la exportación original y es inmutable.

`processed/` contiene la tabla semanal canónica validada.

`features/` almacena derivados únicamente cuando no sea más claro calcularlos durante el pipeline.

`backtests/` conserva las predicciones generadas sobre cortes históricos.

`predictions/` conserva forecasts reales emitidos por versión de modelo y fecha de corte.

`artifacts/` conserva métricas y metadatos suficientes para reproducir cada comparación.

## Dos horizontes distintos

**Operativo:** siguiente semana, 4, 12, 26 y hasta 52 semanas según el uso.

**Estratégico:** varios años. Para diez años se trabajará con agregaciones mensuales/trimestrales/anuales y escenarios. No se presentará una secuencia semanal de 520 pasos como si tuviera la misma confiabilidad que el siguiente abastecimiento.

La incertidumbre debe crecer con el horizonte y formar parte del resultado cuando el modelo lo permita.
