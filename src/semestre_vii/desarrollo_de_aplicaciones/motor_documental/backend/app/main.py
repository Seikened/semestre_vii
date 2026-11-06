import os
from contextlib import asynccontextmanager
from hmac import compare_digest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, File, Form, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader

from app.chat import ChatDocumental
from app.chat_contratos import ConsultaChat, RespuestaChat
from app.configuracion import Configuracion
from app.contratos import (
    Coleccion,
    Consulta,
    DetalleDocumento,
    Documento,
    EditarDocumento,
    ErrorRespuesta,
    NuevaColeccion,
    ResultadoBusqueda,
    Salud,
    Titulo,
)
from app.embeddings import DIMENSION, MODELO
from app.errores import AppError, CodigoError
from app.errores.http import instalar_handlers
from app.motor import MotorDocumental
from app.persistencia import BaseDocumental

MAX_ARCHIVO = 10 * 1024 * 1024
cabecera_clave = APIKeyHeader(name="X-API-Key", auto_error=False)


@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    configuracion = Configuracion.cargar()
    base = BaseDocumental(configuracion.conexion)
    motor = MotorDocumental(base, configuracion.originales)
    motor.cargar_demo(configuracion.corpus)
    app.state.motor = motor
    app.state.configuracion = configuracion
    app.state.chat = ChatDocumental(motor, configuracion.luna_api_key)
    try:
        yield
    finally:
        app.state.chat.cerrar()


app = FastAPI(
    title="Motor documental inmobiliario", version="0.1.0", lifespan=ciclo_vida,
    description="Extracción y búsqueda de contratos ficticios, con chat opcional de Luna y fuentes verificables.",
)
app.add_middleware(
    CORSMiddleware, allow_origins=[os.getenv("ORIGEN_WEB", "http://localhost:3000")],
    allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["X-API-Key", "Content-Type"],
)
instalar_handlers(app)


def motor_actual(request: Request) -> MotorDocumental:
    return request.app.state.motor


def autorizar(request: Request, clave: Annotated[str | None, Depends(cabecera_clave)]) -> None:
    esperada = request.app.state.configuracion.api_key
    if clave is None or not compare_digest(clave.encode(), esperada.encode()):
        raise AppError(CodigoError.ACCESO_DENEGADO, "Se requiere una API key válida.")


Motor = Annotated[MotorDocumental, Depends(motor_actual)]
api = APIRouter(
    dependencies=[Depends(autorizar)],
    responses={status: {"model": ErrorRespuesta, "content": {"application/json": {"example": {
        "codigo": codigo, "detalle": detalle,
    }}}} for status, codigo, detalle in (
        (401, "ACCESO_DENEGADO", "Se requiere una API key válida."),
        (404, "DOCUMENTO_NO_ENCONTRADO", "El documento no está disponible."),
        (409, "COLECCION_DUPLICADA", "La colección ya existe."),
        (413, "DOCUMENTO_TAMANO", "El archivo supera el límite de 10 MiB."),
        (415, "DOCUMENTO_FORMATO", "Solo se admiten PDF y TXT UTF-8."),
        (422, "ENTRADA_INVALIDA", "Revisa los datos y formatos enviados."),
        (500, "UNKNOWN", "No fue posible completar la operación."),
        (503, "BD_NO_DISPONIBLE", "La base de datos no está disponible."),
    )},
)


@app.get("/salud", response_model=Salud, tags=["Servicio"], summary="Comprobar disponibilidad",
         responses={503: {"model": ErrorRespuesta}})
def salud(motor: Motor):
    with motor.base.conectar() as conexion:
        conexion.execute("SELECT 1")
    return Salud(modelo=MODELO, dimension=DIMENSION)


@api.get("/colecciones", response_model=list[Coleccion], tags=["Biblioteca"])
def colecciones(motor: Motor):
    """Lista los grupos disponibles para organizar contratos."""
    return motor.base.colecciones()


@api.post("/colecciones", response_model=Coleccion, status_code=201, tags=["Biblioteca"])
def crear_coleccion(entrada: NuevaColeccion, motor: Motor):
    """Crea una colección con nombre único; rechaza nombres vacíos o repetidos."""
    return motor.base.crear_coleccion(entrada.nombre)


@api.get("/documentos", response_model=list[Documento], tags=["Documentos"])
def documentos(motor: Motor, coleccion_id: UUID | None = None):
    """Lista solo documentos activos; permite restringir la colección."""
    return motor.base.documentos(coleccion_id)


@api.post("/documentos", response_model=DetalleDocumento, status_code=201, tags=["Documentos"])
def incorporar_documento(
    motor: Motor, archivo: Annotated[UploadFile, File(description="PDF o TXT UTF-8, máximo 10 MiB")],
    coleccion_id: Annotated[UUID, Form(examples=["8c9fac40-7aee-4aa6-a08c-3e1ad438da91"])],
    titulo: Annotated[Titulo, Form(examples=["Contrato ficticio de arrendamiento"])],
):
    """Extrae cada página, aplica OCR si hace falta y guarda fragmentos y vectores atómicamente."""
    nombre = Path((archivo.filename or "").replace("\\", "/")).name
    if not nombre or len(nombre) > 200:
        raise AppError(CodigoError.ENTRADA_INVALIDA, "El nombre del archivo debe tener hasta 200 caracteres.")
    if Path(nombre).suffix.lower() not in (".pdf", ".txt"):
        raise AppError(CodigoError.DOCUMENTO_FORMATO, "Solo se admiten PDF y TXT UTF-8.")
    contenido = archivo.file.read(MAX_ARCHIVO + 1)
    if len(contenido) > MAX_ARCHIVO:
        raise AppError(CodigoError.DOCUMENTO_TAMANO, "El archivo supera el límite de 10 MiB.")
    with TemporaryDirectory() as temporal:
        ruta = Path(temporal) / nombre
        ruta.write_bytes(contenido)
        return motor.incorporar(ruta, coleccion_id, titulo)


@api.get("/documentos/{identificador}", response_model=DetalleDocumento, tags=["Documentos"])
def detalle_documento(identificador: UUID, motor: Motor):
    """Devuelve metadatos, texto y método de extracción de cada página."""
    return motor.base.detalle(identificador)


@api.patch("/documentos/{identificador}", response_model=DetalleDocumento, tags=["Documentos"])
def editar_documento(identificador: UUID, entrada: EditarDocumento, motor: Motor):
    """Cambia título o colección; los vectores y el original se conservan."""
    return motor.base.editar(identificador, entrada)


@api.delete("/documentos/{identificador}", status_code=204, tags=["Documentos"])
def retirar_documento(identificador: UUID, motor: Motor):
    """Aplica baja lógica y excluye el documento de búsqueda, detalle y descarga."""
    motor.base.retirar(identificador)
    return Response(status_code=204)


@api.get("/documentos/{identificador}/archivo", response_class=FileResponse, tags=["Documentos"],
         responses={200: {"description": "Original PDF o TXT", "content": {
             formato: {"schema": {"type": "string", "format": "binary"}}
             for formato in ("application/pdf", "text/plain")
         }}})
def archivo_original(identificador: UUID, motor: Motor):
    """Entrega el original disponible; no acepta rutas del sistema de archivos."""
    ruta = motor.archivo(identificador)
    return FileResponse(ruta, media_type="application/pdf" if ruta.suffix == ".pdf" else "text/plain")


@api.post("/buscar", response_model=ResultadoBusqueda, tags=["Recuperación"])
def buscar(entrada: Consulta, motor: Motor):
    """Busca por texto, similitud coseno o fusión RRF; devuelve pasajes y procedencia sin un LLM."""
    return motor.buscar(entrada)


@api.post("/chat", response_model=RespuestaChat, tags=["Conversación"], responses={
    502: {"model": ErrorRespuesta, "description": "La respuesta de Luna no se pudo validar."},
    503: {"model": ErrorRespuesta, "description": "Luna no está configurada o no está disponible."},
})
def conversar(entrada: ConsultaChat, request: Request):
    """Luna busca en el motor local y responde con fuentes; requiere clave privada del proveedor."""
    return request.app.state.chat.conversar(entrada)


app.include_router(api)
