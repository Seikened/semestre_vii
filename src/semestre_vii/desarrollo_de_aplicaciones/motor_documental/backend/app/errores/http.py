from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.contratos import ErrorRespuesta
from app.errores import AppError, CodigoError
from app.errores.handler import registrar

STATUS_HTTP = {
    CodigoError.ACCESO_DENEGADO: 401,
    CodigoError.ENTRADA_INVALIDA: 422,
    CodigoError.DOCUMENTO_FORMATO: 415,
    CodigoError.DOCUMENTO_VACIO: 422,
    CodigoError.DOCUMENTO_LECTURA: 422,
    CodigoError.DOCUMENTO_OCR: 422,
    CodigoError.DOCUMENTO_TAMANO: 413,
    CodigoError.DOCUMENTO_NO_ENCONTRADO: 404,
    CodigoError.COLECCION_NO_ENCONTRADA: 404,
    CodigoError.COLECCION_DUPLICADA: 409,
    CodigoError.BD_NO_DISPONIBLE: 503,
    CodigoError.LUNA_NO_CONFIGURADA: 503,
    CodigoError.LUNA_NO_DISPONIBLE: 503,
    CodigoError.LUNA_RESPUESTA_INVALIDA: 502,
}


def instalar_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def conocido(request: Request, error: AppError):
        codigo = registrar(error)
        status = STATUS_HTTP.get(codigo, 500)
        return respuesta(status, codigo, error.detalle)

    @app.exception_handler(RequestValidationError)
    async def validacion(request: Request, error: RequestValidationError):
        return respuesta(422, CodigoError.ENTRADA_INVALIDA, "Revisa los datos y formatos enviados.")

    @app.exception_handler(HTTPException)
    async def transporte(request: Request, error: HTTPException):
        return respuesta(error.status_code, CodigoError.RUTA_NO_ENCONTRADA, "La operación no está disponible.")

    @app.exception_handler(Exception)
    async def inesperado(request: Request, error: Exception):
        registrar(error)
        return respuesta(500, CodigoError.UNKNOWN, "No fue posible completar la operación.")


def respuesta(status: int, codigo: CodigoError, detalle: str) -> JSONResponse:
    error = ErrorRespuesta(codigo=codigo.value, detalle=detalle)
    return JSONResponse(status_code=status, content=error.model_dump())
