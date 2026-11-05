# Matriz de la rúbrica

Fuente: `referencias/Segundo_Parcial_Criterios_Evaluacion.pdf`, cuatro páginas. Se conserva el puntaje oficial y se distingue documentación de evidencia ejecutada.

| ID | Puntos | Requisito | Evidencia prevista | Estado |
| --- | --- | --- | --- | --- |
| A1 | 4 | Contexto C4 nivel 1 | `01_Arquitectura/C4_Contexto.drawio` y PNG | Diagrama editable y PNG disponibles. |
| A2 | 6 | DAR con componentes, despliegue, red y protocolos | `01_Arquitectura/DAR_Arquitectura.drawio` y PNG | Tres contenedores, redes separadas y protocolos implementados; ver Compose. |
| A3 | 7 | DER y DDA, mínimo cuatro tablas, PK/FK y restricciones | `02_Datos/DER.drawio`, PNG y `DDA.md` | Cuatro tablas con PK/FK, restricciones y DDA; recibo PostgreSQL. |
| A4 | 3 | Índice y vista PostgreSQL justificados | `02_Datos/objetos_bd.sql` y consulta real | Índice GIN, vista y consulta real registrados. |
| A5 | 5 | API, respuestas y seguridad | `03_API/Diseno_API.md` | API key, validación, CORS y BFF implementados; negativos HTTP registrados. |
| B1 | 5 | Instrucciones permanentes equivalentes a CLAUDE.md | `AGENTS.md`, proceso y comandos comprobados | Instrucciones y proceso sincronizados. |
| B2 | 7 | Frontend, API y base en contenedores separados | Compose y ejecución real | Web, API y PostgreSQL separados y ejecutados. |
| B3 | 9 | Cinco endpoints o más, CRUD y prueba negativa | OpenAPI y recibos HTTP | Once operaciones; recorrido repetido con 78/78 controles en `07_Evidencias/servicio_http_luna.json`. Chat y negativos adicionales tienen recibos separados. |
| B4 | 6 | Swagger/OpenAPI con esquemas, ejemplos y respuestas | `/docs` y exportación real | Exportación y Swagger en Chrome verificados. |
| B5 | 8 | Interfaz real, fiel al prototipo, vacío y error | Recorrido de navegador y SC del cambio de proyecto | Verificado en `07_Evidencias/b5_final/README.md`: carga TXT/PDF mixto, OCR, cita, original, vacío, errores reales y recuperación. Dos fallos corregidos. Arrastre simple confirmado por Fernando. Arrastre múltiple y durante carga siguen sin verificación física adicional. |
| B6 | 5 | SC-001 documentada e implementada por capas | `05_Cambios/solicitudes_cambio.md` y PDF mixto | OCR por página implementado en motor, base, API e interfaz; carga y detalle mixtos verificados. |
| C1 | 4 | Carpeta OneDrive completa y compartida | Verificación de estructura y permiso al profesor | Aplazado por Fernando hasta terminar la app; requiere autorización específica. |
| C2 | 9 | Un comando, datos de ejemplo y README suficiente | Arranque desde una copia independiente | Incremento A* comprobado desde ZIP, con volúmenes nuevos y sin clave OpenAI; ver `07_Evidencias/c2_a_asterisco.md`. README incluye reinicio y problemas comunes. Windows sin verificar. |
| C3 | 7 | Tres a cinco prompts y sus ajustes | `06_IA/bitacora_prompts.md` | Cuatro ejemplos reales, con plan disponible, revisión, motivo, autorización y resultado. Los vacíos históricos quedan explícitos. Preparado para revisión académica. |
| D1 | 6 | Flujo completo, SC-001 y negativa | Demostración en vivo | Guion completo preparado; ejecución de la presentación pendiente. |
| D2 | 5 | Explicación C4, DAR y conexión de capas | Guion y exposición | Guion y diagramas actualizados con Luna; exposición pendiente. |
| D3 | 4 | Diez minutos y respuesta a preguntas | Ensayo y explicación de autoría | Recorrido de 600 segundos y respuestas de apoyo preparados; ensayo pendiente. Fernando confirmó exposición el 4 de noviembre a las 17:00. |

Total: 100 puntos. No se calcula una calificación a partir de intenciones.

La [revisión de cierre](15_cierre_rubrica.md) identifica lo que falta y distingue imágenes locales de Docker, publicación pública y entrega oficial.

## Distinción entre rúbrica y guías

Las guías describen una implementación de ejemplo con otras tecnologías, pruebas, MCP y un tag 1.0. La rúbrica admite tecnologías distintas y pide tres contenedores. Las reglas locales de Fernando prevalecen: no agregar suites de tests, no cerrar una versión estable ni enviar nada por inferencia. Las verificaciones serán recorridos reales y reproducibles del servicio.
