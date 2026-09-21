# 05 · Arquitectura

## Estado de la arquitectura

La arquitectura continúa en **definición**, pero el prototipo frontend ya tiene una decisión explícita: **Nuxt 4 + Nuxt UI**, partiendo del Nuxt Dashboard Template oficial. Backend, framework HTTP, persistencia, proveedor de identidad, colas e infraestructura siguen sin decidirse.

Las decisiones deben aparecer cuando exista un caso de uso que las justifique. No se adoptará una tecnología únicamente porque Sol u otro producto la utilice.

## Fronteras principales

```text
┌───────────────────────────────┐
│          FRONTEND             │
│ portal sucursal + admin       │
└───────────────┬───────────────┘
                │ contratos
                ▼
┌───────────────────────────────┐
│           BACKEND             │
│ dominio · pedidos · cuentas   │
│ autorización · persistencia   │
└───────┬─────────────────┬─────┘
        │                 │
        │ contrato        │ integración futura
        ▼                 ▼
┌───────────────┐   ┌───────────────┐
│  FORECASTING  │   │ SISTEMA       │
│ datos/modelos │   │ EXTERNO       │
│ backtesting   │   │ por definir   │
└───────┬───────┘   └───────────────┘
        │
        ▼
┌───────────────────────────────┐
│ DATOS / ARTEFACTOS DE MODELO  │
└───────────────────────────────┘
```

## Frontend

### Baseline de prototipo · 21 de septiembre de 2026

Para acelerar el maquetado se adopta Nuxt 4 con Nuxt UI y la estructura visual de `nuxt-ui-templates/dashboard`. Esta decisión autoriza el scaffold y la experiencia de esta iteración; no autoriza backend, endpoints Nitro ni reglas de dominio en el cliente.

La maqueta utiliza datos locales deterministas y se mantiene frontend-only hasta que exista un contrato backend aprobado. Ver [`07_maquetado_frontend.md`](./07_maquetado_frontend.md).

Responsable de:

- navegación;
- presentación;
- interacción;
- estado de interfaz;
- visualización de históricos, predicciones e incertidumbre;
- captura del pedido;
- experiencia administrativa.

No posee:

- autorización;
- reglas de negocio;
- persistencia autoritativa;
- lógica del modelo;
- estados de dominio duplicados.

## Backend

Responsable de:

- contratos;
- identidad y autorización cuando se definan;
- cuentas y relación con sucursales;
- ciclo de pedidos;
- reglas e invariantes;
- persistencia;
- integración con el motor predictivo;
- traducción segura de errores;
- integración futura con sistemas externos.

El backend no debe conocer detalles visuales.

## Motor predictivo

El forecasting se diseña como una capacidad sustituible detrás de una frontera estable.

La aplicación no debe depender de:

- una arquitectura de red concreta;
- una librería específica;
- formato privado de checkpoints;
- detalles de entrenamiento;
- proveedor de foundation model.

El motor recibe datos validados y produce forecasts con metadatos suficientes para trazabilidad.

## Datos y persistencia

Los datos de entrenamiento, backtests y predicciones tienen necesidades diferentes de la persistencia operativa de cuentas y pedidos.

No se asumirá que una sola base, tabla o tecnología debe resolver ambas áreas.

La estructura local actual separa:

```text
data/desarrollo_de_aplicaciones/reabastecimiento_gasolineras/
models/desarrollo_de_aplicaciones/reabastecimiento_gasolineras/
```

La persistencia operativa se decidirá cuando existan modelos de dominio y consultas reales.

## Contratos

Toda frontera debe ser explícita.

El contrato entre aplicación y forecasting debe distinguir al menos:

- estación;
- producto;
- fecha de corte;
- horizonte;
- predicción;
- incertidumbre cuando exista;
- versión de modelo;
- contexto suficiente para trazabilidad.

El contrato de pedidos deberá distinguir recomendación y decisión humana para conservar evidencia de adopción.

## Identidad y seguridad

La planeación requiere cuentas y recuperación de acceso.

Todavía no se ha elegido mecanismo de autenticación. Independientemente de la implementación:

- la autorización se valida en backend;
- secretos y tokens no viven en estado de interfaz;
- una cuenta de sucursal sólo puede actuar dentro de su ámbito autorizado;
- administración posee capacidades explícitas, no inferidas desde componentes visibles.

## Sistema externo

Existe la expectativa de una integración posterior con una plataforma mayor.

Hasta tener un contrato real:

- se trata como una frontera externa desconocida;
- no se inventan tablas ni endpoints;
- el dominio interno se mantiene independiente;
- cualquier adapter futuro traducirá entre ambos modelos.

## Estructura del producto

```text
src/semestre_vii/desarrollo_de_aplicaciones/reabastecimiento_gasolineras/
├── README.md
├── docs/
├── backend/
└── frontend/
```

Backend permanece vacío salvo sus reglas. Frontend contiene una maqueta Nuxt/Nuxt UI frontend-only basada en la template oficial; todavía no existe integración real.

## Decisiones que todavía no existen

No considerar aprobados por aparecer en conversaciones o ejemplos:

- FastAPI;
- Django;
- PostgreSQL;
- Redis;
- Celery;
- un proveedor de autenticación;
- arquitectura de microservicios;
- despliegue específico.

Cada decisión debe justificar su costo con una necesidad actual del producto.
