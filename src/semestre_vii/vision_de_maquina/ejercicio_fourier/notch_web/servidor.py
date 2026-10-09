import base64
import json
from dataclasses import asdict
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import torch
from PIL import Image

from semestre_vii.vision_de_maquina.ejercicio_fourier.saco import cargar_saco_cuadrado
from semestre_vii.vision_de_maquina.vision_node import VisionNode

from .modelos import (
    ConfiguracionFiltro,
    ErrorRespuesta,
    InfoImagen,
    ResultadoFiltro,
    SolicitudFiltro,
)

_ASSETS = Path(__file__).parent / "static"
_RUTAS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/vista.js": ("vista.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}


class LaboratorioNotch:
    def __init__(self) -> None:
        self.imagen = cargar_saco_cuadrado()
        self.fourier = self.imagen.fft()
        self.original_png = _png(self.imagen)
        self.espectro_png = _png(self.fourier.magnitud())
        self.info = InfoImagen(
            "saco_paneles_led_cortada.bmp",
            self.imagen.width,
            self.imagen.height,
            self.imagen.height // 2,
            self.imagen.width // 2,
        )

    def filtrar(self, solicitud: SolicitudFiltro) -> ResultadoFiltro:
        puntos = [punto for punto in solicitud.puntos if punto.activo]
        if not puntos:
            return ResultadoFiltro("/api/original.png", "/api/espectro.png", 0, False)
        espectro = self.fourier
        for punto in puntos:
            espectro = espectro.notch_ideal([(punto.fila, punto.columna)], radio=punto.radio)
        imagen = espectro.inversa(valor_absoluto=True, clip=True)
        rechazados = (espectro.mascara == 0).sum().item()
        porcentaje = 100 * rechazados / (self.info.ancho * self.info.alto)
        dc = espectro.mascara[self.info.dc_fila, self.info.dc_columna].item() == 0
        return ResultadoFiltro(
            _data_url(_png(imagen)),
            _data_url(_png(espectro.magnitud())),
            porcentaje,
            dc,
        )


class ManejadorNotch(BaseHTTPRequestHandler):
    def __init__(self, *args, laboratorio: LaboratorioNotch, **kwargs) -> None:
        self.laboratorio = laboratorio
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        ruta = urlsplit(self.path).path
        if ruta == "/api/info":
            self._json(HTTPStatus.OK, self.laboratorio.info)
        elif ruta == "/api/original.png":
            self._responder(HTTPStatus.OK, "image/png", self.laboratorio.original_png)
        elif ruta == "/api/espectro.png":
            self._responder(HTTPStatus.OK, "image/png", self.laboratorio.espectro_png)
        elif ruta in ("/api/puntos.json", "/api/filtrada.png"):
            self._descargar(ruta)
        elif ruta in _RUTAS:
            nombre, tipo = _RUTAS[ruta]
            self._responder(HTTPStatus.OK, tipo, (_ASSETS / nombre).read_bytes())
        else:
            self._json(HTTPStatus.NOT_FOUND, ErrorRespuesta("ruta no encontrada"))

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/filtrar":
            self._json(HTTPStatus.NOT_FOUND, ErrorRespuesta("ruta no encontrada"))
            return
        longitud = self.headers.get("Content-Length", "")
        if not longitud.isdecimal() or len(longitud) > 5 or int(longitud) > 65_536:
            self._json(HTTPStatus.BAD_REQUEST, ErrorRespuesta("el JSON debe ocupar hasta 64 KiB"))
            return
        if self.headers.get_content_type() != "application/json":
            self._json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, ErrorRespuesta("usa application/json"))
            return
        try:
            contenido = json.loads(self.rfile.read(int(longitud)))
        except (ValueError, RecursionError):
            self._json(HTTPStatus.BAD_REQUEST, ErrorRespuesta("el JSON no es válido"))
            return
        try:
            solicitud = SolicitudFiltro.desde_json(
                contenido, self.laboratorio.info.alto, self.laboratorio.info.ancho,
            )
        except (TypeError, ValueError) as error:
            self._json(HTTPStatus.BAD_REQUEST, ErrorRespuesta(str(error)))
            return
        resultado = self.laboratorio.filtrar(solicitud)
        self._json(HTTPStatus.OK, resultado)

    def _json(self, estado: HTTPStatus, contenido: InfoImagen | ResultadoFiltro | ErrorRespuesta) -> None:
        cuerpo = json.dumps(asdict(contenido), ensure_ascii=False, allow_nan=False).encode()
        self._responder(estado, "application/json; charset=utf-8", cuerpo)

    def _descargar(self, ruta: str) -> None:
        filtro = parse_qs(urlsplit(self.path).query).get("filtro", [""])[0]
        try:
            contenido = json.loads(filtro)
        except (ValueError, RecursionError):
            self._json(HTTPStatus.BAD_REQUEST, ErrorRespuesta("el JSON no es válido"))
            return
        info = self.laboratorio.info
        try:
            solicitud = SolicitudFiltro.desde_json(contenido, info.alto, info.ancho)
        except (TypeError, ValueError) as error:
            self._json(HTTPStatus.BAD_REQUEST, ErrorRespuesta(str(error)))
            return
        if ruta == "/api/puntos.json":
            configuracion = ConfiguracionFiltro(
                info.nombre, info.ancho, info.alto, "inferior", solicitud.puntos,
            )
            cuerpo = json.dumps(asdict(configuracion), ensure_ascii=False, allow_nan=False).encode()
            self._responder(HTTPStatus.OK, "application/json", cuerpo, "notches_saco.json")
        else:
            resultado = self.laboratorio.filtrar(solicitud)
            cuerpo = self.laboratorio.original_png
            if resultado.imagen.startswith("data:"):
                cuerpo = base64.b64decode(resultado.imagen.split(",", 1)[1])
            self._responder(HTTPStatus.OK, "image/png", cuerpo, "saco_notch.png")

    def _responder(self, estado: HTTPStatus, tipo: str, cuerpo: bytes, archivo: str | None = None) -> None:
        self.send_response(estado)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if archivo:
            self.send_header("Content-Disposition", f'attachment; filename="{archivo}"')
        self.end_headers()
        self.wfile.write(cuerpo)


def crear_servidor(puerto: int) -> HTTPServer:
    manejador = partial(ManejadorNotch, laboratorio=LaboratorioNotch())
    return HTTPServer(("127.0.0.1", puerto), manejador)


def _png(imagen: VisionNode) -> bytes:
    pixeles = imagen.tensor[0].detach().cpu().clamp(0, 1).mul(255).round().to(torch.uint8).numpy()
    with BytesIO() as archivo:
        Image.fromarray(pixeles).save(archivo, format="PNG")
        return archivo.getvalue()


def _data_url(contenido: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(contenido).decode("ascii")
