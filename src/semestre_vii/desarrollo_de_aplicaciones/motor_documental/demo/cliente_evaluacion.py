import hashlib
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import UUID, uuid4

from app.contratos import (
    Coleccion,
    Consulta,
    DetalleDocumento,
    Documento,
    ErrorRespuesta,
    NuevaColeccion,
    ResultadoBusqueda,
)
from app.errores import AppError, CodigoError
from pydantic import TypeAdapter


class ClienteMotor:
    def __init__(self, clave: Path, url: str = "http://127.0.0.1:8000"):
        self._clave = clave.read_text().strip()
        self.url = url

    def coleccion(self, nombre: str) -> Coleccion:
        existentes = TypeAdapter(list[Coleccion]).validate_json(self._pedir("GET", "/colecciones"))
        encontrada = next((c for c in existentes if c.nombre == nombre), None)
        if encontrada:
            return encontrada
        entrada = NuevaColeccion(nombre=nombre)
        respuesta = self._pedir("POST", "/colecciones", entrada.model_dump_json().encode(), "application/json")
        return Coleccion.model_validate_json(respuesta)

    def documentos(self, coleccion_id: UUID) -> list[Documento]:
        respuesta = self._pedir("GET", f"/documentos?coleccion_id={coleccion_id}")
        return TypeAdapter(list[Documento]).validate_json(respuesta)

    def detalle(self, identificador: UUID) -> DetalleDocumento:
        return DetalleDocumento.model_validate_json(self._pedir("GET", f"/documentos/{identificador}"))

    def original(self, identificador: UUID) -> bytes:
        return self._pedir("GET", f"/documentos/{identificador}/archivo")

    def buscar(self, entrada: Consulta) -> ResultadoBusqueda:
        respuesta = self._pedir("POST", "/buscar", entrada.model_dump_json().encode(), "application/json")
        return ResultadoBusqueda.model_validate_json(respuesta)

    def subir(self, archivo: Path, titulo: str, coleccion_id: UUID, sha256: str) -> Documento:
        contenido = archivo.read_bytes()
        if hashlib.sha256(contenido).hexdigest() != sha256:
            raise AppError(CodigoError.DOCUMENTO_LECTURA, f"El hash del archivo {archivo.name} cambió.")
        borde = uuid4().hex
        partes = []
        for campo, valor in (("titulo", titulo), ("coleccion_id", str(coleccion_id))):
            partes.append(f'--{borde}\r\nContent-Disposition: form-data; name="{campo}"\r\n\r\n{valor}\r\n'.encode())
        partes.append(f'--{borde}\r\nContent-Disposition: form-data; name="archivo"; filename="{archivo.name}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode())
        partes.extend([contenido, f'\r\n--{borde}--\r\n'.encode()])
        respuesta = self._pedir("POST", "/documentos", b"".join(partes), f"multipart/form-data; boundary={borde}")
        return DetalleDocumento.model_validate_json(respuesta).documento

    def _pedir(self, metodo, ruta, contenido=None, tipo=None):
        cabeceras = {"X-API-Key": self._clave}
        if tipo:
            cabeceras["Content-Type"] = tipo
        peticion = Request(self.url + ruta, data=contenido, headers=cabeceras, method=metodo)
        try:
            with urlopen(peticion, timeout=180) as respuesta:
                return respuesta.read()
        except HTTPError as error:
            detalle = ErrorRespuesta.model_validate_json(error.read())
            raise AppError(CodigoError(detalle.codigo), detalle.detalle) from error
        except (URLError, TimeoutError) as error:
            raise AppError(CodigoError.UNKNOWN, "El servicio no respondió; revisar documentos existentes antes de repetir una carga.") from error
