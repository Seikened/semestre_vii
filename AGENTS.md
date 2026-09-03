# AGENTS.md — Semestre VII

Este documento define la forma de trabajo del repositorio de semestre VII. Su enfoque principal es **backend, datos, lógica de dominio y procesamiento**, manteniendo frontend como una capa separada que sólo se modifica cuando la capacidad lo requiere explícitamente.

La prioridad es construir software **mínimo, explícito, verificable, cohesionado y mantenible**. DRY, SOLID, orientación a objetos y arquitecturas sofisticadas son herramientas, no objetivos.

## 1. Antes de modificar el sistema

Antes de diseñar o implementar un cambio, entender primero el comportamiento existente y revisar las implementaciones relacionadas.

Antes de crear un modelo, DTO, servicio, adapter, utilidad, pipeline, componente o abstracción, comprobar si ya existe una pieza que resuelva total o parcialmente el problema.

Una implementación nueva debe tener una diferencia funcional o arquitectónica concreta respecto a las existentes. No mantener dos fuentes de verdad para la misma regla.

## 2. Responsabilidad del backend

El backend es la **fuente autoritativa** para lógica de dominio, contratos, permisos, estados, persistencia, procesamiento de datos e integraciones confiables.

Expone capacidades al frontend, agentes u otros consumidores mediante contratos definidos. La presentación, interacción visual y estado puramente de interfaz no pertenecen al backend.

Frontend y backend nunca deben comunicarse accediendo directamente a la persistencia, archivos privados o estado interno del otro.

Cuando una funcionalidad atraviese ambas áreas, debe existir un contrato explícito y cada lado debe conservar sus responsabilidades. Una limitación del frontend nunca justifica duplicar reglas de dominio fuera del backend.

## 3. Diseño y modelado

Preferir estructuras simples y directas.

Una clase requiere una razón concreta relacionada con estado, invariantes o ciclo de vida. La herencia sólo se utiliza cuando existe una relación real de sustitución.

No crear servicios, repositories, managers, wrappers o capas únicamente para que la arquitectura parezca simétrica.

Los datos que cruzan fronteras deben poseer una representación explícita y validada. Usar tipado donde proteja contratos, persistencia, APIs, modelos de datos o comunicación entre módulos, evitando tipos ceremoniales en código interno cuya intención ya sea evidente.

Los modelos internos no deben convertirse accidentalmente en contratos públicos. Un dato externo se valida al ingresar al sistema y, a partir de ahí, se trabaja con representaciones confiables.

## 4. Python

Python es el lenguaje principal del backend.

Las dependencias y entornos se administran con **`uv`**.

Todo código Python debe seguir una filosofía `clean-python`: legibilidad primero, responsabilidades claras, nombres descriptivos y ausencia de complejidad accidental.

No utilizar `__all__` salvo que el proyecto llegue a convertirse explícitamente en una librería pública.

No utilizar diccionarios anónimos para representar información estructurada que cruce fronteras importantes del sistema. Preferir modelos o DTO explícitos para entradas, salidas, persistencia y contratos.

## 5. APIs y contratos

Las respuestas HTTP deben mantener una única estructura compartida. Los endpoints no inventan formas particulares de éxito o error.

Cuando exista un contrato Pydantic aprobado, ése es la fuente de verdad para la representación enviada por el backend. Los datos exitosos deben utilizar DTO explícitos y no diccionarios anónimos.

Los errores de aplicación deben transformarse en errores HTTP en una frontera definida. La lógica de dominio no debe conocer detalles innecesarios del framework HTTP.

Los códigos de error deben provenir de un catálogo controlado. Los mensajes públicos nunca deben revelar excepciones crudas, secretos, credenciales, consultas internas ni información sensible.

Los identificadores de request sirven para **correlación, observabilidad y soporte**. No representan identidad, autorización ni control de concurrencia.

Un cambio incompatible en un contrato requiere diseño explícito, versionamiento o estrategia de migración.

## 6. Persistencia e integraciones

La base de datos es responsabilidad del backend y los consumidores externos nunca deben depender directamente de su estructura interna.

Cambios importantes en base de datos, autenticación, concurrencia, colas, framework HTTP o infraestructura requieren una necesidad real antes de introducir complejidad adicional.

Las integraciones externas deben quedar detrás de fronteras claras para evitar que detalles del proveedor contaminen la lógica de dominio. Los adapters traducen entre sistemas; no deben convertirse en una segunda implementación de las reglas del negocio.

Las bases de datos locales, archivos WAL y artefactos de ejecución no se versionan cuando pueden reconstruirse desde el código o la fuente de datos.

## 7. Datos, minería y procesamiento

Los datos originales deben distinguirse de los datos derivados.

Transformaciones, limpieza, normalización, feature engineering, inferencias, predicciones y resultados calculados deben mantener una procedencia comprensible.

Cuando sea relevante, separar claramente **hechos, predicciones y recomendaciones**.

Un modelo estadístico o de machine learning no sustituye automáticamente una regla determinista cuando ésta puede expresarse de forma más simple, verificable y estable.

Los pipelines deben ser reproducibles y sus etapas deben poseer responsabilidades claras. Evitar transformaciones implícitas difíciles de rastrear.

Cuando una decisión dependa de datos procesados, debe ser posible identificar suficientemente qué entrada y qué proceso produjeron el resultado.

## 8. Errores

Los errores propios del sistema deben estar centralizados conceptualmente y representar fallos del dominio o de la aplicación, no mensajes improvisados por cada endpoint.

Los adapters pueden traducir errores externos hacia errores propios. Los endpoints transforman los errores propios hacia el contrato HTTP correspondiente.

No capturar excepciones indiscriminadamente para ocultar fallos ni utilizar respuestas exitosas para representar errores.

## 9. Seguridad e identidad

La autorización pertenece al backend y debe validarse en cada operación protegida.

Un botón oculto, middleware visual, ruta bloqueada o estado de frontend **no constituye autorización**.

Si existe frontend, access tokens, refresh tokens, credenciales de proveedores y material de seguridad no deben exponerse innecesariamente al estado Vue, Pinia, local storage o session storage.

Cuando exista un BFF, éste debe validar correctamente sesión y seguridad antes de acceder a recursos protegidos. El cierre, expiración o cambio de sesión debe eliminar el estado asociado cuando corresponda.

## 10. Frontend cuando sea necesario

El frontend sólo se modifica cuando el alcance de la tarea lo requiera.

Es responsable de navegación, presentación, interacción, estado de interfaz y BFF del navegador. No puede definir permisos, transiciones de dominio ni persistencia autoritativa.

Debe consumir los contratos proporcionados por backend en lugar de reconstruir las reglas.

Antes de crear UI nueva se reutilizan primero las primitivas y componentes existentes. La implementación visual debe mantener la identidad y patrones del proyecto en lugar de copiar interfaces completas provenientes de otros sistemas.

Cuando un cambio requiera frontend y backend, ambos lados se verifican independientemente y además se prueba el flujo integrado.

## 11. Pruebas y verificación

Todo cambio de comportamiento requiere evidencia proporcional.

Las reglas de negocio, validadores, transformaciones y transiciones se prueban unitariamente. Los contratos deben probarse cuando una capacidad atraviese HTTP. Las integraciones deben probarse cuando una capacidad atraviese persistencia o servicios externos.

Los recorridos críticos deben probarse como flujo desde su entrada hasta un efecto observable, cubriendo el camino exitoso, errores relevantes, permisos cuando existan y casos frontera importantes.

No simular la propia regla que se intenta probar ni reducir assertions, eliminar pruebas o debilitar validaciones únicamente para obtener una suite verde.

Backend:

```bash
uv lock --check
uv run pytest
uv build
```

Si el cambio alcanza frontend, ejecutar además sus pruebas, lint, typecheck y build aplicables.

## 12. Git

`master` es la rama de integración del repositorio. Para trabajo significativo, preferir una rama corta y aislada y revisar el cambio antes de integrarlo.

Antes de considerar un cambio terminado deben pasar las pruebas, validaciones y builds aplicables.

No eliminar, omitir ni debilitar verificaciones para conseguir un resultado verde.

No promover un cambio defectuoso únicamente porque compile o porque el flujo feliz funcione.

## 13. Ciclo de desarrollo

El trabajo sigue conceptualmente:

**requerimientos → diseño → construcción → verificación → integración**

No comenzar construcción relevante sin comprender primero qué debe resolver el sistema. No considerar verificado un cambio sin evidencia.

Cuando durante implementación o pruebas aparezca nueva información, regresar a diseño o requerimientos si es necesario.

## 14. Regla de decisión

Ante dos soluciones funcionalmente equivalentes, elegir la que tenga **menos estado, menos duplicación, menos abstracciones, contratos más claros, comportamiento más explícito y pruebas más sencillas**.

La arquitectura existe para reducir complejidad futura, no para demostrar complejidad presente.

---

# Reglas académicas locales

## Notas académicas

Las notas académicas se guardan en el vault de Obsidian `traveler`, no dentro de este repositorio.

Las materias nuevas se crean dentro de `IBERO 🔴/SEMESTRE_7 7️⃣`, con el nombre de carpeta en mayúsculas y palabras separadas por guiones bajos. Para robótica, usar la carpeta existente `IBERO 🔴/SEMESTRE_7 7️⃣/TEMAS_SELECTOS_DE_ROBOTS_Y_AUTONOMIA`.

Todas las notas académicas deben ser Markdown con extensión `.md`. Cada archivo cubre un tema principal y sigue la nomenclatura secuencial `N-Título.md`.

Evitar carpetas duplicadas para materias que ya existen. Escribir notas simples, cortas y mínimas: cada concepto debe tener una explicación breve y, cuando ayude, un ejemplo concreto.

No agregar secciones vacías, desarrollos extensos ni contenido adicional salvo que Fernando lo pida.

## Dinámica para tomar apuntes

Fernando puede enviar comentarios en bruto mientras toma la clase. Estructurarlos como apuntes claros y ordenados conservando su intención.

Corregir ortografía, términos y conceptos incorrectos; nutrirlos sólo con el contexto mínimo necesario. Si una afirmación es dudosa o ambigua, verificarla o marcarla como pendiente en vez de inventar.

Evitar explicaciones largas. La meta es apoyar los apuntes escolares sin convertirlos en un texto pesado.

## Documentos de referencia

Cuando Fernando pida añadir un documento como referencia, copiarlo dentro de la bóveda `traveler` y guardarlo en una carpeta `REFERENCIAS` dentro de la materia correspondiente, con un nombre descriptivo y seguro para Obsidian.

Conservar el archivo original en su ubicación de origen salvo que Fernando pida moverlo. Enlazar el documento desde la nota en curso mediante un wikilink `[[archivo|título visible]]`.

No convertir ni resumir el documento completo salvo que Fernando lo solicite.

## Actividades

Guardar las actividades en una carpeta `ACTIVIDADES` dentro de la materia correspondiente.

Usar la nomenclatura `AAAA-MM-DD - Tipo N - Título.md`, conservando el tipo y número oficiales, por ejemplo `Evidencia 2`.

Antes de crear una actividad, comparar la fecha local de `America/Mexico_City` con la fecha indicada o inferida del documento. Si no coinciden, preguntar cuál fecha debe usarse.

Todas las actividades usan la misma estructura: propósito, instrucciones generales, desarrollo y referencias.

Colocar modalidad, restricciones y esquema común de respuesta una sola vez al inicio. No repetirlos en cada pregunta.

Transcribir todos los reactivos únicos del documento original. Consolidar duplicados exactos y avisar a Fernando al entregar.
