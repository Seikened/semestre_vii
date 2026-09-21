# 06 · Plan de trabajo

## Método

El trabajo se organiza de forma iterativa en **sprints de dos semanas** con objetivo funcional y resultado verificable.

No se denomina Scrum porque no están definidos todos sus roles, ceremonias y artefactos.

La selección del algoritmo y de la arquitectura debe basarse en evidencia y restricciones reales, no en preferencia previa por una tecnología.

## Distribución de esfuerzo

La planeación inicial asigna aproximadamente:

- **dos terceras partes** a datos, modelado, evaluación y mejora del forecasting;
- **una tercera parte** a autenticación, portales, integración, dashboard y demostración.

La aplicación puede avanzar en paralelo una vez que sus contratos de entrada y salida sean suficientemente estables.

## Cronograma

| Incremento | Fechas | Enfoque | Gate |
| --- | --- | --- | --- |
| Sprint 1 | 7–20 sep | Problema, cuatro alcances y estrategia de evaluación | Alcances, datos de entrada/salida y criterio de comparación establecidos. |
| Sprint 2 | 21 sep–4 oct | Histórico, baseline y acceso básico | Dataset utilizable, referencia inicial y flujo mínimo de autenticación. |
| Sprint 3 | 5–18 oct | Modelos candidatos y flujo inicial de pedidos | Comparación de modelos y alta básica de pedidos. |
| Sprint 4 | 19 oct–1 nov | Evaluación por sucursal y administración | Estrategias comparadas, cola de pedidos y gestión básica de cuentas. |
| Sprint 5 | 2–15 nov | Afinación, validación temporal e indicadores | Modelo candidato y KPIs definidos con limitaciones documentadas. |
| Sprint 6 | 16–29 nov | Integración de recomendación | Sugerencia, decisión del usuario y seguimiento administrativo integrados. |
| Sprint 7 | 30 nov–13 dic | Retroalimentación, dashboard y E2E | Indicadores visibles y flujo completo validado. |
| Cierre | 14–18 dic | Estabilización y demo | Demostración funcional, resultados y conclusiones. |

Las fechas de diciembre siguen sujetas a la fecha oficial de entrega.

## Entregables

- inventario de datos;
- reporte breve de calidad;
- histórico preparado;
- baseline;
- estrategia de evaluación;
- comparación de modelos;
- modelo candidato con métricas y limitaciones;
- acceso remoto y recuperación de credenciales;
- portal de sucursal;
- panel administrativo;
- cola de pedidos;
- gestión de cuentas;
- dashboard del modelo;
- trazabilidad de recomendación frente a decisión;
- ciclo de retroalimentación;
- pruebas de extremo a extremo;
- demostración final;
- conclusiones.

## Hitos

| Fecha | Hito |
| --- | --- |
| 20 sep | Alcance y datos identificados. |
| 4 oct | Baseline disponible. |
| 15 nov | Modelo candidato seleccionado. |
| 29 nov | Flujos principales integrados. |
| 13 dic | Pruebas E2E concluidas. |
| 18 dic | Demostración final propuesta. |

## Riesgos

| Riesgo | Tratamiento |
| --- | --- |
| Datos incompletos o inconsistentes | Auditar calidad antes de seleccionar modelo. |
| Desempeño menor al esperado | Comparar alternativas y documentar límites reales. |
| Diferencias fuertes entre sucursales | Evaluar modelo global, variables de estación y ajustes sólo si mejoran. |
| Falta de acceso al sistema mayor | Mantener arquitectura desacoplada hasta recibir contrato real. |
| Crecimiento de alcance | Mantener portales en el mínimo necesario para demostrar el ciclo. |
| Poco tiempo de integración | Definir contratos temprano y probar un recorrido mínimo antes del final. |
| Acceso no autorizado | Diseñar revocación, recuperación y autorización confiable. |
| Confianza mal comunicada | No inventar porcentajes; definir semántica a partir de evaluación estadística. |
| Leakage temporal | Backtesting temporal y validación de disponibilidad de covariables. |

## Presupuesto

Servicios, licencias, infraestructura y recursos de cómputo todavía no están definidos.

No se seleccionarán servicios pagados antes de conocer:

- volumen real de datos;
- frecuencia de entrenamiento;
- necesidades de serving;
- concurrencia;
- requisitos de disponibilidad;
- condiciones de la demostración.

## Criterios de verificación global

La entrega debe demostrar que:

- el histórico fue auditado antes de elegir modelo;
- el modelo se compara con un baseline estacional;
- las métricas se reportan globalmente y por sucursal;
- la plataforma distingue recomendación y pedido;
- cada pedido registra si la sugerencia fue aceptada, modificada o descartada;
- el panel puede revisar pedidos y desempeño;
- el resultado real puede cerrar el ciclo;
- la documentación registra limitaciones;
- la integración externa no se falsifica.

## Decisiones pendientes

Antes de cerrar diseño e implementación deben resolverse, con evidencia:

- campos del cierre semanal;
- campos del pedido;
- nomenclatura oficial de combustibles;
- utilidad real del precio;
- inventario y capacidad disponibles;
- estados del pedido;
- permisos por rol;
- mecanismo de autenticación y recuperación;
- fórmula de indicadores resumidos;
- semántica de incertidumbre/confianza;
- criterios de drift y reentrenamiento;
- contrato con el sistema externo;
- fecha oficial de entrega;
- infraestructura y presupuesto.

Una decisión pendiente no debe transformarse en implementación accidental.
