# Plan de proyecto: Pronóstico y reabastecimiento de gasolineras

**Estado:** pendiente de completar y revisar.

**Versión:**
**Fecha de adaptación:** 14 de octubre de 2026
**Elaboró:**
**Cliente:** distribuidora de combustible; nombre por confirmar.

Formato adaptado de `plan_proyecto.md` (LabPresta, M.I. Ricardo Medrano). Los campos vacíos corresponden a información aún no definida. Los módulos describen el alcance previsto; su estado actual se indica en 5.3.

## 1. Antecedentes

Una distribuidora atiende aproximadamente 120 gasolineras. Cada sucursal realiza un cierre semanal y envía información de ventas para solicitar combustible para la semana siguiente. Entre cinco y seis responsables atienden alrededor de veinte sucursales cada uno.

Se ha mencionado un histórico cercano a diez años de registros semanales. Su disponibilidad y calidad deben confirmarse mediante una auditoría.

## 2. Problemática

- La decisión de suministro no aprovecha sistemáticamente el histórico disponible.
- No existe una comparación continua entre pronóstico, pedido y resultado real.
- Sin evaluación por sucursal, un promedio general puede ocultar errores relevantes para la operación.

## 3. Objetivos

**Objetivo general:** desarrollar y validar antes de finalizar diciembre de 2026 una plataforma que pronostique ventas semanales por sucursal y producto, recomiende suministro y permita comparar la recomendación con el pedido y el resultado real.

| ID | Objetivo específico | Medición |
| --- | --- | --- |
| OE1 | Preparar un histórico semanal utilizable | Inventario de fuentes, reporte de calidad y tabla canónica reproducible. |
| OE2 | Evaluar un modelo frente a un baseline estacional | Backtesting temporal con MAE, RMSE, WAPE y bias, globalmente y por sucursal. |
| OE3 | Conectar cierre, recomendación y pedido | Recorrido verificable que conserve si la sugerencia fue aceptada, modificada o descartada. |
| OE4 | Facilitar revisión administrativa y evaluación continua | Consulta de pedidos y métricas; comparación posterior con el resultado real. |

La mejora de al menos 10 % respecto del baseline es una **meta inicial pendiente de confirmación** con los datos y el profesor.

## 4. Descripción de la solución

Plataforma web con tres responsabilidades principales:

- **Frontend:** portal de sucursal y panel administrativo. Existe un prototipo visual en Nuxt con datos de demostración.
- **Backend:** validación, cuentas, autorización, pedidos, persistencia e integración. Su implementación y tecnologías siguen pendientes.
- **Motor predictivo:** preparación de datos, forecasting, evaluación e incertidumbre. El modelo se seleccionará con evidencia.

El ciclo previsto es: cierre semanal, validación, pronóstico, recomendación, pedido, revisión administrativa y comparación con el resultado real. La integración con una plataforma externa depende de recibir su contrato.

## 5. Alcance de la entrega académica

### 5.1 Entidades

Los conceptos siguientes ya aparecen en el alcance. Sus campos operativos y relaciones aún no están definidos; las celdas vacías no representan un diseño de tablas aprobado.

| Concepto | Campos | Relaciones |
| --- | --- | --- |
| Sucursal | | |
| Cuenta | | |
| Cierre semanal | | |
| Pedido | | |
| Pronóstico y recomendación | | |

Para el histórico sí existe una estructura inicial: `week`, `station_id`, `product` y `liters`. La fuente debe confirmar la semántica de `liters` y la nomenclatura oficial de combustibles. Véase [Datos](03_datos.md).

### 5.2 Reglas de negocio

- **RN1.** La recomendación asiste la decisión humana; no aprueba pedidos automáticamente.
- **RN2.** La sucursal puede aceptar, modificar o descartar la sugerencia y capturar su pedido.
- **RN3.** Debe conservarse la relación entre recomendación, pedido, decisión humana y resultado real cuando esté disponible.
- **RN4.** Una cuenta de sucursal sólo puede actuar en su ámbito autorizado; el backend valida los permisos.
- **RN5.** La evaluación usa únicamente información disponible en el instante de predicción.
- **RN6.** La llegada de una semana nueva no implica reentrenar automáticamente. La sustitución del modelo requiere evidencia de mejora.

Los estados del pedido, permisos exactos y criterios de drift y promoción siguen sin definirse.

### 5.3 Módulos y entregables

Los primeros cuatro módulos corresponden a los alcances existentes. Infraestructura se conserva como apartado pendiente, como en la plantilla. Los criterios siguientes son objetivos de verificación, no resultados ya alcanzados.

| Módulo | Entregable | Criterio de aceptación |
| --- | --- | --- |
| M1 Autenticación y cuentas | Acceso remoto, recuperación, asociación cuenta/sucursal o rol y revocación | Acceso y recuperación verificables; autorización aplicada en backend según permisos previamente definidos. |
| M2 Panel de administración | Consulta de pedidos, sucursales, cuentas y desempeño del modelo | Se puede revisar el pedido, compararlo con su recomendación y consultar métricas generales y por sucursal. |
| M3 Portal de sucursal | Cierre semanal, recomendación, captura del pedido y registro posterior del resultado real | El recorrido conserva la decisión de aceptar, modificar o descartar la sugerencia y permite cerrar el ciclo. |
| M4 Modelo predictivo | Inventario y reporte de calidad, histórico preparado, baseline, protocolo de evaluación, comparación de candidatos y modelo con métricas y limitaciones | Comparación reproducible mediante backtesting temporal; métricas por estación, producto y horizonte; incertidumbre comunicada con una semántica definida. |
| M5 Infraestructura | | |

**Estado actual comprobado en el repositorio:**

| Módulo | Disponible | Falta |
| --- | --- | --- |
| M1 | Vistas de acceso, recuperación y cuentas | Autenticación, autorización, recuperación y gestión real de credenciales. |
| M2 | Vistas de operación, pedidos, estaciones, cuentas y modelo con fixtures | Backend, consultas reales, persistencia y seguimiento operativo. |
| M3 | Portada de sucursal y vista semanal con Pedido y Cierre | Validación y envío reales, guardado del cierre y pedido, vínculo con recomendación y resultado observado. |
| M4 | Documentación de datos, modelos y evaluación | Pipeline, histórico validado, baseline, comparación, modelo y métricas integrados en este proyecto. |
| M5 | | Definición de infraestructura y presupuesto. |

El directorio `backend/` contiene únicamente su `AGENTS.md`. Las vistas son un prototipo y no acreditan funciones de dominio implementadas. Véase [Prototipo visual frontend](07_prototipo_frontend.md).

### 5.4 Pantallas (prototipo)

| Área | Ruta | Propósito |
| --- | --- | --- |
| Acceso | `/login` | Inicio de sesión. |
| Acceso | `/recuperar-acceso` | Recuperación de credenciales. |
| Administración | `/operacion` | Resumen de operación y desempeño. |
| Administración | `/pedidos` | Cola y detalle de pedidos. |
| Administración | `/estaciones` | Consulta de sucursales. |
| Administración | `/cuentas` | Cuentas, roles y asociación con sucursales. |
| Administración | `/modelo` | Métricas y comparación de candidatos. |
| Sucursal | `/solicitud` | Portada de la sucursal. |
| Sucursal | `/solicitud/semanal` | Pedido y Cierre en una misma vista. |

## 6. Indicadores de éxito

- Histórico auditado y preparación reproducible antes de elegir un modelo.
- Comparación contra un baseline estacional bajo el mismo protocolo temporal.
- Métricas globales y por sucursal, producto y horizonte, con limitaciones documentadas.
- Recorrido completo desde el cierre hasta la revisión administrativa y el resultado real.
- Trazabilidad entre sugerencia y decisión humana.
- Demostración final y conclusiones sustentadas en resultados revisables.

La verificación académica se realiza mediante ejecución real y revisión de resultados. El repositorio no mantiene suites de tests. La integración externa sólo se demostrará si existe un contrato real.

## 7. Componente de IA

Forecasting de ventas semanales por sucursal y producto, con prioridad en la semana siguiente. El modelo seleccionado y su tecnología quedan vacíos hasta completar la evaluación.

| Elemento | Definición |
| --- | --- |
| Unidad de observación | Semana, estación y producto. |
| Variable objetivo | `liters`, con significado por confirmar con la fuente. |
| Baseline | Seasonal Naive; referencias adicionales si aportan valor. |
| Evaluación | Rolling-origin backtesting, sin particiones aleatorias ni información futura. |
| Métricas | MAE, RMSE, WAPE y bias; cobertura y calibración cuando existan intervalos. |
| Modelo seleccionado | |
| Librería de modelado | |
| Semántica de incertidumbre/confianza | |
| Criterios de drift y reentrenamiento | |

Los candidatos y horizontes adicionales se conservan en [Modelos y evaluación](04_modelos_y_evaluacion.md). Actualizar datos y actualizar pesos son decisiones distintas.

## 8. Exclusiones de la entrega académica

- Desarrollar la plataforma completa de la distribuidora.
- Modificar internamente un sistema externo al que el equipo no tiene acceso.
- Operar indefinidamente el sistema después de la entrega.
- Aprobar pedidos automáticamente.

Autenticación, cuentas y forecasting sí forman parte del alcance de este proyecto, aunque la plantilla LabPresta excluya autenticación y no implemente IA en su primera fase.

## 9. Stack tecnológico

Las tecnologías registradas describen el repositorio actual. Las celdas vacías corresponden a decisiones pendientes para la aplicación integrada.

| Capa | Tecnología |
| --- | --- |
| Prototipo frontend | Nuxt 4, Vue 3, Nuxt UI 4, Tailwind CSS 4 y TypeScript. |
| Gestión de dependencias frontend | pnpm. |
| Lenguaje y entorno Python del repositorio | Python y uv. |
| Framework backend | |
| Persistencia y migraciones | |
| Autenticación | |
| Librería de forecasting | |
| Verificación Python del repositorio | Ruff, build y ejecución de las actividades. |
| Verificación frontend disponible | Scripts `lint`, `typecheck` y `build` de `frontend/package.json`. |
| Contenedores | |
| Control de versiones | Git. |
| Asistente de desarrollo | |

FastAPI, PostgreSQL, Alembic y Docker Compose pertenecen al ejemplo descargado; no se adoptan por copiar su formato.

## 10. Infraestructura

| Recurso | Definición |
| --- | --- |
| Entorno de demostración | |
| Hosting del frontend y backend | |
| Base de datos | |
| Cómputo para entrenamiento e inferencia | |
| Despliegue y puertos | |
| Dominio y acceso remoto | |

## 11. Equipo y estimación

| Rol | Responsable | Esfuerzo |
| --- | --- | --- |
| | | |

La distribución inicial de esfuerzo es de aproximadamente dos terceras partes para datos, modelado y evaluación, y una tercera parte para acceso, portales, integración, dashboard y demostración. No se han asignado responsables ni horas.

| Concepto de presupuesto | Estimación |
| --- | --- |
| Servicios y licencias | |
| Infraestructura | |
| Recursos de cómputo | |

Antes de contratar servicios se deben conocer el volumen de datos, frecuencia de entrenamiento, necesidades de serving, concurrencia, disponibilidad y condiciones de la demo.

## 12. Cronograma

Se conserva la planeación inicial de 2026. **Las fechas expresan objetivos previstos y no acreditan avances concluidos.** La fecha oficial de entrega sigue pendiente de confirmación.

### Método de trabajo

Trabajo iterativo en sprints de dos semanas, cada uno con objetivo funcional y resultado verificable. No se denomina Scrum porque no están definidos todos sus roles, ceremonias y artefactos.

Se sigue el ciclo del repositorio: requerimientos, diseño, construcción, verificación e integración. La selección de algoritmos y arquitectura se basa en evidencia. La aplicación puede avanzar en paralelo cuando los contratos sean suficientemente estables.

| Incremento | Fechas | Enfoque | Gate |
| --- | --- | --- | --- |
| Sprint 1 | 7 al 20 sep | Problema, cuatro alcances y estrategia de evaluación | Alcances, datos de entrada/salida y criterio de comparación establecidos. |
| Sprint 2 | 21 sep al 4 oct | Histórico, baseline y acceso básico | Dataset utilizable, referencia inicial y flujo mínimo de autenticación. |
| Sprint 3 | 5 al 18 oct | Modelos candidatos y flujo inicial de pedidos | Comparación de modelos y alta básica de pedidos. |
| Sprint 4 | 19 oct al 1 nov | Evaluación por sucursal y administración | Estrategias comparadas, cola de pedidos y gestión básica de cuentas. |
| Sprint 5 | 2 al 15 nov | Afinación, validación temporal e indicadores | Modelo candidato y KPIs definidos con limitaciones documentadas. |
| Sprint 6 | 16 al 29 nov | Integración de recomendación | Sugerencia, decisión del usuario y seguimiento administrativo integrados. |
| Sprint 7 | 30 nov al 13 dic | Retroalimentación, dashboard y E2E | Indicadores visibles y flujo completo validado. |
| Cierre | 14 al 18 dic | Estabilización y demo | Demostración funcional, resultados y conclusiones. |

### Hitos previstos

| Fecha | Hito |
| --- | --- |
| 20 sep | Alcance y datos identificados. |
| 4 oct | Baseline disponible. |
| 15 nov | Modelo candidato seleccionado. |
| 29 nov | Flujos principales integrados. |
| 13 dic | Verificación E2E concluida. |
| 18 dic | Demostración final propuesta. |

## 13. Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Datos incompletos o inconsistentes | Auditar calidad antes de seleccionar modelo. |
| Desempeño menor al esperado | Comparar alternativas y documentar límites reales. |
| Diferencias fuertes entre sucursales | Evaluar modelo global, variables de estación y ajustes sólo si mejoran. |
| Falta de acceso al sistema mayor | Mantener arquitectura desacoplada hasta recibir contrato real. |
| Crecimiento de alcance | Mantener portales en el mínimo necesario para demostrar el ciclo. |
| Poco tiempo de integración | Definir contratos temprano y verificar un recorrido mínimo antes del final. |
| Acceso no autorizado | Diseñar revocación, recuperación y autorización confiable. |
| Confianza mal comunicada | Definir semántica estadística antes de presentar porcentajes. |
| Leakage temporal | Backtesting temporal y validación de disponibilidad de covariables. |

## 14. Supuestos

- La cifra de referencia es de 120 gasolineras.
- Existe histórico semanal; su cantidad utilizable aún debe validarse.
- Las sucursales capturan cierres y la distribuidora revisa los pedidos.
- Cada cuenta de sucursal estará asociada con una gasolinera.
- La recomendación asiste la decisión humana.
- La integración con una plataforma mayor se define al recibir interfaces reales.

Además de los campos vacíos, siguen pendientes: campos del cierre y pedido, nombres oficiales de combustibles, utilidad del precio, inventario y capacidad disponibles, estados del pedido, permisos, recuperación, fórmula de indicadores, incertidumbre, drift, reentrenamiento y contrato externo.

## Correspondencia con la plantilla descargada

Se conservaron los 14 apartados y los subapartados 5.1 a 5.4. La información del ejemplo LabPresta se sustituyó por el alcance documentado de gasolineras.

| Módulo del ejemplo | Correspondencia en gasolineras |
| --- | --- |
| M1 Catálogo de equipo | Consulta de sucursales dentro de M2; sin alta/baja de equipo de laboratorio. |
| M2 Solicitantes | Cuentas asociadas a sucursales en M1 y M2. |
| M3 Préstamos | Captura de pedidos en M3. |
| M4 Préstamos activos y devolución | Revisión de pedidos en M2 y registro del resultado real en M3. |
| M5 Infraestructura | M5, con entregable y aceptación vacíos. |

Las correspondencias son funcionales, no equivalencias de entidades o reglas. Autenticación y recuperación (M1), cierre semanal (M3), forecasting, evaluación e incertidumbre (M4) son necesidades de gasolineras que el ejemplo no desarrolla.

**Quedó vacío:** versión, autoría, campos y relaciones de entidades, entregable y aceptación de infraestructura, modelo y librería seleccionados, semántica de confianza, criterios de drift/reentrenamiento, tecnologías pendientes, infraestructura, integrantes, horas y montos del presupuesto.

Fuentes del contenido: [Producto y alcance](01_producto_y_alcance.md), [Operación y flujos](02_operacion_y_flujos.md), [Datos](03_datos.md), [Modelos y evaluación](04_modelos_y_evaluacion.md), [Arquitectura](05_arquitectura.md) y [Prototipo frontend](07_prototipo_frontend.md).
