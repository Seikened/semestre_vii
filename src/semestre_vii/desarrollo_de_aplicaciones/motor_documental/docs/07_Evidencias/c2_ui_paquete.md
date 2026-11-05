# Arranque del paquete con la interfaz final

Verificación del 2 de noviembre de 2026, America/Mexico_City. Se extrajo el ZIP académico en una ubicación independiente y se ejecutó desde su `04_Codigo/`, sin `.env` ni clave de OpenAI.

```bash
WEB_PORT=3100 API_PORT=8100 LUNA_API_KEY_FILE=./luna_api_key.example \
docker compose -p motor-documental-c2-ui-final -f docker-compose.yml up --build -d
```

Los puertos y el nombre de proyecto alternos evitaron afectar la demo principal en 3000/8000. Las redes y los cinco volúmenes pertenecen a este proyecto aislado. No se modificaron los puertos internos de API ni PostgreSQL.

## Resultado ejecutado

- Comando completado correctamente; construcción de API y web incluida.
- Tres servicios activos: API y PostgreSQL saludables, web con respuesta HTTP comprobada. Web no define healthcheck propio.
- Modelo `intfloat/multilingual-e5-small`, 384 dimensiones, descargado al volumen nuevo. Primer arranque con Internet; Docker reutilizó capas de construcción disponibles.
- Seis documentos iniciales, doce páginas y seis páginas OCR. No se copiaron los datos de la instalación principal.
- Búsqueda híbrida de salida anticipada de Cedro: fuente correcta `FIC-003_mixto.pdf`, página 2 OCR, con penalización de dos mensualidades.
- Búsqueda textual de `expedienteinexistentexyzq123`: cero coincidencias.
- Chat sin clave: HTTP 503 esperado; Chrome mostró el aviso de indisponibilidad y conservó la pregunta. No hubo llamada al proveedor en esta instalación.
- Chrome abrió la interfaz del paquete en 3100 y ejecutó la búsqueda local correctamente después del aviso del chat.

## Recibos

- [Construcción y arranque](c2_ui_arranque.log).
- [Salud, servicios, documentos y respuestas HTTP](c2_ui_http.json).
- [Interfaz sin clave de Luna](c2_ui_sin_clave.jpg).
- [Recuperación local en la copia independiente](c2_ui_busqueda_local.jpg).

El JSON identifica el hash del ZIP empleado en el primer arranque. El empaque posterior incorpora este informe, sus recibos y el nombre actualizado del botón `Luna` en README, sin modificar el código de aplicación comprobado. Se conserva aparte la validación del archivo final y se comprueba de nuevo su arranque con los volúmenes de esta instalación de verificación.

La prueba no acredita ejecución en Windows, descarga de todas las capas Docker sin caché ni disponibilidad del proveedor de Luna. La instalación principal permanece disponible para Fernando. Los contenedores auxiliares se detienen al terminar, conservando sus volúmenes.
