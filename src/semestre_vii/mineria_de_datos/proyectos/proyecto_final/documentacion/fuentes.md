# Fuentes y procedencia

- **Inspiración:** PortalRunner / p2r3, [ha.mr, repositorio del compresor de enlaces](https://github.com/p2r3/ha.mr). Estudiar vocabularios de URLs, codificación reversible y estrategias QR; no asumir sus métricas como resultados nuestros.
- **Código inicial adaptado:** [EPOK Links v0.3.0, commit 626614f](https://github.com/Seikened/epok_links/commit/626614f2fc72f5a2774bd5fd62b88371fb861109), `src/epok_links/tokens/compresion.py` (DEFLATE y límite de descompresión). El resto es una adaptación nueva para experimentos académicos.
- **Referencias técnicas:** [RFC 3986, sintaxis de URI](https://www.rfc-editor.org/rfc/rfc3986); [RFC 4648, Base32/Base64](https://www.rfc-editor.org/rfc/rfc4648); [RFC 1951, DEFLATE](https://www.rfc-editor.org/rfc/rfc1951); [ISO/IEC 18004, QR Code](https://www.iso.org/standard/83389.html).

Estas fuentes guían el diseño; la versión actual del laboratorio es un baseline experimental, no una reproducción de ha.mr ni una implementación completa del estándar QR.
