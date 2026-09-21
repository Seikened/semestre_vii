# 01 · Producto y alcance

## Contexto

Una distribuidora atiende aproximadamente **120 gasolineras**. Cada sucursal realiza un cierre semanal y envía información sobre sus ventas para solicitar el suministro de la semana siguiente.

La distribuidora cuenta con alrededor de cinco o seis responsables y cada persona atiende cerca de veinte sucursales. El histórico disponible se ha descrito como cercano a diez años de registros semanales, pero la cantidad realmente utilizable debe confirmarse después de auditar calidad, continuidad y consistencia.

## Problema

El proceso actual depende de la información enviada por las sucursales y de la revisión del personal de la distribuidora. Sin una predicción sistemática, la decisión de cuánto combustible solicitar o suministrar no aprovecha por completo el histórico ni permite medir de forma continua qué tan acertadas fueron las estimaciones.

## Propuesta

Construir una plataforma web que conecte la captura semanal con un motor predictivo. El sistema pronosticará la demanda de la semana siguiente por sucursal y producto, generará una recomendación de suministro y permitirá comparar esa recomendación con el pedido enviado y con el resultado real posterior.

La recomendación **asiste** la decisión humana. No aprueba pedidos automáticamente.

## Objetivo

Desarrollar y validar antes de finalizar diciembre de 2026 una solución de apoyo al reabastecimiento para una distribuidora que atiende 120 gasolineras. La solución utilizará el histórico semanal validado para pronosticar ventas por sucursal, recomendar suministro y comparar cada predicción con el resultado real.

La meta inicial es reducir al menos **10 %** el error respecto de un baseline estacional simple. Este umbral sigue pendiente de confirmación con los datos disponibles y con el profesor; no se considera todavía un requisito irrevocable.

## Alcances funcionales

### 1. Autenticación y cuentas

- acceso remoto mediante credenciales;
- asociación de cada cuenta con una sucursal o rol;
- recuperación de acceso;
- revocación y emisión controlada de credenciales;
- permisos según el tipo de usuario.

Los permisos exactos y el mecanismo final de recuperación permanecen pendientes.

### 2. Panel de administración

Debe permitir:

- revisar el desempeño del modelo globalmente y por sucursal;
- consultar indicadores y su evolución;
- recibir y filtrar pedidos;
- comparar pedido y recomendación;
- dar seguimiento a su resolución;
- administrar sucursales y cuentas.

### 3. Portal de sucursal

La persona responsable de una gasolinera podrá:

- registrar el cierre;
- crear el pedido de la semana siguiente;
- consultar una recomendación predictiva;
- aceptar la sugerencia;
- modificarla;
- ignorarla y capturar manualmente;
- entregar el resultado real al cierre del periodo.

### 4. Modelo predictivo

Incluye:

- auditoría y preparación del histórico;
- baselines;
- experimentación;
- forecasting;
- incertidumbre o confianza;
- recomendación de suministro;
- backtesting;
- evaluación general y por sucursal;
- seguimiento de drift;
- criterios de actualización y reentrenamiento.

## Roles

| Rol | Responsabilidad |
| --- | --- |
| Encargado de sucursal | Registrar cierre, enviar pedido y consultar la recomendación. |
| Responsable de distribuidora | Atender sus sucursales, cotejar información y revisar o aprobar pedidos. |
| Administración / management | Consultar desempeño, revisar pedidos y administrar cuentas. |
| Equipo del proyecto | Datos, modelado, aplicación, integración y verificación. |

## Fuera de alcance

- desarrollar la plataforma completa de la distribuidora;
- modificar internamente un sistema externo al que el equipo no tiene acceso;
- operar indefinidamente el sistema después de la entrega académica;
- aprobar pedidos automáticamente mientras esa capacidad no se agregue de forma explícita.

## Supuestos vigentes

- 120 gasolineras se considera la cifra de referencia;
- existe histórico semanal, pero debe validarse cuánto es utilizable;
- las sucursales alimentarán el cierre;
- la distribuidora revisará los pedidos;
- cada cuenta de sucursal estará asociada con una gasolinera;
- la recomendación es asistencia, no autoridad;
- la integración con una plataforma mayor se definirá cuando existan interfaces reales.

## Nomenclatura de combustibles

La planeación histórica menciona Premium, Regular y diésel; documentación técnica posterior utilizó Magna, Premium y Diésel. **No se fija todavía la taxonomía comercial**. El dataset real y el negocio deben definir los nombres y categorías canónicas.

## Proyecto y operación continua

El desarrollo hasta diciembre de 2026 es un proyecto con plazo, entregables y demostración.

La carga semanal, generación periódica de forecasts, seguimiento del error, mantenimiento y reentrenamientos posteriores pertenecen a una operación continua. La demo debe demostrar ese ciclo, no fingir que el sistema ya opera indefinidamente en producción.
