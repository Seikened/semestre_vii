# 07 · Prototipo visual frontend

Esta iteración extiende la plantilla oficial de Nuxt Dashboard **sin eliminar ninguna de sus superficies existentes**.

## Principio

La template conserva Home, Inbox, Customers y Settings como baseline visual y funcional.

El dominio de reabastecimiento se añade en paralelo usando los mismos patrones:

| Nueva superficie | Patrón reutilizado |
| --- | --- |
| Resumen operativo | Home: stats + chart + tabla |
| Pedidos | Inbox: lista + detalle + responsive slideover |
| Estaciones | Customers: filtros + tabla + paginación + acciones |
| Modelo | Home: cards + chart + tabla |

## Rutas añadidas

- `/operacion`
- `/pedidos`
- `/estaciones`
- `/modelo`

## Alcance

El objetivo es validar la composición y experiencia, no implementar el sistema real.

Los datos del dominio son fixtures deterministas locales. No se añade API, persistencia, autenticación ni conexión con modelos reales.

Las acciones visibles en el prototipo no representan efectos autoritativos.

## Regla de evolución

Mientras esta etapa sea de maquetado, cualquier cambio debe preferir componentes, composición y lenguaje visual ya presentes en Nuxt Dashboard Template antes de introducir nuevas primitivas.
