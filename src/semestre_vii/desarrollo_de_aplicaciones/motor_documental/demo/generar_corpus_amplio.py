import hashlib
import sys
from functools import partial
from io import BytesIO
from pathlib import Path
from random import Random

import pymupdf
from app.errores import AppError, CodigoError
from modelos_corpus import (
    CasoRecuperacion,
    ClausulaFicticia,
    CorpusFicticio,
    DocumentoFicticio,
    Formato,
    PaginaControl,
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

DESTINO = Path("data/desarrollo_de_aplicaciones/evaluacion_documental")
OBJETIVOS = (1, 2, 17, 91, 121, 122, 135, 152, 161, 170, 179, 190, 201, 202, 219, 237)
PROPIEDADES = ("Olmo", "Jacaranda", "Álamo", "Ópalo", "Nácar", "Ámbar", "Encino", "Sauce", "Magnolia", "Coral", "Abedul", "Cobre")
TIPOS = ("arrendamiento", "compraventa", "administración", "escritura simulada")
PAGINAS = (
    ("Identificación de las partes", "Objeto del acuerdo", "Descripción del inmueble", "Documentación e inventario"),
    ("Entrega material", "Uso autorizado", "Duración del acuerdo", "Revisión de instalaciones"),
    ("Importe principal", "Calendario de pagos", "Comprobantes y recibos", "Actualización de importes"),
    ("Límite de reparaciones", "Conservación ordinaria", "Servicios del inmueble", "Autorizaciones previas"),
    ("Constitución de garantía", "Devolución de garantía", "Deducciones documentadas", "Entrega de llaves"),
    ("Terminación anticipada", "Notificación de salida", "Cierre de obligaciones", "Acta de devolución"),
    ("Cesión a terceros", "Modificaciones interiores", "Reglas de convivencia", "Inspecciones programadas"),
    ("Inventario final", "Canal de comunicación", "Anexos del expediente", "Constancia de simulación"),
)
CONTEXTO = (
    "Las partes conservarán una copia idéntica de este apartado y cotejarán el folio antes de registrar cualquier movimiento. Una anotación aislada no modifica las condiciones pactadas en las demás secciones.",
    "La documentación de respaldo debe identificar la propiedad y describir el evento correspondiente. Se anotarán por separado los conceptos, sus importes y la fecha de recepción, evitando agrupar operaciones distintas bajo una sola referencia.",
    "La persona encargada del expediente verificará que el inventario coincida con el acta de entrega. Las diferencias se incorporarán como observaciones firmadas por las partes ficticias, sin sustituir la versión original del documento.",
    "Toda modificación de esta condición requiere un anexo escrito que mencione expresamente la cláusula afectada. Mientras no exista ese anexo, se conserva el contenido de este expediente y se rechazan instrucciones verbales contradictorias.",
)


def generar(destino: Path) -> CorpusFicticio:
    archivos = destino / "archivos"
    archivos.mkdir(parents=True, exist_ok=True)
    documentos = []
    casos = []
    for numero in range(1, 241):
        documento = construir_documento(numero)
        ruta = archivos / documento.archivo
        if documento.formato is Formato.TXT:
            texto = texto_documento(documento)
            ruta.write_text(texto, encoding="utf-8")
        else:
            crear_pdf(documento, ruta)
        documento.sha256 = hashlib.sha256(ruta.read_bytes()).hexdigest()
        documentos.append(documento)
        if numero in OBJETIVOS:
            casos.extend(crear_casos(documento))
        if numero % 20 == 0:
            print(f"Generados {numero}/240 documentos", flush=True)
    corpus = CorpusFicticio(version="2", documentos=documentos, casos=casos)
    (destino / "corpus.json").write_text(corpus.model_dump_json(indent=2), encoding="utf-8")
    print(f"Corpus: {len(documentos)} documentos, {sum(len(d.paginas) for d in documentos)} páginas lógicas, {len(casos)} casos.")
    return corpus


def construir_documento(numero: int) -> DocumentoFicticio:
    azar = Random(20261102 + numero)
    folio = f"SIM{numero:04d}"
    if numero <= 120:
        formato = Formato.DIGITAL
    elif numero <= 160:
        formato = Formato.ESCANEADO
    elif numero <= 200:
        formato = Formato.MIXTO
    else:
        formato = Formato.TXT
    tipo = TIPOS[(numero - 1) % len(TIPOS)]
    inmueble = f"Unidad {PROPIEDADES[(numero - 1) % len(PROPIEDADES)]} {numero:03d}"
    cedente = f"Persona Cedente {numero:03d} del Archivo Imaginario"
    receptor = f"Persona Receptora {(numero * 7) % 241:03d} de Puerto Inventado"
    especiales = {1: "Villa Jacaranda", 121: "Departamento Ópalo", 161: "Bodega Nácar", 201: "Local Ámbar"}
    if numero in especiales:
        inmueble = especiales[numero]
        cedente, receptor = "Fernando León Franco", "Fabián León Franco"
    if numero in (2, 3, 4):
        inmueble = ("Villa Jacaranda Norte", "Villa Jacaranda Sur", "Villa Jacaranda Anexo")[numero - 2]
        cedente, receptor = "Fernando León Franco", "Fabián León Franco"
        if numero == 3:
            cedente, receptor = receptor, cedente
    variante = "normal"
    if formato is Formato.MIXTO and numero % 10 == 0:
        variante = "encabezado_digital_cuerpo_imagen"
    elif formato is Formato.ESCANEADO and numero % 5 == 0:
        variante = "escaneo_110dpi"
    importe = azar.randrange(80, 900) * 125
    reparaciones = azar.randrange(15, 70) * 100
    devolucion = azar.randrange(11, 70)
    aviso = azar.randrange(15, 90)
    if numero == 1:
        importe, reparaciones, devolucion, aviso = 27850, 4300, 37, 46
    titulo = f"{folio} | {tipo.capitalize()} ficticio | {inmueble}"
    paginas = []
    for indice, titulos in enumerate(PAGINAS, 1):
        clausulas = []
        for posicion, encabezado in enumerate(titulos):
            identificador = (indice - 1) * 4 + posicion + 1
            frase = contenido_clausula(identificador, importe, reparaciones, devolucion, aviso, numero)
            if identificador == 1:
                frase = f"La parte cedente es {cedente} y la parte receptora es {receptor}. Actúan exclusivamente como personajes de una simulación, sin representar una operación jurídica real."
            contexto = CONTEXTO[(numero + identificador) % len(CONTEXTO)]
            texto = f"{frase} Este apartado corresponde a {inmueble}, folio {folio}. {contexto} La referencia de control es FICT-{numero:04d}-{identificador:02d}."
            clausulas.append(ClausulaFicticia(numero=identificador, titulo=encabezado, texto=texto))
        metodo = "texto"
        if formato is Formato.ESCANEADO or formato is Formato.MIXTO and indice % 2 == 0:
            metodo = "ocr"
        paginas.append(PaginaControl(numero=indice, metodo=metodo, clausulas=clausulas))
    if formato is Formato.TXT:
        paginas = [PaginaControl(numero=1, metodo="texto", clausulas=[c for p in paginas for c in p.clausulas])]
    return DocumentoFicticio(
        folio=folio, titulo=titulo, archivo=f"{folio}_{formato.value}.{'txt' if formato is Formato.TXT else 'pdf'}",
        formato=formato, variante=variante, inmueble=inmueble, cedente=cedente, receptor=receptor, paginas=paginas,
    )


def contenido_clausula(numero, importe, reparaciones, devolucion, aviso, contrato):
    match numero:
        case 1:
            return "Las partes actúan únicamente como personajes de una simulación académica, sin representar una operación jurídica real."
        case 9:
            return f"El importe principal acordado es de {importe} pesos ficticios. No incluye conceptos adicionales que no consten por escrito."
        case 13:
            return f"El límite de reparaciones sin autorización adicional es de {reparaciones} pesos ficticios por evento. Un gasto mayor requiere aprobación escrita."
        case 18:
            return f"La garantía se devuelve dentro de {devolucion} días naturales después de entregar las llaves y firmar el inventario, descontando solo daños documentados."
        case 21:
            return f"La terminación anticipada requiere aviso con {aviso} días naturales y una compensación de {(contrato % 3) + 1} mensualidades ficticias. No basta abandonar el inmueble."
        case 25:
            return "No se permite ceder el uso del inmueble a terceros sin autorización escrita. Una visita temporal no constituye una cesión del acuerdo."
        case 32:
            return "Este documento es enteramente ficticio, carece de firmas reales y no acredita propiedad, deuda ni obligaciones de persona alguna."
        case _:
            condiciones = (
                "La revisión se realizará mediante inventario comparativo y acta de observaciones, con copia para ambas partes ficticias.",
                "Se conservarán los comprobantes relacionados con esta condición y se registrará su recepción en el expediente de la propiedad.",
                "Los avisos se entregarán por escrito con referencia al inmueble. Los acuerdos posteriores deberán identificar expresamente el punto que modifican.",
                "La entrega de bienes se cotejará con el anexo de conservación. Las partes distinguirán desgaste ordinario, daños y mejoras previamente autorizadas.",
            )
            return condiciones[(numero + contrato) % len(condiciones)]


def crear_casos(documento: DocumentoFicticio) -> list[CasoRecuperacion]:
    preguntas = {
        9: "¿Cuál es el importe principal acordado",
        13: "¿Hasta cuánto se pueden autorizar reparaciones sin pedir otra aprobación",
        18: "¿En cuántos días regresan la garantía después de entregar las llaves",
        21: "¿Qué aviso y compensación se requieren para terminar antes de tiempo",
    }
    if documento.folio in {"SIM0001", "SIM0121", "SIM0161", "SIM0201"}:
        preguntas[1] = "¿Qué documento identifica a Fernando León Franco como cedente y a Fabián León Franco como receptor"
    casos = []
    for pagina in documento.paginas:
        for clausula in pagina.clausulas:
            if clausula.numero in preguntas:
                cita = clausula.texto.split(" Este apartado corresponde")[0]
                casos.append(CasoRecuperacion(
                    id=f"{documento.folio}-C{clausula.numero:02d}", archivo=documento.archivo,
                    formato=documento.formato, pagina=pagina.numero, clausula=clausula.numero, cita=cita,
                    natural=f"{preguntas[clausula.numero]} para {documento.inmueble} en el expediente {documento.folio}?",
                    libre=f"{preguntas[clausula.numero]} para {documento.inmueble}?",
                    precisa=f'{documento.folio} "{clausula.titulo}"',
                ))
    return casos


def texto_documento(documento: DocumentoFicticio) -> str:
    partes = ["DOCUMENTO FICTICIO. SIN VALIDEZ LEGAL.", documento.titulo,
              f"Partes ficticias de este acto: {documento.cedente} y {documento.receptor}."]
    for pagina in documento.paginas:
        for clausula in pagina.clausulas:
            partes.extend([f"Cláusula {clausula.numero}. {clausula.titulo}.", clausula.texto])
    return "\n\n".join(partes)


def crear_pdf(documento: DocumentoFicticio, ruta: Path) -> None:
    cuerpo = ParagraphStyle("cuerpo", fontName="Helvetica", fontSize=10.2, leading=14, spaceAfter=10)
    titulo = ParagraphStyle("titulo", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#254c37"), spaceAfter=8)
    subtitulo = ParagraphStyle("subtitulo", parent=cuerpo, fontName="Helvetica-Bold", spaceAfter=4)
    historia = []
    for pagina in documento.paginas:
        if pagina.numero > 1:
            historia.append(PageBreak())
        historia.extend([
            Paragraph("DOCUMENTO FICTICIO. SIN VALIDEZ LEGAL.", subtitulo),
            Paragraph(documento.titulo, titulo),
            Paragraph(f"Partes ficticias: {documento.cedente} y {documento.receptor}.", cuerpo),
            Spacer(1, 8),
        ])
        for clausula in pagina.clausulas:
            historia.extend([Paragraph(f"Cláusula {clausula.numero}. {clausula.titulo}", subtitulo), Paragraph(clausula.texto, cuerpo)])
        historia.append(Paragraph(f"Página {pagina.numero} de 8. Personas, importes y operaciones de este acto son inventados.", cuerpo))
    memoria = BytesIO()
    SimpleDocTemplate(memoria, pagesize=A4, rightMargin=48, leftMargin=48, topMargin=42, bottomMargin=35).build(historia, canvasmaker=partial(Canvas, invariant=1))
    with pymupdf.open(stream=memoria.getvalue(), filetype="pdf") as digital, pymupdf.open() as resultado:
        if len(digital) != 8:
            raise AppError(CodigoError.DOCUMENTO_FORMATO, "El generador debe producir exactamente ocho páginas por PDF.")
        for indice, pagina in enumerate(digital, 1):
            escanear = documento.formato is Formato.ESCANEADO or documento.formato is Formato.MIXTO and indice % 2 == 0
            if not escanear:
                resultado.insert_pdf(digital, from_page=indice - 1, to_page=indice - 1)
                continue
            nueva = resultado.new_page(width=pagina.rect.width, height=pagina.rect.height)
            dpi = 110 if documento.variante == "escaneo_110dpi" else 160
            if documento.variante == "encabezado_digital_cuerpo_imagen":
                region = pymupdf.Rect(40, 130, pagina.rect.width - 40, pagina.rect.height - 30)
                imagen = pagina.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=region)
                nueva.insert_image(region, stream=imagen.tobytes("png"))
                cabecera = f"DOCUMENTO FICTICIO. SIN VALIDEZ LEGAL.\n{documento.titulo}\nPartes ficticias: {documento.cedente} y {documento.receptor}."
                nueva.insert_textbox(pymupdf.Rect(48, 42, pagina.rect.width - 48, 125), cabecera, fontsize=11, fontname="helv")
            else:
                imagen = pagina.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
                nueva.insert_image(nueva.rect, stream=imagen.tobytes("png"))
        resultado.set_metadata({"title": documento.titulo, "subject": "Contrato totalmente ficticio para evaluar recuperación, sin validez legal"})
        resultado.save(ruta, deflate=True, no_new_id=True)


if __name__ == "__main__":
    generar(Path(sys.argv[1]) if len(sys.argv) > 1 else DESTINO)
