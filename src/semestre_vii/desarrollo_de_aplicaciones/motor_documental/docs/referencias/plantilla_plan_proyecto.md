# Plan de Proyecto — LabPresta: Sistema de Préstamo de Equipo de Laboratorio

**Versión:** 1.0 · **Fecha:** octubre 2026
**Elaboró:** M.I. Ricardo Medrano · **Cliente (caso didáctico):** Coordinación de Laboratorios, Departamento de Ingenierías

> Proyecto espejo para la práctica de Claude Code en la materia Ingeniería de Software. Estructura condensada del formato de Plan de Proyecto visto en clase.

---

## 1. Antecedentes

La Coordinación de Laboratorios presta a alumnos y profesores equipo como laptops, kits Arduino/Raspberry Pi, osciloscopios, multímetros y cámaras. Actualmente el control se lleva en una hoja de cálculo compartida y en una libreta en mostrador.

## 2. Problemática

- No se sabe en tiempo real qué equipo está disponible; el alumno debe ir al mostrador a preguntar.
- Los préstamos vencidos se detectan tarde o nunca; hay equipo "perdido" que en realidad está prestado.
- La hoja de cálculo se sobrescribe y no hay historial confiable por alumno o por equipo.

## 3. Objetivos

**Objetivo general:** Implementar una aplicación web que registre el inventario de equipo de laboratorio y el ciclo completo de préstamo y devolución, con visibilidad en tiempo real del estado de cada equipo.

**Objetivos específicos:**

| ID | Objetivo | Medición |
|----|----------|----------|
| OE1 | Registrar el 100% del equipo prestable con su estado actual | Catálogo con todos los equipos cargados |
| OE2 | Registrar un préstamo en menos de 1 minuto desde el mostrador | Tiempo promedio de captura medido en pruebas |
| OE3 | Identificar automáticamente los préstamos atrasados | 100% de préstamos vencidos marcados como *atrasado* |
| OE4 | Mantener historial de préstamos por equipo y por solicitante | Consulta disponible vía API |

## 4. Descripción de la solución

Aplicación web de tres capas desplegada con contenedores:

- **Front end:** HTML + CSS + JavaScript estático servido por **nginx**, derivado del prototipo aprobado.
- **API REST:** **FastAPI** (Python 3.12) con documentación automática OpenAPI/Swagger.
- **Base de datos:** **PostgreSQL 16**, con migraciones administradas por Alembic.
- **Orquestación local:** **Docker Compose** (servicios `web`, `api`, `db`).

## 5. Alcance — Fase 1 (MVP)

### 5.1 Entidades

**Equipo**
- `id`, `clave_inventario` (única, p. ej. `LAB-LAP-001`), `nombre`, `categoria` (Cómputo, Electrónica, Medición, Audiovisual), `estado` (`disponible`, `prestado`, `mantenimiento`), `fecha_alta`.

**Solicitante**
- `id`, `matricula` (única), `nombre`, `correo` (institucional), `carrera`.

**Préstamo**
- `id`, `equipo_id` (FK), `solicitante_id` (FK), `fecha_salida`, `fecha_compromiso`, `fecha_devolucion` (nula mientras no se devuelva), `estado` (`activo`, `devuelto`, `atrasado`).

### 5.2 Reglas de negocio

- **RN1.** Solo se puede prestar un equipo cuyo estado sea `disponible`. Al registrar el préstamo, el equipo cambia a `prestado`.
- **RN2.** Un préstamo `activo` cuya `fecha_compromiso` ya pasó se considera `atrasado`.
- **RN3.** Al registrar la devolución se guarda `fecha_devolucion`, el préstamo pasa a `devuelto` y el equipo regresa a `disponible`.

### 5.3 Módulos y entregables

| Módulo | Entregable | Criterio de aceptación |
|--------|-----------|------------------------|
| M1 Catálogo de equipo | CRUD de Equipo (API) + pantalla de catálogo con filtro por estado y categoría | Se puede dar de alta, editar, consultar y dar de baja equipo; el filtro muestra solo los equipos del estado elegido |
| M2 Solicitantes | CRUD de Solicitante (API) | No se permiten matrículas duplicadas; el correo se valida |
| M3 Préstamos | Registro de préstamo (API + pantalla) | No se puede prestar un equipo no disponible (RN1); el equipo cambia de estado |
| M4 Préstamos activos y devolución | Lista de préstamos activos/atrasados + botón de devolución | Los atrasados se distinguen visualmente (RN2); la devolución aplica RN3 |
| M5 Infraestructura | `docker-compose.yml` con los tres servicios + datos de ejemplo | `docker compose up` levanta el sistema completo en localhost |

### 5.4 Pantallas (prototipo)

1. **Catálogo de equipo** — tabla/tarjetas con filtro por estado y categoría.
2. **Registrar préstamo** — selección de equipo disponible, solicitante y fecha compromiso.
3. **Préstamos activos** — lista con indicador de atraso y acción de devolución.

## 6. Indicadores de éxito

- Sistema levantado en localhost con un solo comando.
- 100% de los endpoints CRUD probados desde Swagger.
- Las tres reglas de negocio verificadas con pruebas automatizadas (pytest).

## 7. Componente de IA

No aplica en Fase 1. *(Nota didáctica: en los proyectos de los alumnos el componente de IA se representa en el MVP como un endpoint simulado si el modelo aún no está listo).*

## 8. Exclusiones de Fase 1

- Autenticación y roles de usuario.
- Notificaciones por correo de préstamos atrasados.
- Reservas anticipadas y multas.
- Despliegue en nube (Fase 2: Azure).

## 9. Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Front end | HTML5, CSS, JavaScript (fetch API), nginx |
| Back end | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic 2, Alembic |
| Base de datos | PostgreSQL 16 |
| Pruebas | pytest, Swagger UI |
| Contenedores | Docker, Docker Compose |
| Control de versiones | Git |
| Asistente de desarrollo | Claude Code |

## 10. Infraestructura

Entorno local en la computadora del desarrollador (Windows o macOS) con Docker Desktop. Puertos sugeridos: `web` 8080, `api` 8000, `db` 5432 (o 5433 si existe un PostgreSQL local).

## 11. Equipo y estimación

| Rol | Responsable | Esfuerzo |
|-----|------------|----------|
| Desarrollador full stack (con Claude Code) | Ricardo Medrano | 8 h |

## 12. Cronograma

| Bloque | Actividad |
|--------|----------|
| 1 | Contexto del proyecto (`CLAUDE.md`), arquitectura y contenedores base |
| 2 | Modelo de datos, migraciones, API REST |
| 3 | Front end a partir del prototipo |
| 4 | Mantenimiento, pruebas y documentación |

## 13. Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| Docker/WSL2 no funciona en Windows | Verificación previa con `docker run hello-world` |
| Conflicto de puerto 5432 con PostgreSQL local | Mapear la base a 5433 |
| Código generado que no se entiende o no se revisa | Modo plan antes de cada cambio grande y commits frecuentes |
| Límites de uso del plan de Claude | Tareas pequeñas y `/clear` entre tareas |

## 14. Supuestos

- Se cuenta con licencia de Claude con acceso a Claude Code.
- El prototipo aprobado está disponible como HTML en la carpeta `/prototipo`.
