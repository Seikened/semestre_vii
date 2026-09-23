# AGENTS.md — Semestre VII

Este documento define la forma de trabajo para todo el repositorio de Semestre VII.

La prioridad es construir software **mínimo, explícito, verificable, cohesionado y mantenible**. DRY, SOLID, orientación a objetos, patrones y arquitecturas sofisticadas son herramientas; nunca son objetivos por sí mismos.

Los AGENTS.md más profundos complementan estas reglas y tienen prioridad dentro de su propio alcance. Una regla local puede especializar la política global, pero no debe debilitar seguridad, trazabilidad, verificación ni separación de responsabilidades.

## Lectura obligatoria

Antes de planificar, implementar o revisar un cambio:

1. Leer el README.md de la raíz.
2. Leer el README.md de la materia y del proyecto afectado cuando existan.
3. Leer todos los AGENTS.md aplicables desde la raíz hasta el directorio que se modificará.
4. Revisar implementaciones, datos y contratos existentes relacionados con el cambio.
5. No asumir arquitectura, dependencias o convenciones que el repositorio todavía no tenga.

AGENTS.md funciona como índice operativo. Los documentos de arquitectura, producto, datos o diseño de cada proyecto son las fuentes de verdad de sus decisiones específicas.

## Propiedad por área

- Cada materia y proyecto conserva su propio dominio y estructura.
- Backend posee lógica de dominio, contratos, persistencia, procesamiento, seguridad e integraciones confiables.
- Frontend posee navegación, presentación, interacción y estado puramente de interfaz.
- Datos, modelos, notebooks, scripts y artefactos mantienen las fronteras declaradas por cada proyecto.
- Un agente asignado a un área no modifica otra por conveniencia ni para evitar un contrato.
- Un cambio transversal requiere alcance explícito y validación de todas las áreas involucradas.
- Frontend y backend nunca se comunican leyendo directamente persistencia, archivos privados o estado interno del otro.

## Filosofía de implementación

- Antes de crear una pieza, inventariar implementaciones existentes.
- Si se agrega una nueva, su diferencia funcional o arquitectónica debe quedar visible en el diseño, el código o la descripción del pull request.
- Preferir código pequeño, directo y cohesionado.
- No crear capas por simetría visual.
- No crear wrappers, managers, services, repositories, factories o clases sólo para que el diseño parezca más formal.
- No mantener dos fuentes de verdad para la misma regla.
- La abstracción debe aparecer después de que exista una necesidad real, no antes.
- Una clase requiere una razón de estado, invariantes o ciclo de vida.
- La herencia requiere una relación real de sustitución.
- Ante dos soluciones funcionalmente equivalentes, elegir la que tenga menos estado, menos duplicación, menos abstracciones, contratos más claros y verificación más sencilla.

## Python

Python es el lenguaje principal del repositorio para backend, datos, machine learning, visión y automatización.

- Administrar dependencias y entornos con uv.
- Mantener compatibilidad con la versión declarada en pyproject.toml.
- Aplicar una filosofía clean-python: legibilidad primero, responsabilidades claras y ausencia de complejidad accidental.
- Mantener declaraciones compactas y horizontales cuando sigan siendo legibles y Ruff no obligue a partirlas.
- No agregar __all__ salvo que un módulo se convierta deliberadamente en una librería pública.
- No usar diccionarios anónimos para representar datos estructurados que crucen fronteras importantes.
- No esconder incertidumbre de runtime mediante typing estático.
- Los errores deben fallar de forma explícita y conservar suficiente contexto para diagnóstico sin exponer secretos.

## Política de tipado Python — alto valor, baja ceremonia

El tipado existe para **hacer los datos y contratos más fáciles de entender, validar y mantener**. No es una métrica de cobertura.

La meta es:

> **Modelar significado, no maquinaria.**

Un tipo, modelo o anotación debe aportar al menos una utilidad concreta: claridad semántica, una forma útil de datos, validación real en runtime, automatización consumida por una herramienta o una relación importante entre valores.

### Datos simples

Si el tipo incorporado ya comunica correctamente el dato, usarlo directamente.

Preferir str, int, float, datetime, Path, list[str], dict[str, float] y equivalentes cuando expresen el concepto con claridad.

No envolver valores triviales en clases o modelos que no añadan reglas, validación o significado.

### Conceptos estructurados

Si una anotación compuesta necesita explicación para entender qué representa, considerar un objeto explícito antes que un alias más complejo.

Nombrar una estructura complicada no equivale a modelarla.

### Pydantic

Usar Pydantic cuando un dato estructurado necesite validación, parsing, coerción, serialización, schemas o invariantes en runtime.

Es especialmente apropiado para datos que cruzan fronteras: HTTP, JSON, configuración, usuarios, LLMs, tools, eventos, colas o servicios externos.

No introducir Pydantic sólo para envolver datos simples.

### dataclass

Usar dataclass para conceptos internos con identidad semántica que ya llegan confiables y no necesitan validación sofisticada en runtime.

### Annotated

Usar Annotated cuando su metadata active comportamiento real en Pydantic, FastAPI, validadores, serializers, dependency injection o herramientas equivalentes.

Metadata ignorada es ceremonia.

### Aliases

Los aliases deben comprimir significado simple o comportamiento reutilizable, no esconder estructuras profundamente complejas.

Si el alias oculta una estructura difícil de entender, probablemente falta un modelo.

### Funciones

No anotar funciones mecánicamente.

Anotar cuando reduzca ambigüedad, documente un contrato importante o active comportamiento real.

Una función interna, pequeña y evidente no necesita typing ceremonial.

### Duck typing

Resolvers, validators, adapters, handlers, strategies y colaboradores similares pueden definirse por comportamiento.

No crear Protocol automáticamente sólo porque existan varias implementaciones.

Formalizar una interfaz cuando el contrato formal tenga valor propio para la API o el diseño.

### Incertidumbre de runtime

Los datos externos deben validarse antes de considerarse confiables.

cast() no valida nada.

Usar isinstance, parsing explícito o model_validate cuando la forma real del dato sea incierta.

cast() sólo es razonable cuando una librería externa tiene typing incorrecto o incompleto y la validez ya está garantizada por otro mecanismo. Debe quedar localizado y justificado.

### Typing avanzado

TypeVar, Generic, Protocol, TypedDict y herramientas similares deben ganarse su complejidad.

La pregunta correcta es:

> ¿Qué información, garantía o relación útil desaparecería si quitáramos este tipo?

Si la respuesta es ninguna, probablemente sobra.

### Checkers

Pyright, mypy y herramientas equivalentes pueden detectar errores reales, pero no deben diseñar la arquitectura.

No introducir wrappers, casts, protocolos, jerarquías o aliases únicamente para dejar un checker en verde.

### Verificación académica

Los tipos comunican expectativas. No demuestran comportamiento. En este repositorio académico no se mantienen suites de tests. Verificar cada actividad con su ejecución real, los datos que utiliza y una revisión concreta de sus resultados.

## Datos, ciencia de datos y machine learning

- Distinguir datos originales de datos derivados.
- Mantener procedencia comprensible de limpieza, normalización, feature engineering, inferencias, predicciones y resultados calculados.
- Separar hechos, predicciones y recomendaciones cuando sea relevante.
- Un modelo estadístico o de machine learning no sustituye una regla determinista que pueda expresarse de forma más simple y estable.
- Los pipelines deben ser reproducibles.
- Evitar transformaciones implícitas difíciles de rastrear.
- Semillas, splits, ventanas temporales, métricas y configuración de evaluación deben quedar explícitos cuando afecten reproducibilidad.
- Nunca evaluar series temporales con particiones que filtren información del futuro.
- Checkpoints, datasets pesados, caches y artefactos reconstruibles permanecen fuera de Git salvo decisión explícita del proyecto.
- Los artefactos versionados deben tener propósito académico o de producto claro.

## APIs y contratos

Cuando un proyecto exponga HTTP u otra frontera externa:

- Mantener contratos explícitos y estables.
- Validar datos al entrar al sistema.
- No exponer directamente modelos internos como contrato por accidente.
- No inventar una forma distinta de respuesta en cada endpoint.
- Transformar errores de aplicación a errores de transporte en una frontera definida.
- Los mensajes públicos nunca exponen excepciones crudas, secretos, credenciales, queries internas ni detalles sensibles.
- Un cambio incompatible requiere diseño explícito, versión o estrategia de migración.
- Los identificadores de request sirven para correlación y soporte; no representan identidad ni autorización.

## Persistencia e integraciones

- La persistencia es una implementación interna del backend.
- Los consumidores externos no deben depender directamente del esquema físico.
- Framework HTTP, base de datos, autenticación, colas, concurrencia y servicios externos requieren una necesidad real antes de introducir complejidad.
- Las integraciones externas deben quedar detrás de fronteras claras.
- Los adapters traducen entre sistemas; no duplican reglas del dominio.
- Bases locales, archivos WAL, caches y artefactos de ejecución no se versionan cuando pueden reconstruirse.

## Seguridad

- La autorización pertenece a la frontera confiable y se valida en cada operación protegida.
- Un botón oculto, middleware visual, ruta bloqueada o estado de frontend no constituye autorización.
- Tokens, credenciales y secretos no se guardan en código, ejemplos versionados, local storage ni logs.
- Variables sensibles se documentan por nombre y propósito, nunca por valor real.
- Toda entrada externa es no confiable hasta validarse.
- No degradar controles de seguridad para simplificar una práctica académica si el mismo resultado puede lograrse correctamente.

## Frontend

Cuando exista frontend:

- El frontend es dueño de navegación, presentación, interacción y estado de interfaz.
- No define permisos, transiciones de dominio ni persistencia autoritativa.
- Consume contratos del backend en vez de reconstruir sus reglas.
- Antes de crear UI nueva, revisar componentes, primitives, composables, schemas y patrones existentes.
- Componer antes de copiar.
- No crear componentes genéricos que sólo añadan flags y complejidad.
- Modelar explícitamente loading, success, empty, error y recuperación cuando apliquen.
- Mantener accesibilidad, responsive y consistencia visual como parte de la corrección, no como decoración posterior.

## Errores

- Los errores propios del sistema representan fallos del dominio o de la aplicación, no textos improvisados en cada endpoint.
- Los adapters traducen errores externos hacia errores propios.
- La frontera HTTP o UI traduce errores propios a una representación segura y accionable.
- No capturar Exception indiscriminadamente para ocultar fallos.
- No representar errores mediante respuestas exitosas.
- No registrar secretos, tokens ni payloads sensibles.

## Verificación

Todo cambio de comportamiento requiere evidencia proporcional.

- Verificar rutas, imports y ejecución de la actividad afectada con sus datos reales o muestras pequeñas.
- Revisar los resultados y errores relevantes de forma proporcional al cambio.
- No agregar suites de tests al repositorio salvo nueva indicación de Fernando.

Comandos base desde la raíz:

~~~bash
uv lock --check
uv run ruff check .
uv build
~~~

Si un subproyecto incorpora frontend u otra toolchain, sus comandos de lint, typecheck y build se vuelven gates adicionales para cambios que lo afecten.

## Git

- main es la rama de integración.
- No trabajar directamente en main para cambios significativos.
- Usar ramas cortas y aisladas.
- Todo cambio relevante entra mediante pull request.
- Antes de presentar un PR como listo deben pasar las verificaciones y builds aplicables.
- No eliminar, omitir ni debilitar checks para conseguir verde.
- No integrar un cambio mientras su verificación requerida esté pendiente o fallando.
- Un commit intermedio es un punto de recuperación, no evidencia de verificación.
- Los agentes pueden preparar ramas, commits y pull requests; Fernando conserva la revisión final y decide el merge.
- Después del merge, eliminar la rama de trabajo cuando ya no tenga utilidad.

## Ciclo de desarrollo

El trabajo sigue:

**requerimientos → diseño → construcción → verificación → integración**

No comenzar una construcción relevante sin comprender primero el problema, las restricciones y la arquitectura existente.

Cuando durante implementación o pruebas aparezca información nueva, regresar a diseño o requerimientos si hace falta.

La arquitectura existe para reducir complejidad futura, no para demostrar complejidad presente.

---

# Reglas académicas locales

## Notas académicas

Las notas académicas se guardan en el vault de Obsidian traveler, no dentro de este repositorio.

Las materias nuevas se crean dentro de IBERO 🔴/SEMESTRE_7 7️⃣, con el nombre de carpeta en mayúsculas y palabras separadas por guiones bajos. Para robótica, usar la carpeta existente IBERO 🔴/SEMESTRE_7 7️⃣/TEMAS_SELECTOS_DE_ROBOTS_Y_AUTONOMIA.

Todas las notas académicas deben ser Markdown con extensión .md. Cada archivo cubre un tema principal y sigue la nomenclatura secuencial N-Título.md.

Evitar carpetas duplicadas para materias que ya existen. Escribir notas simples, cortas y mínimas: cada concepto debe tener una explicación breve y, cuando ayude, un ejemplo concreto.

No agregar secciones vacías, desarrollos extensos ni contenido adicional salvo que Fernando lo pida.

## Dinámica para tomar apuntes

Fernando puede enviar comentarios en bruto mientras toma la clase. Estructurarlos como apuntes claros y ordenados conservando su intención.

Corregir ortografía, términos y conceptos incorrectos; nutrirlos sólo con el contexto mínimo necesario. Si una afirmación es dudosa o ambigua, verificarla o marcarla como pendiente en vez de inventar.

Evitar explicaciones largas. La meta es apoyar los apuntes escolares sin convertirlos en un texto pesado.

## Documentos de referencia

Cuando Fernando pida añadir un documento como referencia, copiarlo dentro de la bóveda traveler y guardarlo en una carpeta REFERENCIAS dentro de la materia correspondiente, con un nombre descriptivo y seguro para Obsidian.

Conservar el archivo original en su ubicación de origen salvo que Fernando pida moverlo. Enlazar el documento desde la nota en curso mediante un wikilink.

No convertir ni resumir el documento completo salvo que Fernando lo solicite.

## Actividades

Guardar las actividades en una carpeta ACTIVIDADES dentro de la materia correspondiente.

Usar la nomenclatura AAAA-MM-DD - Tipo N - Título.md, conservando el tipo y número oficiales.

Antes de crear una actividad, comparar la fecha local de America/Mexico_City con la fecha indicada o inferida del documento. Si no coinciden, aclarar la discrepancia antes de fijar la fecha.

Todas las actividades usan la misma estructura: propósito, instrucciones generales, desarrollo y referencias.

Colocar modalidad, restricciones y esquema común de respuesta una sola vez al inicio. No repetirlos en cada pregunta.

Transcribir todos los reactivos únicos del documento original. Consolidar duplicados exactos y avisar a Fernando al entregar.
