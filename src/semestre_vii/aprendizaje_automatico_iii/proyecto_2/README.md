# Proyecto 2 · Pronóstico de demanda de gasolineras

**Aprendizaje Automático III — Semestre VII.**

El proyecto estudia el pronóstico de demanda semanal de combustible para aproximadamente **120 estaciones**, separando al menos **Magna, Premium y Diésel**. La variable objetivo principal será la cantidad demandada en litros; estación y producto identifican cada serie y el tiempo define su secuencia.

## Objetivo

Construir un sistema de forecasting que responda dos necesidades diferentes:

1. **Operación:** estimar la siguiente carga y horizontes cortos/medios en semanas.
2. **Planeación:** estudiar horizontes largos agregados, sin confundir una proyección estratégica con un forecast semanal confiable a diez años.

Con seis años de historia hay alrededor de 312 observaciones semanales por serie. Predecir 520 semanas directamente sería un horizonte mayor que la historia disponible por serie, por lo que el proyecto tratará el horizonte de diez años mediante agregación y escenarios, no como una única extrapolación semanal ciega.

## Estructura

```text
proyecto_2/
├── __init__.py             # rutas del proyecto
├── README.md               # alcance y reglas principales
└── docs/
    ├── README.md
    ├── 01_problema_y_datos.md
    └── 02_modelos_y_evaluacion.md

data/aprendizaje_automatico_iii/proyecto_2/
├── raw/
├── external/
├── processed/
├── features/
├── backtests/
├── predictions/
└── artifacts/

models/aprendizaje_automatico_iii/proyecto_2/
└── ...                     # sólo artefactos publicados explícitamente
```

El código nunca debe depender de rutas absolutas. Para acceder a los datos o modelos:

```python
from semestre_vii.aprendizaje_automatico_iii.proyecto_2 import PROJECT_DATA_DIR, PROJECT_MODELS_DIR
```

## Estrategia inicial

Antes de entrenar una red se construirán **baselines simples** y un backtesting temporal reproducible. Después se compararán modelos específicos de forecasting y modelos fundacionales modernos como **Chronos-2** y **TimesFM-3**.

El criterio no será qué arquitectura es más nueva, sino cuál generaliza mejor sobre cortes temporales futuros de nuestras propias estaciones.

Todavía no hay pipeline de entrenamiento ni dependencias nuevas por diseño. Esta primera etapa fija el contrato de datos, la evaluación y la organización del proyecto antes de implementar.
