# Datos · Proyecto 1

Raíz local de datos del sistema predictivo de gasolineras.

El código accede a esta carpeta mediante
`semestre_vii.desarrollo_de_aplicaciones.proyecto_1.PROJECT_DATA_DIR`.
No se usan rutas absolutas.

```text
data/desarrollo_de_aplicaciones/proyecto_1/
├── raw/           # exportaciones originales; nunca se sobrescriben
├── external/      # covariables externas opcionales
├── processed/     # tabla semanal canónica y validada
├── features/      # derivados reproducibles cuando sean necesarios
├── backtests/     # predicciones históricas para evaluación
├── predictions/   # forecasts emitidos por el sistema
└── artifacts/     # métricas y metadatos de experimentos
```

Los datasets operativos permanecen fuera de Git. Todo dato derivado debe poder reconstruirse desde `raw/` y el código correspondiente.
