"""Produce fuentes draw.io y PNG del diseño propuesto."""

from dataclasses import dataclass
from html import escape
from math import hypot
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

import pymupdf


@dataclass(frozen=True)
class Caja:
    id: str
    x: int
    y: int
    titulo: str
    lineas: tuple[str, ...]
    ancho: int = 260
    alto: int = 160
    fondo: str = "#ffffff"
    borde: str = "#98ada2"


@dataclass(frozen=True)
class Enlace:
    origen: str
    destino: str
    texto: str
    opcional: bool = False


def generar(
    carpeta: Path,
    nombre: str,
    cajas: list[Caja],
    enlaces: list[Enlace],
    *,
    subtitulo: str = "Motor documental inmobiliario | Implementación local, noviembre de 2026",
    notas: tuple[str, ...] = (),
) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    archivo = Element("mxfile", host="app.diagrams.net")
    diagrama = SubElement(archivo, "diagram", name=nombre)
    modelo = SubElement(diagrama, "mxGraphModel", dx="1400", dy="850", grid="1")
    raiz = SubElement(modelo, "root")
    SubElement(raiz, "mxCell", id="0")
    SubElement(raiz, "mxCell", id="1", parent="0")
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="850">',
        '<rect width="1400" height="850" fill="#f8f7f3"/>',
        '<defs><marker id="flecha" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#627c72"/></marker></defs>',
        f'<text x="40" y="50" font-size="27" fill="#193e34">{escape(nombre.replace("_", " "))}</text>',
        f'<text x="40" y="{87 if notas else 82}" font-size="15" fill="#52655e">{escape(subtitulo)}</text>',
    ]
    posiciones = {c.id: c for c in cajas}
    for indice, enlace in enumerate(enlaces):
        origen, destino = posiciones[enlace.origen], posiciones[enlace.destino]
        estilo = "endArrow=classic;strokeColor=#627c72;fontSize=14;"
        discontinuo = ""
        if enlace.opcional:
            estilo += "dashed=1;"
            discontinuo = ' stroke-dasharray="7 5"'
        celda = SubElement(
            raiz,
            "mxCell",
            id=f"e{indice}",
            value=enlace.texto,
            edge="1",
            parent="1",
            source=origen.id,
            target=destino.id,
            style=estilo,
        )
        SubElement(celda, "mxGeometry", relative="1", attrib={"as": "geometry"})
        if origen.y == destino.y:
            x1, y1 = origen.x + origen.ancho, origen.y + origen.alto / 2
            x2, y2 = destino.x, destino.y + destino.alto / 2
        else:
            x1, y1 = origen.x + origen.ancho / 2, origen.y + origen.alto
            x2, y2 = destino.x + destino.ancho / 2, destino.y
        distancia = hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / distancia, (y2 - y1) / distancia
        flecha = f"{x2},{y2} {x2 - 12 * ux + 5 * uy},{y2 - 12 * uy - 5 * ux} {x2 - 12 * ux - 5 * uy},{y2 - 12 * uy + 5 * ux}"
        etiqueta_x, etiqueta_y = (x1 + x2) / 2, (y1 + y2) / 2 - 12
        ancho_etiqueta = len(enlace.texto) * 7 + 12
        svg.extend(
            [
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#627c72" stroke-width="2"{discontinuo} marker-end="url(#flecha)"/>',
                f'<polygon points="{flecha}" fill="#627c72"/>',
                f'<rect x="{etiqueta_x - ancho_etiqueta / 2}" y="{etiqueta_y - 14}" width="{ancho_etiqueta}" height="19" fill="#f8f7f3"/>',
                f'<text x="{etiqueta_x}" y="{etiqueta_y}" text-anchor="middle" font-size="13" fill="#334d42">{escape(enlace.texto)}</text>',
            ]
        )
    for caja in cajas:
        valor = "\n".join((caja.titulo, *caja.lineas))
        celda = SubElement(
            raiz,
            "mxCell",
            id=caja.id,
            value=valor,
            vertex="1",
            parent="1",
            style=f"rounded=1;whiteSpace=wrap;fillColor={caja.fondo};strokeColor={caja.borde};fontSize=16;align=left;spacing=16;",
        )
        SubElement(
            celda,
            "mxGeometry",
            x=str(caja.x),
            y=str(caja.y),
            width=str(caja.ancho),
            height=str(caja.alto),
            attrib={"as": "geometry"},
        )
        svg.append(
            f'<rect x="{caja.x}" y="{caja.y}" width="{caja.ancho}" height="{caja.alto}" rx="10" fill="{caja.fondo}" stroke="{caja.borde}"/>'
        )
        for indice, texto in enumerate((caja.titulo, *caja.lineas)):
            svg.append(
                f'<text x="{caja.x + 16}" y="{caja.y + 32 + indice * 25}" font-size="{18 if indice == 0 else 15}" fill="#193e34">{escape(texto)}</text>'
            )
    if notas:
        textos = [
            ("titulo", nombre.replace("_", " "), 18, 45, 27),
            ("subtitulo", subtitulo, 55, 45, 15),
            ("nota", "\n".join(notas), 770, 65, 14),
        ]
        for identificador, texto, y, alto, tamano in textos:
            celda = SubElement(
                raiz, "mxCell", id=identificador, value=texto, vertex="1", parent="1",
                style=f"text;whiteSpace=wrap;strokeColor=none;fillColor=none;fontSize={tamano};align=left;",
            )
            SubElement(celda, "mxGeometry", x="40", y=str(y), width="1320", height=str(alto), attrib={"as": "geometry"})
        for indice, nota in enumerate(notas):
            svg.append(f'<text x="40" y="{802 + indice * 24}" font-size="14" fill="#193e34">{escape(nota)}</text>')
    else:
        svg.append('<text x="40" y="815" font-size="14" fill="#52655e">Corpus ficticio. GPT-6 Luna, R2 y WhatsApp oficial se integrarán en etapas posteriores.</text>')
    svg.append("</svg>")
    (carpeta / f"{nombre}.drawio").write_bytes(
        tostring(archivo, encoding="utf-8", xml_declaration=True)
    )
    with pymupdf.open(stream="".join(svg).encode(), filetype="svg") as documento:
        documento[0].get_pixmap(dpi=120).save(carpeta / f"{nombre}.png")


def generar_contexto(docs: Path) -> None:
    subtitulo = "Consulta de contratos ficticios y respuestas con fuentes | Noviembre de 2026"
    notas = (
        "El operador conserva los documentos y verifica sus fuentes.",
        "OpenAI es un apoyo opcional para redactar respuestas; la búsqueda documental funciona por separado.",
    )
    generar(
        docs / "01_Arquitectura",
        "C4_Contexto",
        [
            Caja(
                "usuario",
                40,
                230,
                "Operador inmobiliario",
                ("Organiza contratos ficticios", "y consulta sus cláusulas."),
            ),
            Caja(
                "motor",
                480,
                230,
                "Sistema documental",
                ("Organiza documentos ficticios.", "Encuentra información y muestra", "el documento y la página de origen."),
                ancho=330,
            ),
            Caja(
                "fuentes",
                1000,
                230,
                "Documentos ficticios",
                ("Contratos y expedientes", "para la demostración."),
                ancho=330,
            ),
            Caja(
                "openai",
                480,
                570,
                "OpenAI (servicio externo)",
                ("Apoyo opcional para redactar", "respuestas basadas en fuentes."),
                ancho=330,
                fondo="#fff8e8",
                borde="#c6aa7a",
            ),
        ],
        [
            Enlace("usuario", "motor", "Carga y consulta"),
            Enlace("motor", "fuentes", "Lee y referencia"),
            Enlace("motor", "openai", "Apoyo opcional para responder con fuentes", opcional=True),
        ],
        subtitulo=subtitulo,
        notas=notas,
    )


def generar_arquitectura(docs: Path) -> None:
    generar_contexto(docs)
    subtitulo = "Motor documental inmobiliario | Tres contenedores locales y chat opcional | Noviembre de 2026"
    notas = (
        "La recuperación local funciona sin LLM. OpenAI recibe consulta y pasajes, sin carga de originales.",
        "Luna es opcional. R2 y WhatsApp corresponden a etapas posteriores.",
    )
    generar(
        docs / "01_Arquitectura",
        "DAR_Arquitectura",
        [
            Caja(
                "web",
                40,
                180,
                "Contenedor web",
                ("Nuxt UI 4.12 + BFF", "HTTP solo en localhost", "API key en servidor", "Sin secret de Luna."),
                ancho=300,
                alto=180,
            ),
            Caja(
                "api",
                520,
                180,
                "Contenedor API",
                ("FastAPI + buscar_documentos", "Recuperación y chat opcional", "Compose secret Luna: solo API", "Una búsqueda local por turno."),
                ancho=330,
                alto=180,
            ),
            Caja(
                "db",
                1040,
                180,
                "Contenedor PostgreSQL",
                ("pgvector y búsqueda textual", "Cuatro tablas relacionadas", "Red datos interna", "Sin puerto público."),
                ancho=320,
                alto=180,
            ),
            Caja(
                "ml",
                40,
                540,
                "Motor dentro de la API",
                ("PyMuPDF + Tesseract", "Embeddings E5, 384", "Textual, vectorial y RRF", "Funciona sin OpenAI."),
                ancho=300,
                alto=180,
            ),
            Caja(
                "openai",
                520,
                540,
                "OpenAI Responses (externo)",
                ("Modelo gpt-6-luna", "Consulta y pasajes recuperados", "Sin file_search gestionado", "Chat opcional por credencial."),
                ancho=330,
                alto=180,
                fondo="#fff8e8",
                borde="#c6aa7a",
            ),
            Caja(
                "archivos",
                1040,
                540,
                "Volumen de originales",
                ("PDF y TXT locales privados", "Acceso y descarga por API", "Persistencia entre reinicios", "La web no monta el volumen."),
                ancho=320,
                alto=180,
            ),
        ],
        [
            Enlace("web", "api", "HTTP / JSON + multipart"),
            Enlace("api", "db", "SQL / red privada"),
            Enlace("api", "ml", "Funciones Python"),
            Enlace("api", "openai", "HTTPS saliente / 443", opcional=True),
            Enlace("api", "archivos", "Sistema de archivos"),
        ],
        subtitulo=subtitulo,
        notas=notas,
    )


if __name__ == "__main__":
    docs = Path(__file__).resolve().parents[1] / "docs"
    generar_arquitectura(docs)
    generar(
        docs / "02_Datos",
        "DER",
        [
            Caja(
                "colecciones",
                30,
                260,
                "colecciones",
                ("PK id: uuid", "UNIQUE nombre", "creada_en"),
                ancho=260,
                alto=230,
            ),
            Caja(
                "documentos",
                380,
                260,
                "documentos",
                (
                    "PK id: uuid",
                    "FK coleccion_id",
                    "titulo, nombre_original",
                    "extension, activo",
                    "modelo, creado_en",
                ),
                ancho=280,
                alto=230,
            ),
            Caja(
                "paginas",
                750,
                260,
                "paginas",
                (
                    "PK id: uuid",
                    "FK documento_id",
                    "numero, texto, metodo",
                    "UNIQUE documento + numero",
                ),
                ancho=280,
                alto=230,
            ),
            Caja(
                "fragmentos",
                1110,
                260,
                "fragmentos",
                (
                    "PK id: uuid",
                    "FK pagina_id",
                    "orden, texto",
                    "embedding: vector(384)",
                    "busqueda: tsvector",
                ),
                ancho=260,
                alto=230,
            ),
        ],
        [
            Enlace("colecciones", "documentos", "1 a N"),
            Enlace("documentos", "paginas", "1 a N"),
            Enlace("paginas", "fragmentos", "1 a N"),
        ],
    )
