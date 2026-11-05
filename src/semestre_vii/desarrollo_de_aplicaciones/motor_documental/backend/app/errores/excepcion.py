from app.errores.catalogo import CodigoError, Severidad


class AppError(Exception):
    def __init__(self, codigo: CodigoError, detalle: str, severidad: Severidad = Severidad.ERROR):
        self.codigo = codigo
        self.detalle = detalle
        self.severidad = severidad
        super().__init__(f"[{codigo.value}] {detalle}")
