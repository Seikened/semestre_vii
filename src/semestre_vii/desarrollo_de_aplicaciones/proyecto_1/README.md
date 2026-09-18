# Proyecto 1 · Sistema predictivo de abastecimiento de gasolineras

**Desarrollo de Aplicaciones — Semestre VII.**

El producto apoyará la planeación de abastecimiento de aproximadamente **120 gasolineras**. El motor predictivo trabajará con demanda semanal y distinguirá productos como **Magna, Premium y Diésel**.

El forecasting es una capacidad del producto, no toda la aplicación.

## Objetivo inicial

El sistema debe evolucionar hacia un flujo como:

```text
datos históricos
      ↓
validación y preparación
      ↓
motor de forecasting
      ↓
backtesting + incertidumbre
      ↓
predicción vigente
      ↓
consumo por la aplicación
```

La primera etapa se concentra en definir correctamente **datos, evaluación y modelos candidatos** antes de construir interfaz, API o persistencia adicional.

## Estructura

```text
src/semestre_vii/desarrollo_de_aplicaciones/
├── __init__.py
├── README.md
└── proyecto_1/
    ├── __init__.py
    ├── README.md
    └── docs/
        ├── README.md
        ├── 01_producto_y_datos.md
        └── 02_modelos_y_evaluacion.md

data/desarrollo_de_aplicaciones/proyecto_1/
├── raw/
├── external/
├── processed/
├── features/
├── backtests/
├── predictions/
└── artifacts/

models/desarrollo_de_aplicaciones/proyecto_1/
└── ...
```

Las rutas públicas del proyecto son:

```python
from semestre_vii.desarrollo_de_aplicaciones.proyecto_1 import (
    PROJECT_DATA_DIR,
    PROJECT_MODELS_DIR,
)
```

## Dos horizontes

El producto necesita separar dos preguntas distintas:

**Operación:** cuánto combustible se necesitará en las próximas semanas para apoyar la siguiente carga.

**Planeación:** cómo podría evolucionar la demanda en varios años.

Con unos seis años de histórico hay aproximadamente 312 observaciones semanales por serie. Un horizonte directo de diez años equivale a unas 520 semanas futuras, por lo que la planeación de largo plazo se tratará con agregación, incertidumbre y escenarios; no como si la semana 520 tuviera la misma confiabilidad que la siguiente semana.

## Estado

Todavía no hay pipeline de entrenamiento ni dependencias nuevas. Primero se fija el contrato de datos y la forma de evaluación. Después se implementan los baselines y se comparan modelos modernos bajo el mismo backtesting.
