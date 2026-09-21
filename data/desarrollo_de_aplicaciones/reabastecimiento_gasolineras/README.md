# Datos · Reabastecimiento de gasolineras

Raíz local de datos del sistema de pronóstico y apoyo al reabastecimiento.

El código accede a esta carpeta mediante
`semestre_vii.desarrollo_de_aplicaciones.reabastecimiento_gasolineras.PROJECT_DATA_DIR`.
No se usan rutas absolutas.

```text
data/desarrollo_de_aplicaciones/reabastecimiento_gasolineras/
├── raw/
├── external/
├── processed/
├── features/
├── backtests/
├── predictions/
└── artifacts/
```

Los datasets operativos permanecen fuera de Git. `raw/` no se sobrescribe y todo dato derivado debe ser reproducible desde sus fuentes y el pipeline correspondiente.

La semántica completa de cada nivel vive en `src/semestre_vii/desarrollo_de_aplicaciones/reabastecimiento_gasolineras/docs/03_datos.md`.
