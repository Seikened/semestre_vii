import json
import os
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4
from zoneinfo import ZoneInfo

from app.contratos import Coleccion, DetalleDocumento, Documento, ErrorRespuesta, ResultadoBusqueda
from pydantic import BaseModel, TypeAdapter
from verificar_motor import CASOS, CONTROLES, normalizar


class Comprobacion(BaseModel):
    nombre: str
    correcto: bool
    detalle: str


class InformeServicio(BaseModel):
    fecha: str
    comprobaciones: list[Comprobacion]
    consultas: list[ResultadoBusqueda]


def verificar(destino: Path) -> InformeServicio:
    clave = Path(os.environ["API_KEY_FILE"]).read_text().strip()
    comprobaciones = []
    consultas = []

    def comprobar(nombre, condicion, detalle):
        comprobaciones.append(Comprobacion(nombre=nombre, correcto=bool(condicion), detalle=detalle))

    def solicitar(metodo, ruta, esperado=200, datos=None, contenido=None, tipo=None, autorizar=True):
        cabeceras = {"X-API-Key": clave} if autorizar else {}
        if datos is not None:
            contenido = json.dumps(datos).encode()
            tipo = "application/json"
        if tipo:
            cabeceras["Content-Type"] = tipo
        peticion = Request(f"http://127.0.0.1:8000{ruta}", data=contenido, headers=cabeceras, method=metodo)
        try:
            with urlopen(peticion, timeout=120) as respuesta:
                status, cuerpo = respuesta.status, respuesta.read()
        except HTTPError as error:
            status, cuerpo = error.code, error.read()
        comprobar(f"{metodo} {ruta}: HTTP {esperado}", status == esperado, f"HTTP {status}")
        if status >= 400:
            error = ErrorRespuesta.model_validate_json(cuerpo)
            comprobar(f"Error seguro: {error.codigo}", bool(error.detalle), error.detalle)
        return cuerpo

    def subir(nombre, contenido, coleccion_id, esperado=201):
        borde = uuid4().hex
        partes = []
        for campo, valor in (("titulo", "Contrato ficticio de verificación"), ("coleccion_id", str(coleccion_id))):
            partes.append(f'--{borde}\r\nContent-Disposition: form-data; name="{campo}"\r\n\r\n{valor}\r\n'.encode())
        partes.append(f'--{borde}\r\nContent-Disposition: form-data; name="archivo"; filename="{nombre}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode())
        partes.extend([contenido, f'\r\n--{borde}--\r\n'.encode()])
        return solicitar("POST", "/documentos", esperado, contenido=b"".join(partes), tipo=f"multipart/form-data; boundary={borde}")

    solicitar("GET", "/salud")
    solicitar("GET", "/documentos", 401, autorizar=False)
    solicitar("POST", "/buscar", 422, datos={"texto": "   "})
    solicitar("POST", "/buscar", 422, datos={"texto": "depósito", "limite": 21})
    documentos = TypeAdapter(list[Documento]).validate_json(solicitar("GET", "/documentos"))
    comprobar("Corpus inicial", len(documentos) >= 6, f"{len(documentos)} documentos activos")
    for caso in CASOS:
        resultado = ResultadoBusqueda.model_validate_json(solicitar("POST", "/buscar", datos={"texto": caso.consulta}))
        consultas.append(resultado)
        encontrada = any(f.nombre_original == caso.archivo and f.pagina == caso.pagina for f in resultado.coincidencias)
        comprobar(f"Fuente en top 5: {caso.archivo}", encontrada, caso.consulta)
    for control in CONTROLES:
        documento = next(d for d in documentos if d.nombre_original == control.archivo)
        detalle = DetalleDocumento.model_validate_json(solicitar("GET", f"/documentos/{documento.id}"))
        pagina = next(p for p in detalle.paginas if p.numero == control.pagina)
        comprobar(f"OCR: {control.frase}", normalizar(control.frase) in normalizar(pagina.texto), pagina.metodo)
    nombre = f"Verificación ficticia {datetime.now(ZoneInfo('America/Mexico_City')).strftime('%H%M%S')}"
    grupo = Coleccion.model_validate_json(solicitar("POST", "/colecciones", 201, datos={"nombre": nombre}))
    solicitar("POST", "/colecciones", 409, datos={"nombre": nombre})
    vacia = ResultadoBusqueda.model_validate_json(solicitar("POST", "/buscar", datos={"texto": "depósito", "coleccion_id": str(grupo.id)}))
    comprobar("Colección vacía", not vacia.coincidencias, "Sin resultados de otras colecciones")
    for modo in ("texto", "vector"):
        resultado = ResultadoBusqueda.model_validate_json(solicitar("POST", "/buscar", datos={"texto": "depósito", "modo": modo}))
        comprobar(f"Búsqueda {modo}", bool(resultado.coincidencias), f"{len(resultado.coincidencias)} coincidencias")
    solicitar("GET", f"/documentos/{uuid4()}", 404)
    subir("vacio.txt", b" ", grupo.id, 422)
    subir("codificacion.txt", b"\xff\xfe", grupo.id, 415)
    subir("archivo.exe", b"ficticio", grupo.id, 415)
    subir("roto.pdf", b"archivo ficticio que no es PDF", grupo.id, 422)
    subir("grande.txt", b"x" * (10 * 1024 * 1024 + 1), grupo.id, 413)
    subir("sin_coleccion.txt", b"Documento completamente ficticio de una propiedad inventada.", uuid4(), 404)
    texto = "Contrato totalmente ficticio. Propiedad Olmo. Aviso de salida de sesenta días."
    nuevo = DetalleDocumento.model_validate_json(subir("FIC-TXT.txt", texto.encode(), grupo.id))
    id_nuevo = nuevo.documento.id
    solicitar("GET", f"/documentos/{id_nuevo}/archivo")
    editado = DetalleDocumento.model_validate_json(solicitar("PATCH", f"/documentos/{id_nuevo}", datos={"titulo": "Contrato Olmo ficticio"}))
    comprobar("Edición de título", editado.documento.titulo == "Contrato Olmo ficticio", editado.documento.titulo)
    escaneado = Path("demo/contratos/FIC-002_escaneado.pdf")
    ocr = DetalleDocumento.model_validate_json(subir(escaneado.name, escaneado.read_bytes(), grupo.id))
    comprobar("SC001 vía carga HTTP", ocr.documento.paginas_ocr == 2, "Dos páginas escaneadas procesadas con OCR")
    for identificador in (id_nuevo, ocr.documento.id):
        solicitar("DELETE", f"/documentos/{identificador}", 204)
        solicitar("GET", f"/documentos/{identificador}", 404)
        solicitar("GET", f"/documentos/{identificador}/archivo", 404)
    retirados = ResultadoBusqueda.model_validate_json(solicitar("POST", "/buscar", datos={"texto": "sesenta días", "coleccion_id": str(grupo.id)}))
    comprobar("Baja excluye búsqueda", not retirados.coincidencias, "Colección sin documentos activos")
    informe = InformeServicio(fecha=datetime.now(ZoneInfo("America/Mexico_City")).isoformat(), comprobaciones=comprobaciones, consultas=consultas)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(informe.model_dump_json(indent=2), encoding="utf-8")
    return informe


if __name__ == "__main__":
    informe = verificar(Path(os.getenv("INFORME_SERVICIO", "/tmp/servicio_http.json")))
    correctas = sum(c.correcto for c in informe.comprobaciones)
    print(f"Comprobaciones correctas: {correctas}/{len(informe.comprobaciones)}")
    if correctas != len(informe.comprobaciones):
        raise SystemExit(1)
