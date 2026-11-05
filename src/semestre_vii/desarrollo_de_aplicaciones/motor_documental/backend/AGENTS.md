# Servicio documental

Leer primero `../AGENTS.md`, `../DEVELOPMENT.md` y `../docs/README.md`.

- `app/` contiene extracción, fragmentación y vectorización reales.
- `pyproject.toml` y `uv.lock` definen el entorno independiente Python 3.12.
- `demo/` del proyecto contiene únicamente material ficticio y verificaciones reproducibles.
- La recuperación se verifica sin LLM. El chat opcional con Luna tiene aprobación expresa de Fernando.
- Validar el contenido real de los formatos, no solo su extensión.
- Comparar fidelidad de OCR y recuperación de fuente por separado.
- Conservar revisión y dimensión del modelo de embeddings.
- La API, PostgreSQL y Compose amplían la primera porción; conservar evidencia específica de cada recorrido.
- Fernando autorizó cuatro tablas, CRUD, acceso y después el MVP de Luna: Responses y una herramienta que reutiliza el motor.
- El chat admite una búsqueda y hasta dos llamadas OpenAI por turno; no usa Files, Vector Stores ni acciones de escritura.
- La clave del proveedor es privada, opcional y montada únicamente en API. Su ausencia no bloquea indexación ni recuperación.
- Mantener las reglas clean-python, errores tipados y verificación académica de la raíz.
