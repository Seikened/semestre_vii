# Frontend · Reabastecimiento de gasolineras

Prototipo visual de la aplicación de **Pronóstico y reabastecimiento de gasolineras**.

Esta iteración es deliberadamente **frontend-only**:

- no existe backend;
- no hay autenticación real;
- no hay persistencia;
- no hay endpoints locales;
- no hay modelo conectado;
- todos los datos visibles son mocks deterministas.

## Base visual

El scaffold parte del proyecto oficial **Nuxt Dashboard Template** de `nuxt-ui-templates/dashboard`, la misma plantilla publicada en `dashboard-template.nuxt.dev`.

Snapshot de referencia:

```text
nuxt-ui-templates/dashboard
main @ 8915adfc5139823d65a816792ce365842497c7d1
```

Se conserva su enfoque de dashboard con Nuxt UI: sidebar colapsable, búsqueda, cards, tablas y visualización. Se eliminaron Inbox, Settings, notificaciones y los `server/api` de la demo porque no pertenecen a esta iteración.

La plantilla original se distribuye bajo licencia MIT. El aviso correspondiente se conserva en `LICENSE.nuxt-dashboard`.

## Vistas

- `/` — resumen operativo;
- `/pedidos` — cola simulada de pedidos;
- `/estaciones` — listado reducido de estaciones;
- `/modelo` — visualización conceptual de forecasting y candidatos.

## Ejecución

```bash
pnpm install
pnpm dev
```

Verificación:

```bash
pnpm lint
pnpm typecheck
pnpm build
```

El diseño funcional de esta maqueta está documentado en `../docs/07_maquetado_frontend.md`.
