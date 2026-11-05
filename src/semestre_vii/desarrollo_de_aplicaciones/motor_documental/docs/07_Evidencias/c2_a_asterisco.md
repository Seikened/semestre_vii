# C2: copia independiente del incremento A*

Verificación del 2 de noviembre de 2026, America/Mexico_City. Se regeneró el ZIP académico con la interfaz A* y se extrajo en otra ubicación. La demo principal en 3000/8000 se conservó.

## Arranque ejecutado

Desde el `04_Codigo/` de la copia extraída:

```bash
WEB_PORT=3100 API_PORT=8100 LUNA_API_KEY_FILE=./luna_api_key.example \
docker compose -p motor-documental-c2-a-asterisco up --build -d
```

Los puertos y el nombre de proyecto alternos aíslan esta comprobación. El proyecto creó redes, credenciales, base, originales y volumen de modelos propios. La clave de OpenAI estuvo vacía durante toda la prueba.

El comando construyó API y web y terminó correctamente. Docker reutilizó capas disponibles; el modelo E5 se descargó al volumen de modelos nuevo. La API y PostgreSQL alcanzaron estado saludable; la web respondió HTTP 200. No se acredita una construcción sin caché ni ejecución en Windows.

## Resultado observado

- Seis documentos iniciales, doce páginas y seis páginas procesadas con OCR.
- Marca A* y biblioteca visibles en Chrome en `http://localhost:3100`.
- Consulta híbrida natural de salida anticipada de Cedro: la cláusula correcta apareció en **posición 2**, en `FIC-003_mixto.pdf`, página 2 OCR. Conservó «dos mensualidades» y «sesenta días».
- El primer resultado fue la página 1 del mismo contrato. La primera comprobación asumía por error que la cláusula ocuparía el primer lugar y falló. Se conservó la consulta y se verificó la fuente dentro de los cinco resultados; no se acredita ranking perfecto.
- Descarga del original por BFF: HTTP 200 y cabecera de archivo PDF válida.
- Búsqueda textual de una cadena inexistente: cero coincidencias.
- Chat sin clave: HTTP 503 con `LUNA_NO_CONFIGURADA`, sin llamada al proveedor.
- Búsqueda ejecutada en Chrome; fuente OCR y texto de la cláusula visibles. No se observaron errores de consola en ese recorrido.

## Recibos

- [Construcción y arranque](c2_a_asterisco_arranque.log).
- [Consultas HTTP y posición de la fuente](c2_a_asterisco_http.json).
- [Consulta natural conservada](c2_a_asterisco_consulta_natural.json).
- [Interfaz de la copia y fuente OCR](c2_a_asterisco_busqueda.jpg).

El recibo HTTP identifica el ZIP usado para el arranque inicial. Después se incorporaron esta evidencia y la documentación de cierre. Fernando pidió posteriormente retirar el pie de biblioteca, un ajuste de `app.vue` y `main.css` sin cambios del motor. La verificación del ZIP final se guarda junto al archivo en `entregas/desarrollo_de_aplicaciones/192488-7_Leon_Fernando_2P.verificacion.json`, fuera del propio ZIP para evitar un hash circular. Ese recibo identifica el código comprobado y distingue la instalación inicial con volúmenes nuevos de los arranques posteriores.

C2 no acredita los recorridos físicos pendientes de arrastre y PDF automático de B5, ni una respuesta actual de Luna. El [checklist](../15_cierre_rubrica.md) conserva esas diferencias. OneDrive, envío oficial, ensayo y exposición siguen pendientes.
