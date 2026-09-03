# Semestre VII

Repositorio de código, actividades ejecutables y entregables del séptimo semestre.

La estructura separa deliberadamente **código**, **datos locales**, **archivos temporales** y **entregables finales** para evitar imports frágiles, rutas ambiguas y archivos gigantes versionados por accidente.

## Estructura

```text
semestre_vii/
├── src/semestre_vii/                 # código Python importable
│   └── <materia>/
│       └── actividades/
│           └── <actividad>/          # una actividad autocontenida
├── entregas/                         # PDFs y artefactos finales versionados
├── data/                             # datasets y bases locales; no se versiona
├── tmp/                              # renders y archivos de trabajo; no se versiona
├── pyproject.toml                    # dependencias y entrypoints
└── AGENTS.md                         # reglas de trabajo del repositorio
```

Las carpetas `data/` y `tmp/` se crean localmente cuando hacen falta y están ignoradas por Git.

## Convención para materias y actividades

Los nombres de paquetes Python usan `snake_case`, sin espacios ni acentos. Cada materia vive en `src/semestre_vii/<materia>/` y cada ejercicio ejecutable en `actividades/<actividad>/`.

Una actividad debe exponer un `__main__.py` cuando tenga ejecución propia. Así puede ejecutarse desde cualquier punto del proyecto sin depender del directorio actual.

## Ejecución

Instalar o sincronizar el entorno:

```bash
uv sync
```

Ver los entrypoints disponibles:

```bash
uv run semestre-vii
```

ECOBICI, actividad entregada de Minería de Datos:

```bash
uv run ecobici --year 2025
```

También puede ejecutarse como módulo:

```bash
uv run python -m semestre_vii.mineria_de_datos.actividades.ecobici --year 2025
```

La actividad genera sus datos en `data/ecobici/`; la base DuckDB y los CSV descargados permanecen locales.

## Nueva actividad

Al agregar una nueva actividad ejecutable, crearla bajo la materia correspondiente, darle un `__main__.py` pequeño y registrar un alias en `[project.scripts]` sólo cuando sea útil ejecutarla con frecuencia.

Los resultados finales que deban conservarse se guardan en `entregas/`. Los renders, previews, caches y archivos intermedios pertenecen a `tmp/` y nunca al historial de Git.
