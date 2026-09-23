# Examen parcial 1

`examen_p1.py` lee `albums.csv`, `artists.csv`, `features.csv` y `popularity.csv` desde
`data/mineria_de_datos/`, sin depender del directorio desde el que se ejecute. Los archivos
`*_100.csv` son muestras que genera el examen en esa misma carpeta.

Desde la raíz del repositorio:

```bash
uv run python -m semestre_vii.mineria_de_datos.examen_p1.examen_p1
```

Las cuatro fuentes del examen fueron entregadas por el profesor. `features.csv` y
`popularity.csv` se conservan con Git LFS. En otro clon, instala Git LFS y ejecuta
`git lfs pull` desde la raíz si solo aparecen los archivos de referencia.

Para comprobar que recuperaste los mismos archivos del examen:

| Archivo | Tamaño en bytes | SHA-256 |
| --- | ---: | --- |
| `features.csv` | 456178368 | `456fc5a4d08ffafd3d5579173d6d9f8e412a413d9744bd60506fdc32f152ef2e` |
| `popularity.csv` | 175451915 | `c5ead69afed6ad8cf521d3ea3c533c8e84ccf30132b3464f567dc8f5ca02ec45` |
