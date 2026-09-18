# Datos · Proyecto 2

Directorio local del proyecto de pronóstico de demanda de combustible.

Los datasets operativos **no se versionan**. El código accede a esta raíz mediante
`semestre_vii.aprendizaje_automatico_iii.proyecto_2.PROJECT_DATA_DIR`, evitando rutas absolutas y dependencias del directorio actual.

La estructura prevista es:

```text
data/aprendizaje_automatico_iii/proyecto_2/
├── raw/           # exportaciones originales, inmutables
├── external/      # covariables externas opcionales
├── processed/     # tabla canónica limpia
├── features/      # derivados reproducibles cuando realmente hagan falta
├── backtests/     # predicciones históricas de evaluación
├── predictions/   # pronósticos emitidos
└── artifacts/     # métricas, reportes y metadatos de experimentos
```

`raw/` conserva la fuente original. Ningún proceso debe sobrescribirla. Todo dato derivado debe poder reconstruirse desde `raw/` y el código correspondiente.
