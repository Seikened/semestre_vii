# Proyecto final · Minería de Datos — EPOK Links Lab

Laboratorio **sin HTTP ni servidor** para investigar la representación binaria y compresión reversible de URLs. Parte del trabajo de [`epok_links` v0.3.0](https://github.com/Seikened/epok_links/tree/626614f2fc72f5a2774bd5fd62b88371fb861109) sin modificar ni desplegar ese servicio.

## Ejecutar desde la raíz de `semestre_vii`

```bash
uv run python -m semestre_vii.mineria_de_datos.proyectos.proyecto_final 'https://www.example.com/productos?id=12345'
uv run python -m semestre_vii.mineria_de_datos.proyectos.proyecto_final 'https://www.example.com/productos?id=12345' --json
```

La CLI recibe una URL, genera tokens **URL-safe Base64** y **Base32 alfanumérico** y comprueba que ambos reconstruyen la URL original byte a byte en UTF-8. También compara caracteres, bytes y una **estimación QR de modo único, corrección M** (versión y módulos). La estimación QR no genera imágenes ni optimiza segmentos mixtos.

Los enlaces `https://rd.epok.com.mx/c/...` que presenta son **simulaciones** para comparar el costo completo; esa ruta no existe en el servicio publicado. La decodificación se realiza localmente en `codec.url.descompactar`.

## Estado y alcance

Versión experimental del formato: **01**. El compresor usa un catálogo estático de cuatro prefijos comunes (`https://www.`, `https://`, `http://www.`, `http://`) y elige entre cuerpo literal y DEFLATE nivel 9 según cuál ocupe menos bytes. Los datos se encapsulan en 2 bytes de cabecera y se transportan con Base64 URL-safe o Base32. Acepta HTTP(S) con host, hasta 8192 bytes UTF-8, y preserva exactamente la cadena ingresada, sin normalizar mayúsculas, parámetros ni escapes.

El módulo `codec/compresion.py` es una **adaptación** del baseline y del control de descompresión de EPOK Links v0.3.0 (commit `626614f`). Se reutiliza el concepto de formato autocontenido; **no** se copian FastAPI, autenticación, cifrado, destinos ni infraestructura. No requiere secretos, red ni base de datos.

**Pendiente de investigar:** parser de componentes y vocabulario, diccionarios minados de URLs, representación de `www`/TLD/rutas, Huffman o ANS, alfabetos alternativos, comparación con ha.mr, corpus reproducible y validación QR con codificador real.

## Verificación inicial

Ejecutar las dos variantes anteriores y confirmar `recuperacion_exacta = true`. Probar además URLs con query, fragmento, escapes, mayúsculas, Unicode, prefijos distintos y texto poco compresible; registrar los resultados en `documentacion/resultados.md`. Los datos reales no deben contener tokens o secretos privados. No se incorpora suite de tests al repositorio académico.

## Documentación

[Objetivos](documentacion/objetivos.md) · [Fuentes](documentacion/fuentes.md) · [Estrategia](documentacion/estrategia.md) · [Resultados](documentacion/resultados.md)
