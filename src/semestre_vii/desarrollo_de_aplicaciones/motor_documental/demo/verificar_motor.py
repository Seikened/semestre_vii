"""Ejecuta extracción y recuperación reales sin conectar un LLM ni una base de datos."""

from datetime import datetime
from importlib.metadata import version
from os import environ
from pathlib import Path
from time import perf_counter
from unicodedata import normalize
from zoneinfo import ZoneInfo

import numpy as np
from app.embeddings import DIMENSION, MODELO, REVISION, Vectorizador
from app.errores import AppError, CodigoError
from app.extraccion import OCR_IDIOMA, OCR_TAMANO, Extractor
from app.modelos import MetodoExtraccion, MotorOCR, fragmentar
from pydantic import BaseModel


class Fuente(BaseModel):
    archivo: str
    pagina: int
    texto: str
    metodo: MetodoExtraccion


class Caso(BaseModel):
    consulta: str
    archivo: str
    pagina: int


class Resultado(BaseModel):
    caso: Caso
    primeros: list[Fuente]
    posicion_esperada: int | None
    segundos: float


class ControlTexto(BaseModel):
    archivo: str
    pagina: int
    frase: str
    recuperada: bool = False


class Informe(BaseModel):
    fecha: str
    modelo: str
    revision: str
    dimension: int
    docling: str
    ocr_idioma: str
    ocr_tamano: str | None
    ocr_motor: MotorOCR
    documentos: int
    paginas_texto: int
    paginas_ocr: int
    fragmentos: int
    recall_5: float
    resultados: list[Resultado]
    controles_texto: list[ControlTexto]


CASOS = [
    Caso(
        consulta="¿Cuándo se devuelve el depósito de la casa Aurora?",
        archivo="FIC-001_digital.pdf",
        pagina=2,
    ),
    Caso(
        consulta="¿Qué multa corresponde si se entrega tarde el departamento Bruma?",
        archivo="FIC-002_escaneado.pdf",
        pagina=2,
    ),
    Caso(
        consulta="¿Qué debo pagar si desocupo antes de tiempo el local Cedro?",
        archivo="FIC-003_mixto.pdf",
        pagina=2,
    ),
    Caso(
        consulta="¿Hasta qué monto puede autorizar reparaciones el administrador de Duna?",
        archivo="FIC-004_digital.pdf",
        pagina=2,
    ),
    Caso(
        consulta="¿Se recupera el apartado de Estela si hay problemas con los papeles de propiedad?",
        archivo="FIC-005_escaneado.pdf",
        pagina=2,
    ),
    Caso(
        consulta="¿En qué horario puedo entrar a la oficina Faro?",
        archivo="FIC-006_mixto.pdf",
        pagina=2,
    ),
]


CONTROLES = [
    ControlTexto(archivo="FIC-002_escaneado.pdf", pagina=1, frase="veinte por ciento al firmar"),
    ControlTexto(archivo="FIC-002_escaneado.pdf", pagina=2, frase="1500 pesos ficticios por día"),
    ControlTexto(
        archivo="FIC-002_escaneado.pdf",
        pagina=2,
        frase="El mobiliario no forma parte de la operación",
    ),
    ControlTexto(
        archivo="FIC-003_mixto.pdf", pagina=2, frase="sesenta días naturales de anticipación"
    ),
    ControlTexto(archivo="FIC-003_mixto.pdf", pagina=2, frase="dos mensualidades de renta"),
    ControlTexto(
        archivo="FIC-005_escaneado.pdf", pagina=1, frase="superficie de 320 metros cuadrados"
    ),
    ControlTexto(
        archivo="FIC-005_escaneado.pdf", pagina=2, frase="el apartado se devuelve íntegro"
    ),
    ControlTexto(archivo="FIC-006_mixto.pdf", pagina=2, frase="cuarenta y cinco días"),
]


def normalizar(texto: str) -> str:
    return "".join(c for c in normalize("NFKD", texto.casefold()) if c.isalnum())


def verificar(destino: Path, motor: MotorOCR) -> Informe:
    extractor = Extractor(motor)
    if motor is MotorOCR.TESSERACT:
        idioma, tamano = "spa+eng", None
    else:
        idioma, tamano = OCR_IDIOMA, OCR_TAMANO
    fuentes = []
    nativos = 0
    ocr = 0
    archivos = sorted((Path(__file__).parent / "contratos").glob("*.pdf"))
    for archivo in archivos:
        documento = extractor.extraer(archivo)
        metodos = {p.numero: p.metodo for p in documento.paginas}
        nativos += sum(p.metodo == MetodoExtraccion.TEXTO for p in documento.paginas)
        ocr += sum(p.metodo == MetodoExtraccion.OCR for p in documento.paginas)
        for fragmento in fragmentar(documento):
            fuentes.append(
                Fuente(
                    archivo=archivo.name,
                    pagina=fragmento.pagina,
                    texto=fragmento.texto,
                    metodo=metodos[fragmento.pagina],
                )
            )
        print(
            f"Extraído: {archivo.name}, métodos: {[p.metodo.value for p in documento.paginas]}",
            flush=True,
        )
    vectorizador = Vectorizador()
    vectores = vectorizador.documentos([f.texto for f in fuentes])
    if vectores.shape != (len(fuentes), DIMENSION) or not np.isfinite(vectores).all():
        raise AppError(
            CodigoError.EMBEDDING_FORMATO, "La representación vectorial no tiene la forma esperada."
        )
    resultados = []
    for caso in CASOS:
        inicio = perf_counter()
        consulta = vectorizador.consulta(caso.consulta)
        orden = np.argsort(-(vectores @ consulta))[:5]
        primeros = [fuentes[int(i)] for i in orden]
        posicion = next(
            (
                i + 1
                for i, fuente in enumerate(primeros)
                if fuente.archivo == caso.archivo and fuente.pagina == caso.pagina
            ),
            None,
        )
        resultados.append(
            Resultado(
                caso=caso,
                primeros=primeros,
                posicion_esperada=posicion,
                segundos=round(perf_counter() - inicio, 4),
            )
        )
        print(f"Consulta: {caso.consulta} | fuente esperada en posición {posicion}", flush=True)
    aciertos = sum(r.posicion_esperada is not None for r in resultados)
    informe = Informe(
        fecha=datetime.now(ZoneInfo("America/Mexico_City")).isoformat(),
        modelo=MODELO,
        revision=REVISION,
        dimension=DIMENSION,
        docling=version("docling"),
        ocr_idioma=idioma,
        ocr_tamano=tamano,
        ocr_motor=motor,
        documentos=len(archivos),
        paginas_texto=nativos,
        paginas_ocr=ocr,
        fragmentos=len(fuentes),
        recall_5=aciertos / len(resultados),
        resultados=resultados,
        controles_texto=[
            control.model_copy(
                update={
                    "recuperada": normalizar(control.frase)
                    in normalizar(
                        " ".join(
                            f.texto
                            for f in fuentes
                            if f.archivo == control.archivo and f.pagina == control.pagina
                        )
                    )
                }
            )
            for control in CONTROLES
        ],
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(informe.model_dump_json(indent=2), encoding="utf-8")
    np.savez_compressed(destino.with_suffix(".npz"), vectores=vectores)
    print(f"Recall@5 del corpus ficticio: {informe.recall_5:.3f}. Informe: {destino}")
    print(
        f"Controles de texto OCR: {sum(c.recuperada for c in informe.controles_texto)}/{len(CONTROLES)}"
    )
    return informe


if __name__ == "__main__":
    proyecto = Path(__file__).resolve().parents[1]
    motor = MotorOCR(environ.get("MOTOR_OCR", "rapidocr"))
    sufijo = motor.value
    if motor is MotorOCR.RAPIDOCR:
        sufijo = f"{sufijo}_{OCR_TAMANO}"
    destino = proyecto / "docs" / "07_Evidencias" / f"recuperacion_{sufijo}.json"
    verificar(destino, motor)
