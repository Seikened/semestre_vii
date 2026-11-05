# Arranque desde copia independiente

2 de noviembre de 2026, Docker Desktop en macOS.

Se copió el proyecto a `tmp/motor_documental/copia_independiente`, excluyendo entornos, dependencias, builds, cachés y archivos `.env`. Se copió `.env.example` como `.env`. Se detuvieron temporalmente web y API del proyecto principal para liberar los puertos; sus volúmenes se conservaron.

Comando de arranque:

```bash
docker compose -p motor-documental-copia -f tmp/motor_documental/copia_independiente/docker-compose.yml up -d --build
```

El nombre de proyecto diferente aisló los volúmenes del original. No se suministraron credenciales, modelos ni una base previa. La primera ejecución generó credenciales, descargó el modelo e incorporó el corpus automáticamente. El build aprovechó capas de imágenes locales, por lo que esto no mide la descarga inicial de todas las imágenes de Docker.

Resultado: tres contenedores arrancados, API y PostgreSQL saludables. Una colección, seis documentos, doce páginas y doce fragmentos en la base nueva. El BFF Nuxt devolvió los seis documentos, seis páginas nativas y seis páginas con OCR. Recibos: `copia_contenedores.txt` y `copia_postgres.txt`.

Se reconstruyó únicamente web después de ajustar la validación de Origin. `bff_seguridad.json` registra rechazo de origen externo, origen null y ruta no permitida. `aislamiento_web.json` demuestra que web no resuelve PostgreSQL ni tiene su contraseña. `clave_no_publica.json` comprueba que la clave no aparece en el HTML.

La copia se detiene conservando sus volúmenes. El proyecto principal se vuelve a arrancar para revisión. La ejecución en Windows sigue sin verificarse.

## Paquete con estructura exacta

También se arrancó `192488-7_Leon_Fernando_2P/04_Codigo` con el nombre `motor-documental-entrega` y volúmenes nuevos, después de adaptar la carpeta de API a `api/`. Tres contenedores disponibles, conteos 1/6/12/12 y seis documentos por el BFF. La consulta de Cedro recuperó la página 2 y la descarga coincidió byte por byte con el PDF ficticio original. Recibos: `entrega_contenedores.txt`, `entrega_postgres.txt` y `entrega_verificacion.json`.
