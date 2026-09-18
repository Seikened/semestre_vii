# 01 · Producto y datos

## Problema

La aplicación debe ayudar a estimar la demanda de combustible de una red de aproximadamente 120 estaciones.

La unidad principal será una observación por:

```text
semana × estación × producto
```

Con tres productos principales existirían aproximadamente 360 series relacionadas.

## Esquema mínimo

La tabla canónica utilizará formato largo:

| Campo | Papel |
| --- | --- |
| `week` | semana de la observación |
| `station_id` | identificador de estación |
| `product` | Magna, Premium, Diésel u otra categoría válida |
| `liters` | variable objetivo |

Covariables candidatas, sólo cuando existan y sean confiables:

| Campo | Uso |
| --- | --- |
| `price` | precio histórico; futuro sólo como dato conocido o escenario |
| `holiday` | calendario conocido con anticipación |
| `promotion` | campaña conocida con anticipación |
| clima / movilidad | señal externa observada o pronosticada |

Una variable que no estaría disponible al momento real de predecir no puede usarse como entrada futura: hacerlo produciría **data leakage**.

## Datos originales y derivados

`raw/` conserva la exportación original y nunca se sobrescribe.

`processed/` contiene la tabla semanal canónica ya validada.

`features/` sólo almacena derivados cuando no sea más claro calcularlos dentro del pipeline.

`backtests/` conserva forecasts emitidos sobre cortes históricos.

`predictions/` conserva pronósticos reales del producto.

`artifacts/` conserva métricas y metadatos suficientes para reconstruir una comparación.

## Calidad temporal

Antes de modelar deben detectarse semanas faltantes, duplicados por estación/producto/semana, cambios de identificadores, cierres temporales y valores imposibles.

Una semana sin venta no equivale automáticamente a un dato faltante. Esa diferencia debe resolverse con la fuente antes de imputar.

## Producto, no sólo modelo

El motor predictivo debe quedar detrás de una frontera clara para que la aplicación pueda cambiar de modelo sin reescribir el resto del producto.

La aplicación consumirá una salida estable: serie, fecha de corte, horizonte, predicción e incertidumbre cuando exista. La elección concreta del algoritmo permanece interna al motor.
