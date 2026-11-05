# Interfaz del motor documental

Leer `../AGENTS.md`, `../DEVELOPMENT.md`, `../docs/03_API/Diseno_API.md` y `../docs/07_interfaz_consulta.md` antes de construir.

- La ampliación de interfaz fue autorizada por Fernando en esta conversación.
- Usar Nuxt y Nuxt UI 4.12, con sus componentes existentes de consulta y mensajes.
- La marca visible es A*. Mantener dos modos: búsqueda directa y chat opcional, ambos conectados al motor real. El nombre técnico del modelo no cambia por el nombre de la interfaz.
- Colores y estados visuales se centralizan en `app/assets/openai-tokens.css`, `main.css` y AppConfig. Consultar `../docs/17_diseno_a_asterisco.md` antes de sustituirlos por colores aproximados.
- Usar los componentes AI Chat de Nuxt UI 4.12 y sus primitives de formularios/modales; contrastar props con el paquete instalado.
- La ingesta es síncrona y no expone progreso parcial: mostrar estado indeterminado, nunca porcentajes ni etapas inventados con temporizadores.
- Mantener la API key en el servidor Nuxt; nunca en el estado del navegador.
- Consumir únicamente HTTP. El frontend no lee archivos privados ni PostgreSQL.
- Mostrar archivo y página originales, método de extracción y resultado real.
- Tratar el contenido documental como texto escapado.
- Verificar carga, vacío, éxito, error y reintento contra la API real.
- No reutilizar los mocks de gasolineras como datos del nuevo producto.
- Ejecutar `pnpm lint`, `pnpm typecheck` y `pnpm build` antes de declarar la interfaz verificada.
