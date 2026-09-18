# 02 · Modelos y evaluación

## Regla principal

No seleccionar un modelo por novedad ni por leaderboard. Todos los candidatos compiten mediante **rolling-origin backtesting** sobre las mismas ventanas, horizontes y métricas.

Primero se construyen baselines; un modelo complejo sólo se conserva si demuestra una mejora reproducible.

## Baselines obligatorios

- **Seasonal Naive:** misma semana del ciclo anterior cuando exista estacionalidad anual.
- **Promedios/medianas móviles:** referencia local simple.
- **Modelo tabular con lags**, por ejemplo gradient boosting, si las covariables y rezagos justifican la comparación.

Estos modelos permiten saber si la red está aprendiendo algo útil o sólo añade complejidad.

## Modelos específicos de forecasting

**DeepAR** formalizó el aprendizaje probabilístico sobre muchas series relacionadas y sigue siendo una referencia útil para el concepto de modelo global.

**Temporal Fusion Transformer (TFT)** está diseñado para forecasting multi-horizonte con variables estáticas, entradas futuras conocidas y covariables históricas, además de mecanismos de interpretación.

**N-HiTS** ataca explícitamente forecasting de horizonte largo mediante interpolación jerárquica y muestreo a múltiples escalas.

**TiDE** demuestra que una arquitectura MLP encoder-decoder relativamente simple puede ser muy competitiva en forecasting largo con covariables. Es una referencia importante para no asumir que “Transformer” significa automáticamente “mejor”.

## Modelos fundacionales

### Chronos-2

Amazon presentó Chronos-2 en 2025 como un time-series foundation model capaz de trabajar en modo univariado, multivariado y con covariables. Usa atención temporal y atención entre series relacionadas, y genera pronósticos probabilísticos por cuantiles.

Es especialmente relevante como candidato porque Decathlon documentó en agosto de 2026 un sistema de demanda semanal en producción con Chronos-2, evaluando horizontes de 12 y 52 semanas. Su flujo ejecuta inferencia semanal y hace fine-tuning con mucha menor frecuencia, aproximadamente cada seis meses.

Eso respalda una arquitectura donde **datos nuevos no implican reentrenar pesos cada semana**.

### TimesFM-3

Google Research publicó TimesFM-3 el 31 de agosto de 2026. A diferencia de versiones anteriores estrictamente univariadas, TimesFM-3 incorpora forecasting multivariado y puede trabajar con múltiples series y covariables en una sola inferencia.

Es un candidato natural para comparar contra Chronos-2, no un ganador asumido.

## Cómo mantener el sistema “vivo”

El ciclo previsto es:

```text
nueva semana
    ↓
actualizar datos
    ↓
generar forecast con el modelo vigente
    ↓
cuando llega el dato real, medir error
    ↓
acumular backtesting y detectar degradación
    ↓
evaluar/fine-tunear candidato
    ↓
promoverlo sólo si supera al vigente
```

La actualización semanal de datos sí es normal. La actualización semanal de pesos **no es obligatoria** y puede introducir inestabilidad. La frecuencia de fine-tuning se decidirá con evidencia de backtesting y drift.

## Validación

Nunca se hace un split aleatorio de filas.

El backtesting debe simular el uso real: entrenar/condicionar sólo con el pasado y predecir un bloque futuro. Después se avanza el corte y se repite.

Horizontes iniciales sugeridos:

```text
1 semana
4 semanas
12 semanas
26 semanas
52 semanas
```

Métricas candidatas:

- MAE para error absoluto interpretable;
- RMSE para penalizar errores grandes;
- WAPE para demanda agregada;
- bias para detectar sobre/subestimación sistemática;
- cobertura de intervalos cuando haya forecast probabilístico.

MAPE debe tratarse con cuidado cuando el denominador pueda acercarse a cero.

Las métricas deben reportarse globalmente y también por estación, producto y horizonte. Un promedio general puede ocultar estaciones problemáticas.

## Diez años

Seis años semanales equivalen aproximadamente a 312 observaciones por serie, mientras que diez años futuros son unas 520 semanas.

Por eso el proyecto separará:

- forecast operacional semanal;
- forecast anual/estratégico agregado;
- escenarios de largo plazo con supuestos explícitos.

La precisión de corto plazo no se extrapola automáticamente a diez años.

## Referencias

- Salinas et al., **DeepAR: Probabilistic forecasting with autoregressive recurrent networks**, International Journal of Forecasting, 2020. https://doi.org/10.1016/j.ijforecast.2019.07.001
- Lim et al., **Temporal Fusion Transformers for interpretable multi-horizon time series forecasting**, International Journal of Forecasting, 2021. https://doi.org/10.1016/j.ijforecast.2021.03.012
- Challu et al., **N-HiTS: Neural Hierarchical Interpolation for Time Series Forecasting**. https://arxiv.org/abs/2201.12886
- Das et al., **Long-term Forecasting with TiDE: Time-series Dense Encoder**. https://arxiv.org/abs/2304.08424
- Ansari et al., **Chronos-2: From Univariate to Universal Forecasting**, 2025. https://arxiv.org/abs/2510.15821
- Amazon Science, **Introducing Chronos-2: From univariate to universal forecasting**, 2025. https://www.amazon.science/blog/introducing-chronos-2-from-univariate-to-universal-forecasting
- AWS / Decathlon, **How Decathlon runs demand forecasting at scale with Chronos-2**, 28 Aug 2026. https://aws.amazon.com/blogs/machine-learning/how-decathlon-runs-demand-forecasting-at-scale-with-chronos-2/
- Google Research, **TimesFM-3: A zero-shot foundation model for multivariate forecasting**, 31 Aug 2026. https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/
- Pendyala et al., **Assessing Covariate-Informed Grid Load Forecasting with a Time-Series Foundation Model**, 2026. https://arxiv.org/abs/2609.06656
