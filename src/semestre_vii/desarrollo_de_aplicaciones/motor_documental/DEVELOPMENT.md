# Desarrollo

## Metodología

Trabajo iterativo por incrementos pequeños y revisables, continuando el método del repositorio. La entrega cercana y la incertidumbre del OCR justifican verificar cada recorrido antes de agregar otra capacidad. No se denomina Scrum.

## Ciclo de vida

| Etapa | Entrada | Verificación y salida |
| --- | --- | --- |
| Concepción y requerimientos | Necesidad del usuario y rúbrica original | Alcance local con contratos ficticios, separación de la futura conexión LLM y criterios trazables. |
| Diseño | Casos actuales y restricciones | Arquitectura, datos y API revisados; aprobación de piezas críticas y presupuesto. |
| Construcción | Porción aprobada | Código cohesionado, configuración reproducible y documentación sincronizada. |
| Verificación | Capacidad ejecutable | Entradas reales del corpus ficticio, resultados revisados, errores y recuperación observables. |
| Integración y entrega | Gates aplicables aprobados | Revisión independiente, paquete limpio y arranque desde una copia siguiendo README. |
| Operación y mantenimiento | Demo local funcional | Observación de errores, conservación de originales y reindexación controlada cuando cambie el modelo. |

## Reglas

- Priorizar procesamiento, recuperación y después UI.
- Los cambios de persistencia, acceso o contratos se diseñan antes de implementarse.
- Usar solo documentos ficticios. La recuperación no requiere credenciales externas.
- El chat opcional con Luna requiere autorización de consumo y una clave privada externa. Fernando aprobó la prueba del MVP; registrar sus resultados por separado del benchmark de recuperación.
- Comparar extracción nativa y OCR con fuentes conocidas; una página sin texto utilizable no equivale a procesamiento correcto.
- Mantener el servicio local; exponerlo requiere un diseño de acceso y despliegue aprobado.
- Para este semestre basta la demo local. La aceptación del cambio de proyecto está confirmada por Fernando; no volver a presentarla como pendiente.
- Verificar lint, contratos HTTP, build y arranque Compose cuando exista la toolchain.
- Revisar presupuesto y pendientes al terminar cada incremento; simplificar según resultados, sin debilitar los criterios de aceptación.
- OneDrive y correo constituyen la entrega oficial y requieren autorización específica de Fernando, después del cierre funcional de la app.
