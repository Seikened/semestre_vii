from pathlib import Path

import pymupdf
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.exceptions import ConversionError

from app.errores import AppError, CodigoError
from app.modelos import DocumentoExtraido, MetodoExtraccion, MotorOCR, PaginaExtraida

OCR_IDIOMA = "iso:es"
OCR_TAMANO = "small"


class Extractor:
    def __init__(self, motor: MotorOCR = MotorOCR.RAPIDOCR):
        self._ocr = None
        self.motor = motor

    def extraer(self, archivo: Path) -> DocumentoExtraido:
        if archivo.suffix.lower() == ".txt":
            try:
                texto = archivo.read_text(encoding="utf-8").strip()
            except UnicodeDecodeError as error:
                raise AppError(
                    CodigoError.DOCUMENTO_FORMATO, "El archivo TXT debe usar UTF-8."
                ) from error
            if not texto:
                raise AppError(CodigoError.DOCUMENTO_VACIO, "El documento no contiene texto.")
            pagina = PaginaExtraida(numero=1, texto=texto, metodo=MetodoExtraccion.TEXTO)
            return DocumentoExtraido(nombre=archivo.name, paginas=[pagina])
        if archivo.suffix.lower() != ".pdf":
            raise AppError(CodigoError.DOCUMENTO_FORMATO, "Solo se admiten PDF y TXT UTF-8.")
        return self._extraer_pdf(archivo)

    def _extraer_pdf(self, archivo: Path) -> DocumentoExtraido:
        paginas = []
        try:
            documento = pymupdf.open(archivo)
        except (pymupdf.FileDataError, pymupdf.EmptyFileError) as error:
            raise AppError(
                CodigoError.DOCUMENTO_LECTURA, "El archivo PDF no se puede leer."
            ) from error
        with documento:
            if not documento.is_pdf:
                raise AppError(
                    CodigoError.DOCUMENTO_FORMATO, "El contenido del archivo no es un PDF."
                )
            if documento.needs_pass:
                raise AppError(
                    CodigoError.DOCUMENTO_LECTURA, "El PDF está protegido con contraseña."
                )
            for indice, pagina in enumerate(documento):
                texto = pagina.get_text(sort=True).strip()
                metodo = MetodoExtraccion.TEXTO
                solo_imagen = len(texto) < 60
                imagen_grande = any(
                    (pymupdf.Rect(imagen["bbox"]) & pagina.rect).get_area()
                    >= pagina.rect.get_area() / 4
                    for imagen in pagina.get_image_info()
                )
                if solo_imagen or imagen_grande:
                    texto = self._reconocer(archivo, pagina, indice + 1, completo=solo_imagen)
                    metodo = MetodoExtraccion.OCR
                if not texto.strip():
                    raise AppError(
                        CodigoError.DOCUMENTO_VACIO,
                        f"La página {indice + 1} no contiene texto utilizable.",
                    )
                paginas.append(PaginaExtraida(numero=indice + 1, texto=texto, metodo=metodo))
        if not paginas:
            raise AppError(CodigoError.DOCUMENTO_VACIO, "El documento no contiene páginas.")
        return DocumentoExtraido(nombre=archivo.name, paginas=paginas)

    def _reconocer(self, archivo: Path, pagina: pymupdf.Page, numero: int, completo: bool = True) -> str:
        if self.motor is MotorOCR.TESSERACT:
            try:
                texto_ocr = pagina.get_textpage_ocr(language="spa+eng", dpi=200, full=completo)
                return pagina.get_text(textpage=texto_ocr, sort=True).strip()
            except RuntimeError as error:
                raise AppError(
                    CodigoError.DOCUMENTO_OCR,
                    f"No se pudo reconocer la página {numero} con Tesseract.",
                ) from error
        if self._ocr is None:
            opciones = PdfPipelineOptions(
                do_table_structure=False,
                ocr_options=RapidOcrOptions(
                    lang=[OCR_IDIOMA], model_size=OCR_TAMANO, force_full_page_ocr=True
                ),
            )
            self._ocr = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=opciones),
                }
            )
        try:
            resultado = self._ocr.convert(archivo, page_range=(numero, numero))
        except ConversionError as error:
            raise AppError(
                CodigoError.DOCUMENTO_OCR, f"No se pudo procesar la página {numero} mediante OCR."
            ) from error
        return resultado.document.export_to_markdown().strip()
