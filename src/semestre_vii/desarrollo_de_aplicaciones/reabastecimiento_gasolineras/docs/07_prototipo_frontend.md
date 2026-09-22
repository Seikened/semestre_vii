# 07 · Prototipo visual frontend

Esta etapa representa **todas las vistas funcionales ya descritas en la documentación canónica** sin implementar backend, persistencia, autenticación real ni forecasting real.

## Principio

El prototipo reutiliza el lenguaje visual del Nuxt Dashboard Template y separa claramente los dos contextos del producto:

- **Administración:** revisión y supervisión de la operación.
- **Solicitud:** experiencia de una sucursal asociada a una cuenta.

El selector superior cambia únicamente el contexto visual y la navegación disponible.

## Vistas de administración

| Ruta | Propósito visual |
| --- | --- |
| `/operacion` | Resumen ejecutivo de estaciones, pedidos, demanda y desempeño. |
| `/pedidos` | Cola administrativa con lista, detalle, recomendación, solicitud y decisión humana. |
| `/estaciones` | Consulta de sucursales, responsables, cierres y señal de desempeño. |
| `/cuentas` | Asociación de cuentas, sucursales, roles, revocación y emisión de credenciales. |
| `/modelo` | Métricas, evolución, filtros por estación/producto/horizonte y comparación de candidatos. |

## Vistas de solicitud

| Ruta | Propósito visual |
| --- | --- |
| `/solicitud` | Portada de la sucursal y acceso a la operación semanal. |
| `/solicitud/semanal` | Vista única con tabs para Pedido y Cierre; comparte composición y cambia únicamente el acento visual y los datos de cada modo. |

## Vistas de acceso

| Ruta | Propósito visual |
| --- | --- |
| `/login` | Acceso remoto mediante credenciales. |
| `/recuperar-acceso` | Representación del flujo de recuperación de credenciales. |

## Decisiones deliberadas

- No existe autorización real.
- No existe API nueva.
- No existe persistencia.
- No se envían formularios.
- No se revocan cuentas.
- No se generan credenciales.
- No se calcula forecast.
- No se calcula confianza.
- Los controles pueden cambiar estado puramente visual, pero no producen efectos de dominio.
- Los valores mostrados son fixtures de demostración.

## Incertidumbre

La documentación todavía no define una fórmula única de confianza. Por ello el prototipo **no inventa un porcentaje de confianza**; muestra ese concepto como pendiente de definición.

## Campos pendientes

Los campos exactos de cierre y pedido aún deben confirmarse. Las vistas usan etiquetas provisionales y lo indican explícitamente para no convertir la maqueta en contrato accidental.

## Regla de evolución

Cuando exista backend, los mocks deben sustituirse en una frontera de datos clara. Las vistas no deben absorber autorización, reglas de negocio, persistencia o lógica del modelo.
