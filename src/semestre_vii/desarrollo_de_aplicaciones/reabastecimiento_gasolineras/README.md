# Pronóstico y reabastecimiento de gasolineras

**Desarrollo de Aplicaciones — Semestre VII.**

Sistema académico de apoyo al reabastecimiento de combustible para una distribuidora que atiende aproximadamente **120 gasolineras**. La aplicación integra autenticación, operación de sucursales, revisión administrativa y un motor de forecasting con evaluación continua.

## Fuente canónica

Desde el **21 de septiembre de 2026**, este directorio es la fuente canónica del producto.

La planeación original se desarrolló en el vault Traveler y se conserva allí como **snapshot histórica**. A partir de esta migración, las decisiones, ajustes y documentación nueva deben ocurrir aquí. Si la snapshot de Traveler y este repositorio divergen, prevalece este repositorio.

## Principio del producto

El sistema debe conectar el cierre semanal de una sucursal con una recomendación de suministro, permitir que una persona la acepte, modifique o ignore, y después comparar la predicción con el resultado real.

```text
cierre semanal
      ↓
validación de datos
      ↓
forecast + incertidumbre
      ↓
recomendación de suministro
      ↓
pedido de la sucursal
      ↓
revisión administrativa
      ↓
resultado real
      ↓
evaluación y aprendizaje
```

La retroalimentación semanal **no implica reentrenar automáticamente** los pesos del modelo.

## Estructura

```text
reabastecimiento_gasolineras/
├── README.md
├── docs/
│   ├── README.md
│   ├── 01_producto_y_alcance.md
│   ├── 02_operacion_y_flujos.md
│   ├── 03_datos.md
│   ├── 04_modelos_y_evaluacion.md
│   ├── 05_arquitectura.md
│   └── 06_plan_de_trabajo.md
├── backend/
│   └── AGENTS.md
└── frontend/
    └── AGENTS.md
```

Los datos y modelos locales viven fuera del paquete importable:

```text
data/desarrollo_de_aplicaciones/reabastecimiento_gasolineras/
models/desarrollo_de_aplicaciones/reabastecimiento_gasolineras/
```

Las rutas públicas del producto son:

```python
from semestre_vii.desarrollo_de_aplicaciones.reabastecimiento_gasolineras import (
    PROJECT_DATA_DIR,
    PROJECT_MODELS_DIR,
)
```

## Estado actual

La fase vigente es de **planeación y definición técnica**. Todavía no se ha fijado framework HTTP, base de datos, sistema de autenticación ni framework frontend. Primero se estabilizan producto, datos, evaluación y fronteras; la implementación se construirá encima de estas decisiones.
