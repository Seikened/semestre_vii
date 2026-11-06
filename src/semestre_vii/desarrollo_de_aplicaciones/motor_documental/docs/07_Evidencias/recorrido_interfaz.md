# Recorrido de interfaz

2 de noviembre de 2026, Chrome local en macOS. Interfaz y BFF conectados a FastAPI y PostgreSQL en Docker.

1. Consultar la salida anticipada de Cedro: primera fuente, página 2 con OCR. Abrir el enlace al original: el visor PDF mostró la página 2 de 2 y la cláusula de dos mensualidades con aviso de sesenta días.
2. Crear `Revisión ficticia de interfaz` y seleccionarla: la biblioteca mostró el estado vacío.
3. Cargar `FIC-003_mixto.pdf` con título ficticio: apareció con dos páginas, una con OCR. El detalle mostró página 1 digital y página 2 OCR.
4. Editar el título a `Contrato Cedro revisado, ficticio`: la biblioteca reflejó el cambio.
5. Confirmar y retirar exclusivamente ese documento de verificación: la colección volvió al estado vacío. Los seis contratos iniciales permanecieron activos.
6. Detener temporalmente la API y consultar Aurora: la UI conservó el texto y mostró un error con acción de reintento. Restaurar la API y pulsar reintentar: apareció Aurora, página 2, con el plazo de treinta días. La primera fuente quedó visible al comenzar el resultado.

Capturas: `interfaz_inicio.png`, `interfaz_consulta.png`, `interfaz_vacio.png`, `interfaz_pdf_mixto.png`, `original_pagina2.png`, `interfaz_error.png`. Swagger rechazó una consulta documental sin clave con HTTP 401; captura `swagger_negativa.png`.

Estos recorridos no acreditan una conexión a Luna ni la presentación en clase.
