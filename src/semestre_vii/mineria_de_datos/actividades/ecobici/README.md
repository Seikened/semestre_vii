# Actividad ECOBICI

**Estado:** entregada.

Esta actividad descarga el histórico público de viajes de ECOBICI, normaliza los CSV con Polars y persiste la capa cruda en DuckDB.

El código de la actividad vive completo dentro de esta carpeta. Los datos generados se escriben en `data/ecobici/` y no forman parte del repositorio.

## Ejecutar

Desde la raíz del proyecto:

```bash
uv run ecobici --year 2025
```

Para todos los años publicados:

```bash
uv run ecobici --all
```

Como módulo Python:

```bash
uv run python -m semestre_vii.mineria_de_datos.actividades.ecobici --year 2025
```
