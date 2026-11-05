from pathlib import Path
from uuid import UUID, uuid4

import numpy as np

from app.contratos import Consulta, DetalleDocumento, ModoBusqueda, ResultadoBusqueda
from app.embeddings import DIMENSION, Vectorizador
from app.errores import AppError, CodigoError
from app.extraccion import Extractor
from app.indexacion import DocumentoIndexado
from app.modelos import MotorOCR, fragmentar
from app.persistencia import BaseDocumental
from app.recuperacion import recuperar

COLECCION_DEMO = UUID("8c9fac40-7aee-4aa6-a08c-3e1ad438da91")


class MotorDocumental:
    def __init__(self, base: BaseDocumental, originales: Path):
        self.base = base
        self.originales = originales
        self.originales.mkdir(parents=True, exist_ok=True)
        self.extractor = Extractor(MotorOCR.TESSERACT)
        self.vectorizador = Vectorizador()

    def incorporar(self, archivo: Path, coleccion_id: UUID, titulo: str) -> DetalleDocumento:
        extraido = self.extractor.extraer(archivo)
        fragmentos = fragmentar(extraido)
        vectores = self.vectorizador.documentos([fragmento.texto for fragmento in fragmentos])
        if vectores.shape != (len(fragmentos), DIMENSION) or not np.isfinite(vectores).all():
            raise AppError(CodigoError.EMBEDDING_FORMATO, "No se pudieron generar vectores válidos.")
        indexado = DocumentoIndexado(uuid4(), coleccion_id, titulo, extraido, fragmentos, vectores)
        destino = self.originales / f"{indexado.id}{archivo.suffix.lower()}"
        guardado = False
        try:
            destino.write_bytes(archivo.read_bytes())
            self.base.incorporar(indexado)
            guardado = True
        finally:
            if not guardado:
                destino.unlink(missing_ok=True)
        return self.base.detalle(indexado.id)

    def buscar(self, consulta: Consulta) -> ResultadoBusqueda:
        vector = None
        if consulta.modo != ModoBusqueda.TEXTO:
            vector = self.vectorizador.consulta(consulta.texto)
        return recuperar(self.base, consulta, vector)

    def archivo(self, identificador: UUID) -> Path:
        documento = self.base.detalle(identificador).documento
        archivo = self.originales / f"{documento.id}.{documento.extension}"
        if not archivo.is_file():
            raise AppError(CodigoError.DOCUMENTO_NO_ENCONTRADO, "El original no está disponible.")
        return archivo

    def cargar_demo(self, corpus: Path) -> None:
        if not any(c.id == COLECCION_DEMO for c in self.base.colecciones()):
            self.base.crear_coleccion("Contratos ficticios", COLECCION_DEMO)
        with self.base.conectar() as conexion:
            existentes = conexion.execute(
                "SELECT nombre_original FROM documentos WHERE coleccion_id=%s", (COLECCION_DEMO,),
            ).fetchall()
        nombres = {fila["nombre_original"] for fila in existentes}
        for archivo in sorted(corpus.glob("*.pdf")):
            if archivo.name not in nombres:
                self.incorporar(archivo, COLECCION_DEMO, archivo.stem.replace("_", " "))
