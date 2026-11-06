# Reproducción de entradas negativas

La ejecución guardada en `negativas_extraccion.json` corresponde al 2 de noviembre de 2026, 13:57, America/Mexico_City. Se probaron datos reales de entrada contra el extractor, sin mocks ni un servidor simulado. Estos resultados no se presentan como errores HTTP.

Desde la raíz del producto, con el entorno uv sincronizado:

```bash
uv run --project backend python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
import pymupdf
from app.extraccion import Extractor
from app.errores import AppError

with TemporaryDirectory() as temporal:
    carpeta = Path(temporal)
    (carpeta / 'vacio.txt').write_text('  ')
    (carpeta / 'invalido.txt').write_bytes(bytes([255, 254, 0]))
    (carpeta / 'contrato.exe').write_text('ficticio')
    imagen = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 10, 10), False)
    (carpeta / 'imagen.pdf').write_bytes(imagen.tobytes('png'))
    for archivo in carpeta.iterdir():
        try:
            Extractor().extraer(archivo)
        except AppError as error:
            print(archivo.name, error.codigo.value)
        else:
            raise AssertionError(f'Se aceptó una entrada incompatible: {archivo.name}')
PY
```

Se esperan `DOCUMENTO_VACIO` para el TXT vacío y `DOCUMENTO_FORMATO` para las otras tres entradas. El PNG tiene extensión PDF intencionalmente; el extractor comprueba el contenido real.
