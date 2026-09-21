# 04 · Modelos y evaluación

## Principio de selección

El modelo se selecciona mediante **rolling-origin backtesting** sobre las propias estaciones.

No se hace split aleatorio de filas. Cada evaluación debe simular el uso real: entrenar o condicionar sólo con el pasado y predecir un bloque futuro.

Un modelo complejo sólo permanece si supera de forma reproducible a referencias simples bajo el mismo protocolo.

## Baselines obligatorios

Antes de conservar una arquitectura avanzada:

- Seasonal Naive;
- media o mediana móvil cuando tenga sentido;
- modelo tabular con rezagos y covariables si aporta una referencia útil.

El baseline no es una formalidad: define si la complejidad adicional realmente agrega señal.

## Hipótesis de modelado

La hipótesis inicial es evaluar un **modelo global** que aprenda de muchas estaciones y productos relacionados, incorporando identidad de sucursal y otras covariables útiles.

Una afinación o modelo individual por sucursal sólo se adopta si la evidencia muestra una mejora que justifique su costo operativo.

## Modelos candidatos

### Modelos específicos de forecasting

- **DeepAR**: referencia probabilística global para múltiples series relacionadas.
- **Temporal Fusion Transformer (TFT)**: forecasting multi-horizonte con variables estáticas, históricas y futuras conocidas.
- **N-HiTS**: arquitectura diseñada para horizontes largos mediante múltiples escalas.
- **TiDE**: encoder-decoder basado en MLP que sirve como recordatorio de que Transformer no implica automáticamente mejor desempeño.

### Foundation models

- **Chronos-2**: candidato para forecasting univariado, multivariado y con covariables, con salida probabilística.
- **TimesFM-3**: candidato zero-shot/multivariado con múltiples targets y covariables.

Ningún modelo es ganador por reputación, fecha de publicación o tamaño. Todos compiten bajo el mismo backtesting.

## Sistema vivo

```text
llega una nueva semana
        ↓
actualizar datos
        ↓
forecast con modelo vigente
        ↓
llega el valor real
        ↓
medir error y drift
        ↓
evaluar candidato / fine-tuning
        ↓
promover sólo si mejora
```

Actualizar datos y actualizar pesos son decisiones distintas.

## Horizontes

Horizontes técnicos iniciales:

```text
1 semana
4 semanas
12 semanas
26 semanas
52 semanas
```

La operación de reabastecimiento prioriza el corto plazo.

Una planeación de diez años no se tratará como 520 semanas con la misma certeza. Debe usar agregaciones mensuales, trimestrales o anuales, escenarios y una representación explícita de incertidumbre.

## Métricas

Como mínimo:

- MAE;
- RMSE;
- WAPE;
- bias.

Cuando el modelo produzca distribuciones, cuantiles o intervalos también se medirá cobertura y calibración apropiada.

MAPE se utilizará con cautela cuando existan valores cercanos a cero.

Las métricas deben reportarse:

- globalmente;
- por estación;
- por producto;
- por horizonte.

Un promedio no puede ocultar estaciones con comportamiento inaceptable.

## Objetivo comparativo

La planeación histórica propuso mejorar al menos **10 %** respecto de un baseline estacional. Este porcentaje permanece como meta inicial pendiente de confirmación y no debe manipular la evaluación.

## Confianza e incertidumbre

La UI necesita comunicar incertidumbre, pero todavía no se ha definido un único valor de “confianza”.

No convertir arbitrariamente una métrica estadística en un porcentaje de 0 a 100. La representación debe derivarse del tipo de forecast y de una interpretación defendible.

## Reentrenamiento

No se reentrenará automáticamente cada semana.

Primero deben existir:

- evaluación reproducible;
- versionado de datos y modelos;
- criterio de degradación;
- criterio de promoción;
- comparación contra el modelo vigente.

Un candidato sólo sustituye al vigente cuando la evidencia lo justifica.

## Referencias técnicas iniciales

- Salinas et al., *DeepAR: Probabilistic forecasting with autoregressive recurrent networks*, 2020.
- Lim et al., *Temporal Fusion Transformers for interpretable multi-horizon time series forecasting*, 2021.
- Challu et al., *N-HiTS: Neural Hierarchical Interpolation for Time Series Forecasting*.
- Das et al., *Long-term Forecasting with TiDE: Time-series Dense Encoder*.
- Ansari et al., *Chronos-2: From Univariate to Universal Forecasting*.
- Google Research, *TimesFM-3: A zero-shot foundation model for multivariate forecasting*, 2026.
