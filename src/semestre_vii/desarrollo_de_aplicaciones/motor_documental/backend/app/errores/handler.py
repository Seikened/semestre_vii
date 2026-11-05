import logging

from app.errores import AppError, CodigoError, Severidad


def registrar(error: Exception) -> CodigoError:
    if isinstance(error, AppError):
        codigo = error.codigo
        severidad = error.severidad
    else:
        codigo = CodigoError.UNKNOWN
        severidad = Severidad.ERROR
    logging.getLogger("motor").log(getattr(logging, severidad.value), "%s (%s)", codigo, type(error).__name__)
    return codigo
