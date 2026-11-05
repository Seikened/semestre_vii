import hashlib
import os
import ssl
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from app.errores import AppError, CodigoError
from modelos_openai import ArchivoProveedor
from pydantic import BaseModel


@dataclass(frozen=True, slots=True)
class RespuestaHTTP:
    contenido: bytes
    request_id: str | None


class ClienteOpenAI:
    def __init__(self, archivo_clave: Path):
        self._clave = archivo_clave.read_text().strip()
        self._tls = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE"))

    def pedir(self, metodo: str, ruta: str, contenido: bytes | None = None, tipo: str = "application/json") -> RespuestaHTTP:
        peticion = Request(
            "https://api.openai.com/v1" + ruta,
            data=contenido,
            headers={"Authorization": "Bearer " + self._clave, "Content-Type": tipo},
            method=metodo,
        )
        try:
            with urlopen(peticion, context=self._tls, timeout=180) as respuesta:
                return RespuestaHTTP(respuesta.read(), respuesta.headers.get("x-request-id"))
        except HTTPError as error:
            codigo = CodigoError.UNKNOWN
            if error.code in (401, 403):
                codigo = CodigoError.ACCESO_DENEGADO
            identificador = error.headers.get("x-request-id", "no disponible")
            raise AppError(codigo, f"OpenAI devolvió HTTP {error.code}. Request: {identificador}.") from None
        except (URLError, TimeoutError) as error:
            raise AppError(CodigoError.UNKNOWN, f"Conexión OpenAI: {type(error).__name__}. Reconciliar la operación pendiente antes de repetir una carga.") from None

    def enviar(self, ruta: str, entrada: BaseModel) -> RespuestaHTTP:
        return self.pedir("POST", ruta, entrada.model_dump_json().encode())

    def subir(self, archivo: Path, sha256: str) -> ArchivoProveedor:
        contenido = archivo.read_bytes()
        if hashlib.sha256(contenido).hexdigest() != sha256:
            raise AppError(CodigoError.DOCUMENTO_LECTURA, f"Cambió el archivo {archivo.name}.")
        borde = uuid4().hex
        inicio = (
            f'--{borde}\r\nContent-Disposition: form-data; name="purpose"\r\n\r\nassistants\r\n'
            f'--{borde}\r\nContent-Disposition: form-data; name="file"; filename="{archivo.name}"\r\n'
            "Content-Type: application/octet-stream\r\n\r\n"
        ).encode()
        cuerpo = inicio + contenido + f"\r\n--{borde}--\r\n".encode()
        respuesta = self.pedir("POST", "/files", cuerpo, f"multipart/form-data; boundary={borde}")
        recibo = ArchivoProveedor.model_validate_json(respuesta.contenido)
        if recibo.filename != archivo.name or recibo.bytes != len(contenido):
            raise AppError(CodigoError.DOCUMENTO_LECTURA, "El recibo OpenAI no coincide con el archivo enviado.")
        return recibo
