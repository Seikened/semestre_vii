# 07 · Maquetado frontend

## Objetivo

Construir una maqueta navegable y visual del sistema antes de implementar backend, autenticación, persistencia o forecasting real.

La meta de esta iteración no es demostrar lógica de negocio. Es validar rápidamente:

- jerarquía de información;
- navegación;
- densidad del dashboard;
- representación de pedidos;
- representación de estaciones;
- forma de comunicar resultados del modelo;
- separación visual entre datos observados, pronósticos y decisiones humanas.

## Base de interfaz

La maqueta parte del proyecto oficial **Nuxt Dashboard Template**:

```text
https://github.com/nuxt-ui-templates/dashboard
https://dashboard-template.nuxt.dev/
```

Snapshot de referencia utilizado:

```text
nuxt-ui-templates/dashboard
main @ 8915adfc5139823d65a816792ce365842497c7d1
```

La plantilla se distribuye bajo licencia MIT. El frontend conserva el aviso de licencia en `LICENSE.nuxt-dashboard`.

Se reutiliza la gramática de la plantilla, no su dominio de ejemplo:

- sidebar colapsable;
- búsqueda de navegación;
- `UDashboardPanel`;
- `UDashboardNavbar`;
- cards de indicadores;
- tablas;
- visualización con Unovis;
- light/dark mode;
- Nuxt UI como sistema visual.

## Alcance de la maqueta

La primera navegación contiene cuatro vistas.

### Resumen `/`

Vista ejecutiva con indicadores rápidos, comparación real vs. pronóstico, pedidos recientes y acceso al resto de la maqueta.

### Pedidos `/pedidos`

Tabla basada conceptualmente en la vista `Customers` de la template. Muestra estación, semana, producto, recomendación, solicitud, forma de captura y estado. Los filtros son locales.

### Estaciones `/estaciones`

Tabla reducida para representar una red cercana a 120 estaciones: ID, región, responsable, último cierre, WAPE de ejemplo y señal de seguimiento.

### Modelo `/modelo`

Vista conceptual del motor predictivo con gráfico real vs. pronóstico, baseline, candidatos y estado de evaluación.

## Datos de maqueta

Todos los valores se encuentran en código frontend como fixtures deterministas.

No se utilizan:

- `server/api`;
- requests HTTP;
- base de datos;
- cookies de sesión;
- autenticación;
- persistencia;
- modelos de machine learning;
- generación aleatoria al cargar la página.

Los mocks existen únicamente para evaluar la interfaz de forma estable.

## Elementos descartados de la template

No se trasladan porque no aportan a esta iteración:

- Inbox;
- Settings;
- Members;
- Notifications;
- cookie consent demo;
- gestión de customers;
- endpoints `server/api`;
- datos de mails;
- modales de alta/eliminación de customers;
- enlaces de deploy o feedback propios de la template.

## Backend

**No se implementa backend en esta iteración.**

El frontend no debe crear endpoints falsos para aparentar integración.

Cuando llegue el momento de conectar backend, primero se define un contrato y después los mocks se sustituyen en la frontera de datos.

## Criterio de salida

La maqueta está lista cuando las cuatro rutas sean navegables, conserve la experiencia base del Nuxt Dashboard Template, no contenga endpoints/backend y cualquier valor ficticio esté identificado como demo o mock.
