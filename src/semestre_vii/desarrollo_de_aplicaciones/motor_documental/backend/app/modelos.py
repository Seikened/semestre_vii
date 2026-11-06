from enum import StrEnum

from pydantic import BaseModel, Field


class MetodoExtraccion(StrEnum):
    TEXTO = "texto"
    OCR = "ocr"


class MotorOCR(StrEnum):
    RAPIDOCR = "rapidocr"
    TESSERACT = "tesseract"


class PaginaExtraida(BaseModel):
    numero: int = Field(ge=1)
    texto: str = Field(min_length=1)
    metodo: MetodoExtraccion


class DocumentoExtraido(BaseModel):
    nombre: str
    paginas: list[PaginaExtraida] = Field(min_length=1)


class FragmentoExtraido(BaseModel):
    pagina: int = Field(ge=1)
    orden: int = Field(ge=0)
    texto: str = Field(min_length=1)


def fragmentar(documento: DocumentoExtraido, limite: int = 900) -> list[FragmentoExtraido]:
    fragmentos = []
    for pagina in documento.paginas:
        orden = 0
        palabras = pagina.texto.split()
        inicio = 0
        while inicio < len(palabras):
            fin = inicio
            longitud = 0
            while fin < len(palabras) and longitud + len(palabras[fin]) < limite:
                longitud += len(palabras[fin]) + 1
                fin += 1
            if fin == inicio:
                fin += 1
            fragmentos.append(
                FragmentoExtraido(
                    pagina=pagina.numero,
                    orden=orden,
                    texto=" ".join(palabras[inicio:fin]),
                )
            )
            inicio = fin
            orden += 1
    return fragmentos
