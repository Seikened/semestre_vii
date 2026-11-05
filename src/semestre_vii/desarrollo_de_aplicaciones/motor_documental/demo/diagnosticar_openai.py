import os
import sys
from pathlib import Path

from app.errores import AppError, CodigoError
from cliente_openai import ClienteOpenAI
from evaluar_corpus import espacios, normalizar
from modelos_corpus import CorpusFicticio
from modelos_openai import BusquedaOpenAI, PaginaArchivos, RegistroOpenAI, RespuestaBusqueda
from pydantic import BaseModel, TypeAdapter


class TextoIndexado(BaseModel):
    type: str | None = None
    text: str | None = None


class ContenidoIndexado(BaseModel):
    data: list[TextoIndexado]
    has_more: bool
    next_page: str | None = None


class ControlIndice(BaseModel):
    caso_id: str
    archivo: str
    formato: str
    bloques: int
    caracteres: int
    cita_normalizada_en_un_bloque: bool
    cita_literal_en_un_bloque: bool


class ConsultaAusente(BaseModel):
    consulta: str
    modo: str


class NegativaOpenAI(BaseModel):
    vector_store_id: str
    modo_local: str
    peticion: BusquedaOpenAI
    respuesta: RespuestaBusqueda
    request_id: str | None


def inspeccionar(raiz: Path, archivo_clave: Path, negativas_locales: Path) -> None:
    destino = raiz / "comparacion_openai"
    if len(list((destino / "respuestas").glob("*.json"))) != 612:
        raise AppError(CodigoError.ENTRADA_INVALIDA, "Completar las 612 búsquedas antes del diagnóstico adicional.")
    corpus = CorpusFicticio.model_validate_json((raiz / "corpus.json").read_bytes())
    carga = RegistroOpenAI.model_validate_json((destino / "carga_openai.json").read_bytes())
    identificadores = {r.archivo: r.file_id for r in carga.archivos}
    cliente = ClienteOpenAI(archivo_clave)
    base = f"/vector_stores/{carga.vector_store_id}"
    contenidos = destino / "contenidos"
    contenidos.mkdir(exist_ok=True)
    textos = {}
    for nombre in sorted({c.archivo for c in corpus.casos}):
        ruta = contenidos / f"{nombre}.json"
        if not ruta.exists():
            respuesta = cliente.pedir("GET", base + f"/files/{identificadores[nombre]}/content")
            ruta.write_bytes(respuesta.contenido)
        contenido = ContenidoIndexado.model_validate_json(ruta.read_bytes())
        if contenido.has_more:
            raise AppError(CodigoError.ENTRADA_INVALIDA, f"Falta completar contenido paginado de {nombre}; no atribuir ausencia de cita.")
        textos[nombre] = [b.text for b in contenido.data if b.type == "text" and b.text]
    controles = []
    for caso in corpus.casos:
        bloques = textos[caso.archivo]
        controles.append(ControlIndice(
            caso_id=caso.id, archivo=caso.archivo, formato=caso.formato.value,
            bloques=len(bloques), caracteres=sum(len(b) for b in bloques),
            cita_normalizada_en_un_bloque=any(normalizar(caso.cita) in normalizar(b) for b in bloques),
            cita_literal_en_un_bloque=any(espacios(caso.cita) in espacios(b) for b in bloques),
        ))
    (destino / "control_contenido.json").write_bytes(TypeAdapter(list[ControlIndice]).dump_json(controles, indent=2))
    inventario = destino / "inventario"
    inventario.mkdir(exist_ok=True)
    cursor = ""
    numero = 1
    while True:
        respuesta = cliente.pedir("GET", base + "/files?limit=100" + cursor)
        (inventario / f"{numero}.json").write_bytes(respuesta.contenido)
        pagina = PaginaArchivos.model_validate_json(respuesta.contenido)
        if not pagina.has_more:
            break
        cursor = f"&after={pagina.last_id}"
        numero += 1
    negativas = TypeAdapter(list[ConsultaAusente]).validate_json(negativas_locales.read_bytes())
    salida = destino / "negativas"
    salida.mkdir(exist_ok=True)
    for numero, negativa in enumerate(negativas, 1):
        ruta = salida / f"{numero}.json"
        entrada = BusquedaOpenAI(query=negativa.consulta)
        if ruta.exists():
            anterior = NegativaOpenAI.model_validate_json(ruta.read_bytes())
            if (anterior.vector_store_id, anterior.modo_local, anterior.peticion) != (carga.vector_store_id, negativa.modo, entrada):
                raise AppError(CodigoError.ENTRADA_INVALIDA, "El control negativo previo pertenece a otra consulta.")
            continue
        recibo = cliente.enviar(base + "/search", entrada)
        resultado = NegativaOpenAI(vector_store_id=carga.vector_store_id, modo_local=negativa.modo, peticion=entrada, respuesta=RespuestaBusqueda.model_validate_json(recibo.contenido), request_id=recibo.request_id)
        ruta.write_text(resultado.model_dump_json(indent=2))
    print(f"Diagnóstico: {len(textos)} documentos con casos, {len(controles)} citas y {len(negativas)} controles adicionales sin evidencia.")


if __name__ == "__main__":
    inspeccionar(Path(sys.argv[1]), Path(os.environ["OPENAI_API_KEY_FILE"]), Path(sys.argv[2]))
