"""Genera seis contratos ficticios en PDF digital, escaneado y mixto."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import pymupdf
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


@dataclass(frozen=True)
class Contrato:
    folio: str
    titulo: str
    formato: str
    clausulas: tuple[str, ...]


CONTRATOS = (
    Contrato(
        "FIC-001",
        "Arrendamiento de vivienda Aurora",
        "digital",
        (
            "Partes: Persona Alfa y Persona Beta, identidades inventadas. Inmueble: casa Aurora, calle Imaginaria 101, ciudad ficticia Puerto Claro.",
            "Renta mensual: 12500 pesos ficticios, pagaderos durante los primeros cinco días de cada mes. Plazo: doce meses desde el 1 de enero de 2027.",
            "Depósito en garantía: 12500 pesos ficticios. Se devuelve dentro de treinta días naturales después de entregar la vivienda, descontando daños documentados.",
            "Mascotas: se permite un gato doméstico. Queda prohibido subarrendar la vivienda sin autorización escrita.",
        ),
    ),
    Contrato(
        "FIC-002",
        "Compraventa de departamento Bruma",
        "escaneado",
        (
            "Partes: Persona Gamma y Persona Delta, identidades inventadas. Inmueble: departamento Bruma, edificio ficticio Nube, unidad B-12.",
            "Precio: 2400000 pesos ficticios. Anticipo: veinte por ciento al firmar; saldo: ochenta por ciento al formalizar la operación.",
            "Entrega de posesión: 15 de febrero de 2027. Si la parte vendedora retrasa la entrega, la penalización será de 1500 pesos ficticios por día, hasta veinte días.",
            "El mobiliario no forma parte de la operación. Se incluyen dos espacios de estacionamiento identificados como E-07 y E-08.",
        ),
    ),
    Contrato(
        "FIC-003",
        "Arrendamiento de local Cedro",
        "mixto",
        (
            "Partes: Persona Épsilon y Persona Zeta, identidades inventadas. Inmueble: local comercial Cedro, plaza ficticia Horizonte, local L-04.",
            "Renta mensual: 18000 pesos ficticios. El uso autorizado es una librería. El plazo es de veinticuatro meses a partir del 1 de marzo de 2027.",
            "Salida anticipada: debe avisarse con sesenta días naturales de anticipación. La penalización equivale a dos mensualidades de renta.",
            "Mantenimiento: 900 pesos ficticios mensuales por cuenta del arrendatario. La renovación requiere acuerdo escrito treinta días antes del vencimiento.",
        ),
    ),
    Contrato(
        "FIC-004",
        "Administración de propiedad Duna",
        "digital",
        (
            "Partes: Persona Eta y Administración Umbral Ficticia. Inmueble: casa Duna, avenida Inventada 404, ciudad ficticia Puerto Claro.",
            "Comisión de administración: ocho por ciento de la renta efectivamente cobrada. El informe de ingresos y gastos se entrega el día diez de cada mes.",
            "Reparaciones: el administrador puede autorizar gastos hasta 3000 pesos ficticios por evento. Los montos superiores requieren autorización escrita del propietario.",
            "Rescisión: cualquiera de las partes puede terminar el servicio con treinta días naturales de aviso. La entrega de llaves se registra mediante inventario.",
        ),
    ),
    Contrato(
        "FIC-005",
        "Reserva de terreno Estela",
        "escaneado",
        (
            "Partes: Persona Theta y Persona Iota, identidades inventadas. Inmueble: terreno Estela, lote ficticio T-09, superficie de 320 metros cuadrados.",
            "Reserva: 25000 pesos ficticios por un plazo de quince días naturales, desde el 5 de abril de 2027. El precio de referencia es 850000 pesos ficticios.",
            "Condición de devolución: el apartado se devuelve íntegro si la documentación de propiedad presenta inconsistencias antes del vencimiento.",
            "La reserva no transfiere la propiedad. La firma definitiva depende de verificar la documentación y del acuerdo de ambas partes.",
        ),
    ),
    Contrato(
        "FIC-006",
        "Arrendamiento de oficina Faro",
        "mixto",
        (
            "Partes: Persona Kappa y Persona Lambda, identidades inventadas. Inmueble: oficina Faro, torre ficticia Prisma, nivel 3, espacio O-16.",
            "Renta mensual: 22000 pesos ficticios. Plazo de doce meses desde el 1 de mayo de 2027. Se incluye un cajón de estacionamiento.",
            "Acceso: lunes a viernes de ocho a veinte horas. Las modificaciones eléctricas requieren autorización previa por escrito.",
            "Actualización de renta: cuatro por ciento al renovar. Depósito: dos mensualidades, con devolución dentro de cuarenta y cinco días después de la entrega.",
        ),
    ),
)


def generar(destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    estilos = getSampleStyleSheet()
    estilos["BodyText"].fontSize = 12
    estilos["BodyText"].leading = 19
    for contrato in CONTRATOS:
        digital = pymupdf.open()
        for numero in range(2):
            memoria = BytesIO()
            pagina = SimpleDocTemplate(memoria, pagesize=A4, topMargin=65, bottomMargin=65)
            contenido = [
                Paragraph("DOCUMENTO FICTICIO · DEMOSTRACIÓN ACADÉMICA", estilos["Heading2"]),
                Paragraph(f"{contrato.folio} | {contrato.titulo}", estilos["Title"]),
                Spacer(1, 25),
            ]
            for indice in range(numero * 2, numero * 2 + 2):
                contenido.extend(
                    [
                        Paragraph(f"Cláusula {indice + 1}", estilos["Heading2"]),
                        Paragraph(contrato.clausulas[indice], estilos["BodyText"]),
                        Spacer(1, 24),
                    ]
                )
            contenido.append(
                Paragraph(
                    f"Página {numero + 1}. Todo el contenido y sus partes son inventados.",
                    estilos["BodyText"],
                )
            )
            pagina.build(contenido)
            with pymupdf.open(stream=memoria.getvalue(), filetype="pdf") as parcial:
                digital.insert_pdf(parcial)
        resultado = pymupdf.open()
        for indice, pagina in enumerate(digital):
            escanear = (
                contrato.formato == "escaneado" or contrato.formato == "mixto" and indice == 1
            )
            if escanear:
                imagen = pagina.get_pixmap(dpi=160)
                nueva = resultado.new_page(width=pagina.rect.width, height=pagina.rect.height)
                nueva.insert_image(nueva.rect, stream=imagen.tobytes("png"))
            else:
                resultado.insert_pdf(digital, from_page=indice, to_page=indice)
        resultado.set_metadata(
            {"title": contrato.titulo, "subject": "Documento totalmente ficticio"}
        )
        resultado.save(destino / f"{contrato.folio}_{contrato.formato}.pdf", deflate=True)
        resultado.close()
        digital.close()
    print(f"{len(CONTRATOS)} contratos ficticios en {destino}")


if __name__ == "__main__":
    generar(Path(__file__).parent / "contratos")
