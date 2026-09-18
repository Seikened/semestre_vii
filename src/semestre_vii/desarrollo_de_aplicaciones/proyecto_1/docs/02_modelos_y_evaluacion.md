# 02 · Modelos y evaluación

## Criterio de selección

El modelo se seleccionará mediante **rolling-origin backtesting** sobre nuestras propias estaciones.

No habrá split aleatorio de filas: cada evaluación debe simular el uso real, condicionando únicamente con el pasado y prediciendo un bloque futuro.

Un modelo complejo sólo se conserva si supera de forma reproducible a referencias simples.

## Baselines

Antes de usar un foundation model:

- **Seasonal Naive** para comparar contra la misma etapa del ciclo anterior.
- medias o medianas móviles;
- un modelo tabular con rezagos y covariables cuando tenga sentido.

Estos baselines son obligatorios porque permiten medir si la complejidad adicional realmente aporta señal.

## Modelos específicos de forecasting

**DeepAR** es una referencia importante para modelos globales probabilísticos entrenados sobre muchas series relacionadas.

**Temporal Fusion Transformer (TFT)** trabaja con forecasting multi-horizonte, variables estáticas, covariables históricas y entradas futuras conocidas.

**N-HiTS** fue diseñado específicamente para forecasting de horizonte largo mediante interpolación jerárquica y múltiples escalas.

**TiDE** demuestra que una arquitectura encoder-decoder basada en MLP puede competir fuertemente en forecasting largo; Transformer no significa automáticamente mejor.

## Foundation models

### Chronos-2

Chronos-2, de Amazon, amplía la familia Chronos hacia forecasting univariado, multivariado y con covariables, produciendo además pronósticos probabilísticos.

Es relevante para este proyecto porque Decathlon documentó en 2026 un sistema de forecasting de demanda semanal con Chronos-2 para horizontes de 12 y 52 semanas. Su operación genera pronósticos semanalmente y hace fine-tuning con una frecuencia mucho menor.

Eso respalda separar **actualización de datos** de **actualización de pesos**.

### TimesFM-3

Google Research presentó TimesFM-3 el 31 de agosto de 2026. Esta versión incorpora forecasting multivariado, múltiples targets y covariables, por lo que es un candidato natural para una red de estaciones y productos relacionados.

Se evaluará como competidor, no como ganador asumido.

## Sistema “vivo”

El ciclo esperado es:

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
promover sólo si mejora al vigente
```

No se reentrenarán pesos automáticamente cada semana salvo que la evidencia lo justifique.

## Horizontes iniciales

```text
1 semana
4 semanas
12 semanas
26 semanas
52 semanas
```

Para diez años se usarán agregaciones mensuales, trimestrales o anuales y escenarios explícitos.

## Métricas

Se evaluarán, como mínimo, MAE, RMSE, WAPE y bias. Cuando el modelo produzca distribuciones o cuantiles también se medirá cobertura de intervalos.

MAPE se usará con cautela cuando existan valores cercanos a cero.

Las métricas se reportarán globalmente y por estación, producto y horizonte para evitar que un promedio esconda fallos locales.

## Referencias

- Salinas et al., **DeepAR: Probabilistic forecasting with autoregressive recurrent networks**, International Journal of Forecasting, 2020. https://doi.org/10.1016/j.ijforecast.2019.07.001
- Lim et al., **Temporal Fusion Transformers for interpretable multi-horizon time series forecasting**, International Journal of Forecasting, 2021. https://doi.org/10.1016/j.ijforecast.2021.03.012
- Challu et al., **N-HiTS: Neural Hierarchical Interpolation for Time Series Forecasting**. https://arxiv.org/abs/2201.12886
- Das et al., **Long-term Forecasting with TiDE: Time-series Dense Encoder**. https://arxiv.org/abs/2304.08424
- Ansari et al., **Chronos-2: From Univariate to Universal Forecasting**, 2025. https://arxiv.org/abs/2510.15821
- Amazon Science, **Introducing Chronos-2: From univariate to universal forecasting**, 2025. https://www.amazon.science/blog/introducing-chronos-2-from-univariate-to-universal-forecasting
- AWS / Decathlon, **How Decathlon runs demand forecasting at scale with Chronos-2**, 28 Aug 2026. https://aws.amazon.com/blogs/machine-learning/how-decathlon-runs-demand-forecasting-at-scale-with-chronos-2/
- Google Research, **TimesFM-3: A zero-shot foundation model for multivariate forecasting**, 31 Aug 2026. https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/
