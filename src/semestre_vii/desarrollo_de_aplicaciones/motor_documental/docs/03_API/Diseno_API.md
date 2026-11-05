# Diseño de API

**Estado:** endpoints implementados; los resultados ejecutados se registran en `../07_Evidencias/servicio_http.json`.

| Verbo | Ruta | Propósito | Respuestas previstas |
| --- | --- | --- | --- |
| GET | `/salud` | Comprobar servicio y base local | 200, 503. |
| GET | `/colecciones` | Consultar grupos de documentos | 200, 401. |
| POST | `/colecciones` | Crear una colección | 201, 401, 409, 422. |
| GET | `/documentos` | Consultar documentos disponibles, con filtro de colección | 200, 401, 422. |
| POST | `/documentos` | Cargar, extraer, vectorizar e incorporar un PDF o TXT | 201, 401, 413, 415, 422. |
| GET | `/documentos/{id}` | Consultar metadatos y páginas | 200, 401, 404, 422. |
| PATCH | `/documentos/{id}` | Editar título o colección | 200, 401, 404, 422. |
| DELETE | `/documentos/{id}` | Retirar el documento mediante baja lógica | 204, 401, 404, 422. |
| GET | `/documentos/{id}/archivo` | Abrir o descargar el original disponible | 200, 401, 404, 422. |
| POST | `/buscar` | Recuperar fragmentos por texto, vector o combinación | 200, 401, 422. |
| POST | `/chat` | Conversar con Luna usando la recuperación local y fuentes verificadas | 200, 401, 422, 502, 503. |

## Contratos

Los DTO de entrada y salida se validan con Pydantic. Una consulta incluye texto no vacío, modo acotado, límite máximo y colección opcional. Cada coincidencia identifica documento, página, texto y método de extracción. El ranking expresa orden de relevancia, no porcentaje de confianza.

## Acceso

La API valida `X-API-Key`. El BFF de Nuxt la añade en el servidor, utilizando configuración privada. No se envía en el estado de UI ni en enlaces a archivos. Las pruebas directas de Swagger usarán su control Authorize.

Solo se exponen puertos de localhost. CORS utiliza orígenes explícitos. Esta medida protege el servicio de demostración, pero no representa identidad ni permisos por inmobiliaria.

## Errores

Catálogo y handler central. Mensajes seguros en español, sin excepciones crudas ni credenciales. Los fallos no se representan como respuestas exitosas.

## OpenAPI

`openapi.json` se exporta de la API real. Swagger se encuentra en `http://localhost:8000/docs`; el control Authorize recibe la clave del volumen privado. El README explica cómo consultarla localmente.

Ejemplo de consulta: `{"texto":"¿Cuándo se devuelve el depósito de Aurora?","modo":"hibrida","limite":5}`. Los modos permitidos son `texto`, `vector` e `hibrida`. El límite es de 1 a 20; el texto admite de 1 a 1000 caracteres útiles. La carga usa multipart: `archivo`, `titulo` y `coleccion_id`.

La API expone su schema sin clave; las operaciones documentales requieren `X-API-Key`. `/salud` es público y comprueba PostgreSQL. No contiene información de contratos.

## Chat opcional

`POST /chat` recibe `texto` de 1 a 1000 caracteres, `modo`, `coleccion_id` opcional e `historial` de hasta seis mensajes `{rol,texto}`. Los roles permitidos son `user` y `assistant`; cada mensaje admite hasta 4000 caracteres. No acepta modelo, URLs, claves ni selección de herramientas del navegador.

Devuelve `respuesta`, `resultado` con solo las coincidencias citadas y `modelo`. La numeración `[1]` corresponde al orden de esas fuentes. El backend valida que las referencias existan; esto no demuestra por sí solo la fidelidad semántica de cada afirmación.

La herramienta solo formula el texto de consulta. Colección, modo y límite quedan bajo control del backend. Se reutiliza `MotorDocumental.buscar`; no se añaden tablas ni un Store externo. Los errores `LUNA_NO_CONFIGURADA` y `LUNA_NO_DISPONIBLE` devuelven 503; una respuesta incompleta o no válida devuelve 502. Ver [diseño del MVP](../16_chat_luna_mvp.md).
