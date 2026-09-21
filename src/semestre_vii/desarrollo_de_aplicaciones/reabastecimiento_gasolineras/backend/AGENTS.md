# AGENTS.md — Reabastecimiento de Gasolineras · Backend

Estas reglas complementan el AGENTS.md de la raíz y gobiernan únicamente este directorio.

El backend de Reabastecimiento de Gasolineras adopta la filosofía de ingeniería de Sol, adaptada al sistema predictivo de abastecimiento de gasolineras. La intención es reutilizar sus buenas prácticas, no copiar nombres, dominio ni infraestructura que todavía no existan aquí.

## Fuentes obligatorias

Antes de modificar backend, leer:

1. ../../../../../AGENTS.md
2. ../README.md
3. ../docs/README.md
4. ../docs/01_producto_y_alcance.md
5. ../docs/02_operacion_y_flujos.md
6. ../docs/03_datos.md
7. ../docs/04_modelos_y_evaluacion.md
8. ../docs/05_arquitectura.md
9. ../docs/06_plan_de_trabajo.md

Si aparece documentación de arquitectura, contratos HTTP, persistencia o seguridad dentro del proyecto, pasa a ser fuente obligatoria para el área correspondiente.

## Límite del área

- Backend posee lógica de dominio, validación, contratos, forecasting, backtesting, persistencia e integraciones confiables.
- Expone capacidades al frontend; no dicta presentación ni interacción visual.
- No modificar ../frontend por conveniencia.
- Un cambio transversal requiere un contrato explícito y validación de ambos lados.
- Framework HTTP, base de datos, autenticación, colas y concurrencia sólo se introducen cuando exista un caso real.
- El forecasting es una capacidad del producto, no toda la aplicación.

## Dominio del proyecto

El sistema debe conservar una separación explícita entre:

~~~text
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
~~~

No mezclar adquisición de datos, preparación, entrenamiento, evaluación, publicación de predicciones y serving en una sola pieza.

Operación y planeación son horizontes distintos. Una predicción de corto plazo y una proyección de largo plazo no deben compartir supuestos de confianza por conveniencia.

## Datos y reproducibilidad

- Usar PROJECT_DATA_DIR y PROJECT_MODELS_DIR como raíces públicas del proyecto.
- No introducir rutas absolutas.
- Distinguir raw, external, processed, features, backtests, predictions y artifacts según la estructura aprobada.
- Un transform derivado debe poder rastrearse hasta su entrada y configuración.
- Splits temporales respetan causalidad; nunca filtrar información futura al entrenamiento o al tuning.
- Métricas, ventanas, horizonte, frecuencia, seed y configuración relevante deben quedar explícitos.
- Mantener separada la predicción vigente de los resultados históricos de backtesting.
- Checkpoints, caches, datasets pesados y artefactos reconstruibles no se versionan salvo decisión explícita.
- No tratar una métrica aislada como evidencia suficiente de calidad del producto.

## Modelado y reutilización

- Revisar DTO, modelos, adapters, servicios, pipelines y utilidades existentes antes de crear una pieza.
- No crear capas por simetría.
- Una clase requiere estado, invariantes o ciclo de vida.
- La herencia requiere sustitución real.
- Preferir composición y funciones directas antes de jerarquías.
- No mantener un modelo interno paralelo a un contrato validado sin una razón concreta.
- Reutilizar las reglas de typing del AGENTS.md raíz: alto valor, baja ceremonia.

## Formato Python

Las declaraciones se mantienen compactas y horizontales por defecto mientras la línea sea razonablemente legible y Ruff no exija partirla.

El formato vertical es apropiado para construcción de objetos, llamadas complejas y estructuras donde realmente mejore la lectura.

No introducir saltos de línea como ceremonia visual.

## Contratos y Pydantic

Cuando el backend exponga datos fuera de su módulo:

- Usar modelos explícitos para conceptos estructurados.
- Usar Pydantic cuando importe validación, parsing, serialización o schemas.
- No usar dicts anónimos como contrato estable.
- Validar datos externos una vez en la frontera y trabajar después con representaciones confiables.
- No confundir cast con validación.
- Un cambio incompatible de contrato requiere diseño explícito y migración.

## APIs

Si se introduce HTTP:

- Mantener una única forma compartida de éxito y error.
- Los handlers traducen errores de aplicación a transporte.
- La lógica de dominio no depende de FastAPI, status codes ni objetos Request.
- Los mensajes públicos no exponen excepciones crudas, queries, credenciales ni secretos.
- Los códigos de error deben pertenecer a un catálogo controlado, no ser strings improvisados.
- OpenAPI y schemas deben reflejar el comportamiento real.

No introducir FastAPI sólo porque Sol lo use. El framework se elige cuando el proyecto necesite una API.

## Persistencia

- El esquema físico pertenece al backend.
- El frontend nunca depende directamente de tablas, archivos de base de datos o detalles del ORM.
- Mantener lógica de negocio fuera del adapter de persistencia.
- Una repository abstraction sólo se introduce cuando exista una frontera real que justifique el costo.
- Migraciones deben ser reproducibles y revisables.
- SQLite, PostgreSQL u otra base se eligen por necesidades reales del proyecto, no por imitación.

## Errores

- Centralizar conceptualmente errores propios de aplicación y dominio.
- Los adapters traducen errores externos.
- Los endpoints o jobs traducen errores propios a su representación pública.
- No capturar Exception indiscriminadamente.
- No devolver éxito para representar una falla.
- Preservar el error original como causa cuando sea útil para debugging interno sin filtrarlo al consumidor.

## Seguridad

- Toda entrada externa es no confiable hasta validarse.
- Autorización, si existe, se aplica en backend.
- No versionar secretos ni credenciales.
- No incluir tokens o payloads sensibles en logs.
- Un frontend ocultando una acción no reemplaza autorización.
- No implementar autenticación antes de que exista un caso de producto que la necesite.

## Soporte a la experiencia de usuario

El frontend es dueño de aplicar UX, pero el backend debe permitirla.

Los contratos deben poder distinguir estados reales: aceptado, pendiente, completado, fallido o equivalentes cuando existan.

Exponer lenguaje del dominio, no nombres de tablas, columnas internas ni detalles del proveedor.

Validar combinaciones inválidas antes de producir efectos.

Entregar errores estructurados y accionables que permitan al frontend explicar qué ocurrió y cómo recuperarse.

Evitar round trips que sólo compensen una frontera mal diseñada, sin inventar endpoints genéricos por anticipación.

## Pruebas

Toda regla de negocio, preparación de datos, métrica, split temporal, backtest, serializer y transform relevante debe tener evidencia proporcional.

- Unit tests para lógica determinista.
- Tests de contrato para fronteras.
- Tests de integración cuando exista persistencia o servicios externos.
- Tests de regresión para bugs reales.
- No mockear la propia regla que se intenta demostrar.
- No debilitar assertions para conseguir verde.
- En forecasting, comparar modelos bajo el mismo protocolo de backtesting.

Durante construcción ejecutar primero pruebas focales. Antes de declarar listo el backend, cerrar con los gates aplicables desde la raíz:

~~~bash
uv run ruff check src/semestre_vii/desarrollo_de_aplicaciones/reabastecimiento_gasolineras tests/desarrollo_de_aplicaciones
uv run pytest tests/desarrollo_de_aplicaciones
uv build
~~~

Si todavía no existe una suite específica para backend, no inventar un comando falso; añadir la estructura de pruebas junto con la primera capacidad que la necesite.

## Git y alcance

- El cambio de backend debe permanecer dentro de su alcance salvo tarea transversal explícita.
- No modificar frontend para ocultar una incompatibilidad.
- Documentar dependencias de frontend cuando el contrato todavía no tenga consumidor.
- Un PR significativo debe explicar qué cambió, por qué, cómo se validó y cualquier deuda deliberadamente aceptada.
- Fernando conserva la decisión final de merge.
