# Plan de proyecto: motor documental inmobiliario

**Estado:** alcance funcional autorizado; ampliación técnica de la rúbrica autorizada por Fernando; verificación registrada por capacidad.
**Fecha:** 2 de noviembre de 2026.
**Responsable:** Fernando Leon Franco.
**Cliente de demostración:** inmobiliaria ficticia, sin datos reales.

Se conserva la estructura de 14 apartados de la plantilla del profesor.

## 1. Antecedentes

Una inmobiliaria maneja contratos y expedientes de distintas propiedades. Fernando sustituyó el proyecto de gasolineras por un motor documental, conservando la estructura de trabajo del repositorio.

## 2. Problemática

Encontrar manualmente cláusulas y documentos se vuelve costoso cuando aumenta el archivo. Los escaneos añaden una dificultad: su contenido debe convertirse en texto antes de indexarse.

## 3. Objetivos

Construir una demostración local que organice contratos ficticios, extraiga su texto, genere embeddings y permita buscar evidencias con archivo y página verificables. Preparar el MVP el 3 de noviembre; la rúbrica fija entrega formal el 4 de noviembre antes de las 19:00.

## 4. Descripción de la solución

Servicio Python de ingesta y recuperación, PostgreSQL con pgvector y originales en volumen local. Interfaz Nuxt UI 4.12 para cargar documentos y consultar resultados. La conexión a GPT-6 Luna pertenece al paso dos.

## 5. Alcance de la entrega académica

### 5.1 Entidades

Colección, documento, página y fragmento. Cada pieza posee una relación real con la anterior; las cuatro tablas responden al recorrido documental y al mínimo de la rúbrica.

### 5.2 Reglas de negocio

- El corpus de ejemplo es completamente ficticio y está rotulado como tal.
- La búsqueda utiliza únicamente documentos disponibles y conserva su procedencia.
- Los vectores de consulta y documento utilizan el mismo modelo y dimensión.
- La extracción se decide por página para admitir PDF mixtos.
- Un documento sin texto utilizable no se declara indexado correctamente.
- La API valida acceso, archivos, tamaños e identificadores.
- Un resultado de búsqueda no se presenta como respuesta generada por Luna.

### 5.3 Módulos y entregables

| Módulo | Entregable | Aceptación |
| --- | --- | --- |
| M1 Organización y gestión | Colecciones y CRUD documental | Crear, consultar, editar y retirar datos con validación. |
| M2 Extracción y OCR | Texto por página y método utilizado | PDF digital, escaneado y mixto con procedencia correcta. |
| M3 Indexación y recuperación | Embeddings locales y tres modos de búsqueda | Consultas con evidencia conocida y resultados revisables. |
| M4 Interfaz de consulta | Nuxt UI con componentes de chat | API real, carga, resultados, vacío, error y recuperación. |
| M5 Ejecución y entrega | Compose, seed, documentación y paquete | Levantar desde otra carpeta con un comando. |

### 5.4 Pantallas

Una interfaz de consulta con biblioteca de documentos, carga, organización por colección y resultados con fuentes. La UI conversacional funciona como explorador de evidencias en esta etapa.

## 6. Indicadores de éxito

Recuperación de la fuente correcta entre los primeros cinco resultados; métodos de extracción correctos por página; prueba negativa con error esperado; arranque reproducible y ejecución desde una copia independiente. Registrar resultados reales antes de atribuir cumplimiento.

## 7. Componente de IA

Embeddings multilingües locales para recuperación semántica. Comparar búsqueda textual, vectorial e híbrida. El modelo concreto y los resultados deben quedar registrados al ejecutarse. GPT-6 Luna se integrará después, con credenciales proporcionadas por Fernando.

## 8. Exclusiones de la entrega académica

Documentos reales, interpretación jurídica automatizada, acceso de múltiples inmobiliarias, entrenamiento de un modelo desde cero, integración de Luna, R2 y WhatsApp oficial. La futura integración no se acredita mediante una simulación.

## 9. Stack tecnológico

Nuxt UI 4.12 y Vue para interfaz; Python y uv para servicio; FastAPI y Pydantic para HTTP; PostgreSQL con pgvector para catálogo y recuperación. Extracción/OCR y embeddings se seleccionan mediante ejecución local. Tres contenedores separados por exigencia de la rúbrica.

## 10. Infraestructura

Docker Desktop, red privada Compose, volúmenes de PostgreSQL y documentos, web y Swagger publicados en localhost. El entorno del servicio es independiente del de las otras materias. No contratar infraestructura ni usar APIs de pago en esta etapa.

## 11. Equipo y estimación

Fernando revisa alcance y resultados; el asistente implementa y verifica; un subagente independiente audita contra requisitos. Primera porción inicial: 350 a 550 líneas. Ampliación de rúbrica autorizada: 1200 a 1600 líneas de aplicación, documentación y artefactos aparte. Son estimaciones de código, no promesas de tiempo.

## 12. Cronograma

Trabajo iterativo por incrementos revisables: diseño, procesamiento, recuperación, interfaz, verificación y empaque. El 2 de noviembre se revisan fuentes y alcance; el objetivo del 3 es una demo local. La entrega oficial del PDF es el 4 antes de las 19:00. No se asignan avances a fechas históricas de gasolineras.

## 13. Riesgos

OCR incorrecto, descargas iniciales de modelos, incompatibilidad de dependencias, Docker no disponible, poco tiempo de integración y fallos de interfaz. Mitigar con corpus pequeño, validación temprana, copia limpia y límites visibles. La aceptación del cambio de proyecto quedó confirmada por Fernando el 2 de noviembre de 2026. Mantener pendiente cualquier requisito funcional sin evidencia.

## 14. Supuestos

La demo utiliza un operador local y seis contratos sintéticos iniciales. La emulación consiste en consultar el motor y revisar sus evidencias; existe además un chat opcional con Luna. La rúbrica puede cumplirse con tecnologías distintas del ejemplo cuando se conservan las tres capas en contenedores. Fernando confirmó que el profesor aceptó el cambio de dominio. Este semestre requiere demostración local; no se exige montar el producto en línea.
