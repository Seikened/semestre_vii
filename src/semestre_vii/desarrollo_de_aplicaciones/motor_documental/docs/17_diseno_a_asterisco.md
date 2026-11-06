# A*: referencia visual y verificación

Fernando pidió sustituir la marca visible por `A*`, adoptar colores y estilos de OpenAI y facilitar la incorporación de documentos. Este incremento modifica la interfaz; conserva agente, modelo, contratos HTTP, procesamiento y PostgreSQL.

## Referencias consultadas

- [Apps SDK UI de OpenAI](https://github.com/openai/apps-sdk-ui), sistema de diseño público recomendado para interfaces coherentes con ChatGPT.
- [Tokens primitivos](https://github.com/openai/apps-sdk-ui/blob/0f00143c7a639906f1621fe58e1b6be7b5bea46d/src/styles/variables-primitive.css), [tokens semánticos](https://github.com/openai/apps-sdk-ui/blob/0f00143c7a639906f1621fe58e1b6be7b5bea46d/src/styles/variables-semantic.css) y [variables de componentes](https://github.com/openai/apps-sdk-ui/blob/0f00143c7a639906f1621fe58e1b6be7b5bea46d/src/styles/variables-components.css). Revisión fijada: `0f00143c7a639906f1621fe58e1b6be7b5bea46d`.
- [Guía oficial de UI](https://developers.openai.com/plugins/concepts/ui-guidelines) y [apariencia de ChatGPT](https://help.openai.com/en/articles/11958281-updating-your-visual-experience-on-chatgpt).
- [Guía pública de marca](https://openai.com/brand/). La guía completa enlazada exige autenticación; los valores utilizados proceden del repositorio público y de estilos observados en ChatGPT, no de contenido privado.

Se revisaron también los colores calculados de la página actual de ChatGPT y su tipografía del sistema. Se conservó la marca propia A*. Los componentes siguen siendo Nuxt UI 4.12; no se agregó React ni otra librería de interfaz.

## Valores aplicados

| Pieza | Claro | Oscuro |
| --- | --- | --- |
| Fondo de la aplicación | `#ffffff` | `#0e0e0e` |
| Biblioteca | `#f9f9f9` | `#131313` |
| Compositor | `#f3f3f3` | `#212121` |
| Texto principal | `#0d0d0d` | `#ededed` |
| Hover de botón ghost | Negro `#0d0d0d` al 8 % | Blanco al 12 % |
| Borde de campo | Negro al 16 % | Blanco al 25 % |
| Hover del borde de campo | Negro al 25 % | Blanco al 30 % |
| Foco del campo | Negro al 50 %, 1 px interior | Blanco al 50 %, 1 px interior |
| Foco de teclado en botones | `#0169cc`, 2 px | `#0285ff`, 2 px |

Transiciones básicas de 150 ms. Radios: controles de 8 px, menús de 12 px, paneles de 16 px y compositor de 24 px. Los estados solid, outline, soft, ghost y disabled comparten tokens centrales. El hover no desplaza las tarjetas. Las animaciones respetan movimiento reducido.

La adaptación vive en `frontend/app/assets/openai-tokens.css` y se conecta mediante AppConfig a Nuxt UI. La licencia MIT de OpenAI se conserva en `frontend/THIRD_PARTY_NOTICES.md`.

## Recorridos ejecutados en Chrome

- Marca A* y temas claro/oscuro comprobados en escritorio. Vista móvil de 390 por 700 con biblioteca desplegable y compositor visible.
- Hover real de **Actualizar biblioteca**: `rgba(13, 13, 13, 0.08)` y transición de `0.15s`.
- Foco de teclado: contorno azul de 2 px con separación de 2 px. Campo inválido: borde interior de 1 px `rgb(186, 38, 35)`, radio de 8 px y texto legible.
- Crear colección y adjuntar `test.txt` desde el compositor. Título automático `test`; en **Todas las colecciones** con varios destinos, ninguno preseleccionado. Elegir destino no envió el archivo.
- Confirmar la carga TXT: una página, cero OCR y documento disponible. La pregunta escrita en el compositor se conservó después de cerrar el panel.
- Consultar la penalización de Cedro mediante búsqueda híbrida: actividad pendiente visible y fuente `FIC-003_mixto.pdf`, página 2 OCR, con la cláusula esperada.
- Lint, typecheck y build de producción aprobados. Se reconstruyó y reinició solo web; el motor mantuvo su instalación y sus contratos.

## Evidencia

- [Tema claro](07_Evidencias/a_asterisco/tema_claro_oficial.jpg).
- [Tema oscuro](07_Evidencias/a_asterisco/tema_oscuro_oficial.jpg).
- [Vista móvil](07_Evidencias/a_asterisco/movil_claro.jpg).
- [Formulario móvil](07_Evidencias/a_asterisco/formulario_movil.jpg).
- [Fuente OCR recuperada](07_Evidencias/a_asterisco/busqueda_ocr.jpg).
- [Indexación real durante el primer recorrido A*](07_Evidencias/a_asterisco/indexando.jpg), anterior al ajuste final de bordes y hover.

## Ajuste posterior del pie de biblioteca

Por petición de Fernando se retiró el bloque inferior «PostgreSQL + pgvector» y «Demo local. Documentos ficticios.», junto con sus estilos sin uso. El cambio afecta únicamente `app.vue` y `main.css`; el procesamiento, los datos y la documentación técnica conservan su alcance.

## Cierre posterior de B5

El [recorrido final](07_Evidencias/b5_final/README.md) verifica TXT, PDF mixto, título manual conservado, OCR por página, consulta, original, vacío, rechazo y recuperación ante caída real de la API. Se corrigieron dos fallos: el aviso de archivo vacío persistía después de sustituirlo y una actualización fallida borraba la biblioteca visible. Ambos cambios se comprobaron en la versión compilada.

Fernando confirmó la indexación al soltar un archivo. Se observó un PDF indexado sin pulsar Indexar, pero no se acredita como éxito de la automatización del arrastre. Siguen sin verificación física el rechazo de varios archivos y un segundo arrastre durante carga. La extensión de Chrome rechazó la selección automatizada por su permiso de acceso a URLs de archivo; no se cambió ese permiso y se utilizó el selector nativo.

La animación indica actividad durante la petición. El recorrido de texto/OCR, fragmentos, embeddings e índice vectorial es explicativo: la API no publica etapas intermedias ni porcentajes. El éxito depende de la respuesta real del servicio.

La [copia C2 inicial de A*](07_Evidencias/c2_a_asterisco.md) arrancó con volúmenes nuevos y seis contratos. B5 reutiliza esa instalación aislada y añade tres documentos ficticios. El recibo junto al ZIP identifica el paquete actualizado. OneDrive y correo continúan aplazados por Fernando.
