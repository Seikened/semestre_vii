# 02 · Operación y flujos

## Ciclo semanal

El flujo objetivo es:

1. La sucursal registra su cierre y prepara el pedido de la semana siguiente.
2. El sistema valida la información disponible.
3. El motor genera un pronóstico por sucursal y producto.
4. La aplicación transforma el pronóstico en una recomendación de suministro con información de incertidumbre cuando exista.
5. La sucursal acepta, modifica o descarta la sugerencia y envía su pedido.
6. El personal de la distribuidora compara solicitud y recomendación, revisa el caso y da seguimiento.
7. Al concluir la semana se registra el resultado real.
8. El sistema compara predicción, pedido y resultado observado y actualiza métricas.

La evidencia acumulada puede disparar una evaluación de un modelo candidato, pero **no modifica automáticamente los pesos cada semana**.

## Trazabilidad de la decisión

Cada pedido debe conservar al menos la relación entre:

- recomendación emitida;
- pedido finalmente enviado;
- decisión del usuario: asistida, modificada o manual;
- resultado real cuando esté disponible.

Esta trazabilidad permite medir no sólo precisión del modelo sino también **adopción y utilidad operativa**.

## Portal de sucursal

La experiencia debe estar centrada en una tarea principal: preparar el pedido siguiente con suficiente contexto para decidir.

Debe hacer visible:

- sucursal activa;
- semana o periodo;
- producto;
- datos relevantes del cierre;
- recomendación;
- incertidumbre o confianza, una vez definida su semántica;
- cantidades finalmente solicitadas;
- estado del envío.

No se debe presentar una predicción como hecho observado ni hacer que aceptar la sugerencia sea obligatorio.

## Panel administrativo

El panel se divide conceptualmente en tres áreas.

### Modelo

- métricas generales;
- evolución histórica;
- desglose por sucursal;
- desglose por producto y horizonte cuando aplique;
- señal visible de degradación o drift cuando exista evidencia.

La planeación original propuso un indicador resumido de 0 a 100 %. Esa escala **no debe implementarse hasta definir una fórmula defendible**.

### Pedidos

- cola de solicitudes;
- filtros por sucursal y estado;
- detalle del pedido;
- recomendación asociada;
- diferencia entre sugerencia y solicitud final;
- seguimiento de resolución.

Los estados exactos de la cola todavía deben diseñarse.

### Sucursales y cuentas

- consultar sucursales;
- consultar cuentas asociadas;
- revocar acceso;
- emitir o recuperar credenciales según el mecanismo finalmente aprobado.

## Autenticación

La planeación requiere acceso remoto y recuperación de credenciales, pero todavía no fija proveedor, protocolo ni implementación.

La UI nunca será autoridad de permisos. La autorización debe validarse en una frontera confiable.

## Integración externa

La solución formará parte de una plataforma mayor, pero el equipo no posee todavía su contrato.

Por ello:

- el producto debe mantenerse desacoplado;
- no se inventarán APIs externas;
- no se hará depender el dominio de una integración hipotética;
- la frontera se definirá cuando el responsable del sistema externo proporcione restricciones reales.

## Demostración final esperada

La demo debe permitir, con datos validados:

1. iniciar sesión con una cuenta asociada a una sucursal;
2. preparar un pedido;
3. recibir una predicción y recomendación;
4. aceptar, modificar o ignorar la sugerencia;
5. encontrar el pedido en la experiencia administrativa;
6. identificar cómo se utilizó la recomendación;
7. consultar métricas generales y por sucursal;
8. registrar o simular el resultado real;
9. mostrar la comparación posterior.

## Pendientes operativos

Antes de implementar el flujo completo deben definirse:

- campos exactos del cierre;
- campos exactos del pedido;
- estados de la cola;
- permisos por rol;
- proceso de recuperación de acceso;
- semántica del indicador de confianza;
- fórmula de cualquier KPI resumido;
- condiciones de integración con la plataforma externa.
