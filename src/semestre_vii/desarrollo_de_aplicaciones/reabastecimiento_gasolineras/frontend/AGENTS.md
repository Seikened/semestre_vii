# AGENTS.md — Reabastecimiento de Gasolineras · Frontend

Estas reglas complementan el AGENTS.md de la raíz y gobiernan únicamente este directorio.

El frontend de Reabastecimiento de Gasolineras adopta la filosofía de ingeniería y experiencia de Sol, adaptada al sistema predictivo de abastecimiento de gasolineras. Se reutilizan principios, no identidad de producto ni código visual específico de Sol.

## Fuentes obligatorias

Antes de modificar frontend, leer:

1. ../../../../../AGENTS.md
2. ../README.md
3. ../docs/README.md
4. ../docs/01_producto_y_alcance.md
5. ../docs/02_operacion_y_flujos.md
6. ../docs/03_datos.md
7. ../docs/04_modelos_y_evaluacion.md
8. ../docs/05_arquitectura.md
9. ../docs/06_plan_de_trabajo.md

Cuando aparezca documentación local de arquitectura, diseño, accesibilidad, contratos o identidad, leerla antes de implementar cambios relacionados.

## Límite del área

- Frontend posee navegación, presentación, interacción, estado de interfaz y, si se adopta, el BFF del navegador.
- No define permisos, reglas de forecasting, transiciones de dominio ni persistencia autoritativa.
- No modificar ../backend por conveniencia.
- Si una capacidad necesita backend, definir o documentar el contrato requerido.
- No replicar reglas de dominio en componentes, local storage o helpers de UI.
- Si backend todavía no expone una capacidad, usar adapters de demostración sólo cuando el alcance lo justifique y dejar explícita su naturaleza temporal.

## Arquitectura de interfaz

- Separar componentes visuales, composición de páginas, acceso a datos y lógica de interacción.
- Mantener componentes pequeños y cohesionados.
- Componer antes de copiar.
- No crear wrappers genéricos que sólo añadan flags.
- No introducir un store global para estado que puede permanecer local.
- Una abstracción cliente debe existir porque reduce duplicación o protege un contrato, no por simetría.
- Validar los datos externos en la frontera antes de distribuirlos por la aplicación.
- No mantener tipos manuales paralelos a un schema validado sin una razón concreta.

## Estado

Elegir la ubicación del estado por propiedad y ciclo de vida.

- Estado efímero de un componente: local.
- Estado derivado: computado, no duplicado.
- Estado compartido de una feature: composable o store sólo cuando aporte valor real.
- Estado del servidor: usar las primitives de fetching y cache del framework antes de copiarlo a un store.
- Estado persistente del dominio: pertenece al backend.
- No usar local storage o session storage como base de datos de la aplicación.

Si se adopta Nuxt/Vue como en Sol, preferir useFetch, useAsyncData, useState, composables y estado local antes de Pinia. Pinia se introduce cuando exista estado cliente complejo y realmente compartido.

## Seguridad e identidad

Si el proyecto incorpora identidad:

- No exponer access tokens, refresh tokens, secretos, credenciales de proveedores o material CSRF al estado de UI.
- Validar la sesión en una frontera confiable antes de solicitar recursos protegidos.
- Proteger mutaciones del BFF contra CSRF cuando corresponda.
- Limpiar estado y caches asociados a la persona al cerrar, expirar o cambiar de sesión.
- Un middleware, modal, ruta escondida o botón deshabilitado no constituye autorización.
- Backend valida cada acceso protegido.

No implementar un sistema de identidad antes de que el producto lo requiera.

## Contratos

- Consumir el contrato del backend; no reconstruir reglas con strings mágicos.
- Validar respuestas externas en una frontera única.
- No repartir parsing defensivo por componentes.
- Mantener diferenciados errores de validación, autorización, conflicto, red e infraestructura cuando el contrato lo permita.
- request_id, si existe, sirve para soporte y trazabilidad; no controla concurrencia de UI.
- Una vista que descarte una respuesta obsoleta conserva su propia identidad local de operación.

## Reutilización y sistema visual

- Revisar componentes, composables, primitives y schemas existentes antes de crear nuevos.
- Cuando exista una librería de componentes adoptada por el proyecto, usarla antes de crear primitives propias.
- Mantener tokens globales en un único sistema, no repetir colores, spacing o tipografía en cada componente.
- No copiar interfaces completas de Sol u otros productos. Recuperar principios, flujos neutrales al dominio y aprendizajes de UX.
- La identidad visual del producto debe surgir de sus propias necesidades.
- No mezclar decisiones de producto con detalles accidentales de una demo.

## Datos predictivos en UI

El frontend debe distinguir claramente:

- datos históricos,
- predicciones,
- intervalos o incertidumbre,
- escenarios de planeación,
- recomendaciones derivadas.

No presentar una predicción como hecho observado.

No ocultar incertidumbre relevante por simplificar la gráfica.

No permitir que una visualización sugiera precisión mayor a la que soporta el modelo.

Un cambio de horizonte, producto, estación o escenario debe actualizar explícitamente el contexto visible.

## Estados de experiencia

Toda capacidad asíncrona debe considerar, cuando apliquen:

- carga,
- éxito,
- vacío,
- actualización,
- error,
- reintento,
- estado parcial,
- datos obsoletos.

No usar spinners eternos como manejo genérico de incertidumbre.

Conservar información válida cuando un refresh falle, siempre que el contrato permita identificarla como anterior o parcial.

## Heurísticas de Nielsen

Todo cambio de interacción se diseña y revisa con estas heurísticas:

1. **Visibilidad del estado del sistema:** mostrar carga, progreso, éxito, vacío, actualización, fallo y recuperación con feedback oportuno.
2. **Relación con el mundo real:** usar vocabulario de operación y planeación de combustible; no exponer nombres internos, tablas o detalles de infraestructura.
3. **Control y libertad:** ofrecer volver, cancelar, cerrar, corregir o recuperar cuando el dominio lo permita.
4. **Consistencia y estándares:** la misma intención se representa y comporta igual entre pantallas.
5. **Prevención de errores:** restringir combinaciones inválidas antes del envío y usar defaults seguros.
6. **Reconocer antes que recordar:** mantener visibles opciones, labels, contexto, unidades y siguientes acciones.
7. **Flexibilidad y eficiencia:** mantener un recorrido claro y añadir aceleradores sólo cuando aporten valor real.
8. **Diseño estético y minimalista:** mostrar sólo información y acciones relevantes para la tarea actual.
9. **Diagnóstico y recuperación:** explicar qué ocurrió, dónde corregir y qué opciones existen.
10. **Ayuda y documentación:** hacer que la interfaz se explique por sí misma y añadir ayuda contextual breve cuando haga falta.

## Accesibilidad

- Usar HTML semántico.
- Mantener navegación por teclado.
- No depender sólo de color para transmitir estado.
- Asociar labels y mensajes de error con sus controles.
- Respetar reduced motion cuando exista animación no esencial.
- Mantener contraste suficiente.
- Las gráficas deben tener contexto textual, unidades y una alternativa comprensible para información crítica.

## Responsive

- Diseñar para contenidos reales, no sólo para una captura de escritorio.
- Evitar layouts que dependan de anchuras mágicas.
- Tablas densas deben tener una estrategia explícita para pantallas pequeñas.
- Priorizar contenido y progressive disclosure antes que reducir todo hasta volverlo ilegible.

## Errores

- Traducir errores técnicos a lenguaje útil sin inventar causas.
- No mostrar stack traces, tokens, payloads internos ni mensajes crudos del proveedor.
- Conservar inputs válidos después de un fallo cuando sea seguro.
- Diferenciar error recuperable de error terminal cuando el contrato lo permita.
- No ocultar fallos silenciosamente.

## Tests

Ubicar cada prueba junto al nivel de comportamiento que demuestra.

- Unit tests para utilidades, formatters, composables y lógica determinista.
- Component tests para estados visibles, eventos, formularios y errores.
- Integration tests para contratos con la capa de datos.
- E2E para recorridos críticos una vez exista una aplicación navegable.
- No usar mocks que reimplementen exactamente la lógica bajo prueba.

Cuando se cree el scaffold del frontend, su package manager y package.json deben convertirse en la fuente de verdad de los comandos. El gate esperado debe cubrir como mínimo test, lint, typecheck y build cuando esas capacidades existan.

No inventar comandos antes de que exista la toolchain.

## Git y alcance

- Un PR frontend no debe incluir backend salvo cambio transversal explícito.
- Si falta una capacidad de backend, documentar la dependencia en vez de falsificar autoridad en el cliente.
- Antes de cerrar un cambio visual, revisar sus estados de carga, éxito, vacío y error.
- Un PR significativo debe indicar cómo se verificó el comportamiento y qué estados fueron probados.
- Fernando conserva la decisión final de merge.
