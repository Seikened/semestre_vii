from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


ROOT = Path("/Users/ferleon/Github/PROYECTOS_UNIVERSITARIOS/semestre_vii")
MEETING_PHOTO = Path("/Users/ferleon/Desktop/foto.png")
FORUM_SCREENSHOT = ROOT / "tmp/pdfs/actividad_6_evidencia_foro_final.png"
OUTPUT = ROOT / "output/pdf/Actividad_6_Encuadre_Semana_2_Fernando_Leon_Franco.pdf"

page_width, page_height = landscape(letter)
canvas = Canvas(str(OUTPUT), pagesize=(page_width, page_height))
canvas.setTitle("Actividad 6. Encuadre Semana 2")
canvas.setAuthor("Fernando León Franco")

red = HexColor("#C62828")
ink = HexColor("#1F2937")
muted = HexColor("#5F6B7A")
panel = HexColor("#F5F7FA")
border = HexColor("#D8DEE8")

canvas.setFillColor(red)
canvas.rect(0, page_height - 14, page_width, 14, stroke=0, fill=1)
canvas.setFillColor(ink)
canvas.setFont("Helvetica-Bold", 20)
canvas.drawString(42, page_height - 55, "Actividad 6. Encuadre Semana 2")
canvas.setFillColor(muted)
canvas.setFont("Helvetica", 10)
canvas.drawString(42, page_height - 73, "Gestión de Proyectos de Ingeniería")

panel_y = page_height - 160
canvas.setFillColor(panel)
canvas.setStrokeColor(border)
canvas.roundRect(42, panel_y, page_width - 84, 65, 7, stroke=1, fill=1)

labels = ("Nombre completo", "Matrícula", "Carrera")
values = (
    "Fernando León Franco",
    "192488-7",
    "Ingeniería en Inteligencia Artificial",
)
columns = (58, 280, 440)

for label, value, x in zip(labels, values, columns):
    canvas.setFillColor(muted)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(x, panel_y + 43, label.upper())
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 11)
    canvas.drawString(x, panel_y + 23, value)

canvas.setFillColor(ink)
canvas.setFont("Helvetica-Bold", 12)
canvas.drawString(42, panel_y - 30, "Evidencia de primera reunión del equipo")
canvas.setFillColor(muted)
canvas.setFont("Helvetica", 9)
canvas.drawString(
    42,
    panel_y - 45,
    "Reunión a distancia con los tres integrantes visibles.",
)

meeting_image = ImageReader(str(MEETING_PHOTO))
meeting_width, meeting_height = meeting_image.getSize()
meeting_scale = min(620 / meeting_width, 300 / meeting_height)
meeting_render_width = meeting_width * meeting_scale
meeting_render_height = meeting_height * meeting_scale
meeting_x = (page_width - meeting_render_width) / 2
meeting_y = 86

canvas.setStrokeColor(border)
canvas.rect(
    meeting_x - 1,
    meeting_y - 1,
    meeting_render_width + 2,
    meeting_render_height + 2,
    stroke=1,
    fill=0,
)
canvas.drawImage(
    meeting_image,
    meeting_x,
    meeting_y,
    width=meeting_render_width,
    height=meeting_render_height,
    preserveAspectRatio=True,
    mask="auto",
)

canvas.setFillColor(muted)
canvas.setFont("Helvetica-Oblique", 8.5)
canvas.drawCentredString(
    page_width / 2,
    68,
    "Santiago Romo, Rodrigo Mendoza Rodríguez y Fernando León durante la reunión del equipo.",
)
canvas.setStrokeColor(border)
canvas.line(42, 33, page_width - 42, 33)
canvas.setFillColor(muted)
canvas.setFont("Helvetica", 8)
canvas.drawString(42, 19, "Universidad Iberoamericana León | 28 de agosto de 2026")
canvas.drawRightString(page_width - 42, 19, "Página 1 de 2")

canvas.showPage()
canvas.setFillColor(red)
canvas.rect(0, page_height - 14, page_width, 14, stroke=0, fill=1)
canvas.setFillColor(ink)
canvas.setFont("Helvetica-Bold", 20)
canvas.drawString(42, page_height - 55, "Evidencia complementaria del foro")
canvas.setFillColor(muted)
canvas.setFont("Helvetica", 10)
canvas.drawString(
    42,
    page_height - 73,
    "Publicación de integración del equipo en la Actividad 5.",
)

forum_image = ImageReader(str(FORUM_SCREENSHOT))
forum_width, forum_height = forum_image.getSize()
forum_render_width = page_width - 84
forum_render_height = forum_render_width * forum_height / forum_width
forum_y = page_height - 125 - forum_render_height

canvas.setStrokeColor(border)
canvas.rect(41, forum_y - 1, forum_render_width + 2, forum_render_height + 2, stroke=1, fill=0)
canvas.drawImage(
    forum_image,
    42,
    forum_y,
    width=forum_render_width,
    height=forum_render_height,
    preserveAspectRatio=True,
    mask="auto",
)

canvas.setFillColor(panel)
canvas.setStrokeColor(border)
canvas.roundRect(42, forum_y - 87, page_width - 84, 55, 7, stroke=1, fill=1)
canvas.setFillColor(ink)
canvas.setFont("Helvetica-Bold", 9)
canvas.drawString(58, forum_y - 54, "Integrantes mencionados")
canvas.setFillColor(muted)
canvas.setFont("Helvetica", 9)
canvas.drawString(
    58,
    forum_y - 70,
    "Fernando León, Rodrigo Mendoza y Santiago Romo.",
)

canvas.setStrokeColor(border)
canvas.line(42, 33, page_width - 42, 33)
canvas.setFillColor(muted)
canvas.setFont("Helvetica", 8)
canvas.drawString(42, 19, "Universidad Iberoamericana León | 28 de agosto de 2026")
canvas.drawRightString(page_width - 42, 19, "Página 2 de 2")

canvas.save()
print(OUTPUT)
