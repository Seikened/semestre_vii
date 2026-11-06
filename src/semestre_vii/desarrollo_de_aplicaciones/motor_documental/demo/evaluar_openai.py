import hashlib
import os
import sys
from pathlib import Path
from time import monotonic, perf_counter, sleep

from app.errores import AppError, CodigoError
from cliente_openai import ClienteOpenAI
from evaluar_corpus import espacios, normalizar
from modelos_corpus import CorpusFicticio, InformeEvaluacion
from modelos_openai import (
    ArchivoIndexado,
    BusquedaOpenAI,
    LoteOpenAI,
    MedicionOpenAI,
    NuevoLote,
    PaginaArchivos,
    ReciboArchivo,
    RegistroOpenAI,
    RespuestaBusqueda,
    StoreOpenAI,
)
from pydantic import BaseModel, TypeAdapter


def ejecutar(raiz: Path, archivo_clave: Path, informe_local: Path, store_id: str) -> None:
    contenido = (raiz / "corpus.json").read_bytes()
    corpus = CorpusFicticio.model_validate_json(contenido)
    huella = hashlib.sha256(contenido).hexdigest()
    local = InformeEvaluacion.model_validate_json(informe_local.read_bytes())
    if huella != local.corpus_sha256 or len(local.consultas) != 612:
        raise AppError(CodigoError.ENTRADA_INVALIDA, "El corpus o el informe local no coinciden con las 612 consultas fijadas.")
    for documento in corpus.documentos:
        archivo = raiz / "archivos" / documento.archivo
        if archivo.resolve().parent != (raiz / "archivos").resolve():
            raise AppError(CodigoError.ENTRADA_INVALIDA, "El manifiesto apunta fuera del corpus.")
        if hashlib.sha256(archivo.read_bytes()).hexdigest() != documento.sha256:
            raise AppError(CodigoError.DOCUMENTO_LECTURA, f"El archivo {archivo.name} no coincide con su hash.")
    destino = raiz / "comparacion_openai"
    destino.mkdir(exist_ok=True)
    cliente = ClienteOpenAI(archivo_clave)
    registro = cargar(cliente, corpus, raiz, destino, huella, store_id)
    indexar(cliente, registro, destino)
    evaluar(cliente, corpus, local, destino, huella, store_id)


def cargar(cliente: ClienteOpenAI, corpus: CorpusFicticio, raiz: Path, destino: Path, huella: str, store_id: str) -> RegistroOpenAI:
    ruta = destino / "carga_openai.json"
    store = StoreOpenAI.model_validate_json(cliente.pedir("GET", f"/vector_stores/{store_id}").contenido)
    if not (destino / "store_antes_carga.json").exists():
        guardar(store, destino / "store_antes_carga.json")
    if ruta.exists():
        registro = RegistroOpenAI.model_validate_json(ruta.read_bytes())
        if registro.corpus_sha256 != huella or registro.vector_store_id != store_id:
            raise AppError(CodigoError.ENTRADA_INVALIDA, "El recibo OpenAI pertenece a otra evaluación.")
    else:
        if store.file_counts.total:
            raise AppError(CodigoError.ENTRADA_INVALIDA, "El Store contiene archivos sin recibos de esta evaluación.")
        registro = RegistroOpenAI(corpus_sha256=huella, vector_store_id=store_id)
    if registro.operacion_pendiente:
        raise AppError(CodigoError.ENTRADA_INVALIDA, f"Reconciliar primero: {registro.operacion_pendiente}.")
    recibos = {r.archivo: r for r in registro.archivos}
    for numero, documento in enumerate(corpus.documentos, 1):
        if documento.archivo in recibos:
            if recibos[documento.archivo].sha256 != documento.sha256:
                raise AppError(CodigoError.ENTRADA_INVALIDA, "Cambió un hash previamente enviado.")
            continue
        registro.operacion_pendiente = documento.archivo
        guardar(registro, ruta)
        inicio = perf_counter()
        recibido = cliente.subir(raiz / "archivos" / documento.archivo, documento.sha256)
        registro.archivos.append(ReciboArchivo(archivo=documento.archivo, sha256=documento.sha256, file_id=recibido.id, segundos=perf_counter() - inicio))
        registro.operacion_pendiente = None
        guardar(registro, ruta)
        if numero % 10 == 0:
            print(f"Enviados a OpenAI {numero}/{len(corpus.documentos)} archivos", flush=True)
    return registro


def indexar(cliente: ClienteOpenAI, registro: RegistroOpenAI, destino: Path) -> None:
    base = f"/vector_stores/{registro.vector_store_id}"
    if registro.lote_id is None:
        registro.operacion_pendiente = "adjuntar lote"
        guardar(registro, destino / "carga_openai.json")
        entrada = NuevoLote(file_ids=[r.file_id for r in registro.archivos])
        lote = LoteOpenAI.model_validate_json(cliente.enviar(base + "/file_batches", entrada).contenido)
        registro.lote_id = lote.id
        registro.operacion_pendiente = None
        guardar(registro, destino / "carga_openai.json")
    plazo = monotonic() + 3600
    while True:
        lote = LoteOpenAI.model_validate_json(cliente.pedir("GET", base + f"/file_batches/{registro.lote_id}").contenido)
        guardar(lote, destino / "lote_openai.json")
        print(f"Indexación OpenAI: {lote.file_counts.model_dump()}", flush=True)
        if lote.status in ("completed", "failed", "cancelled"):
            break
        if monotonic() >= plazo:
            raise AppError(CodigoError.UNKNOWN, "La indexación sigue pendiente después de una hora.")
        sleep(5)
    archivos = []
    cursor = ""
    while True:
        pagina = PaginaArchivos.model_validate_json(cliente.pedir("GET", base + "/files?limit=100" + cursor).contenido)
        archivos.extend(pagina.data)
        if not pagina.has_more:
            break
        cursor = f"&after={pagina.last_id}"
    (destino / "archivos_indexados.json").write_bytes(TypeAdapter(list[ArchivoIndexado]).dump_json(archivos, indent=2))
    if {a.id for a in archivos} != {r.file_id for r in registro.archivos}:
        raise AppError(CodigoError.ENTRADA_INVALIDA, "El Store no contiene exactamente los archivos enviados.")
    if any(a.status == "in_progress" for a in archivos):
        raise AppError(CodigoError.UNKNOWN, "Aún hay archivos pendientes de indexación.")
    guardar(StoreOpenAI.model_validate_json(cliente.pedir("GET", base).contenido), destino / "store_indexado.json")


def evaluar(cliente: ClienteOpenAI, corpus: CorpusFicticio, local: InformeEvaluacion, destino: Path, huella: str, store_id: str) -> None:
    casos = {c.id: c for c in corpus.casos}
    respuestas = destino / "respuestas"
    respuestas.mkdir(exist_ok=True)
    for numero, consulta in enumerate(local.consultas, 1):
        ruta = respuestas / f"{numero:03}.json"
        entrada = BusquedaOpenAI(query=consulta.consulta)
        if ruta.exists():
            anterior = MedicionOpenAI.model_validate_json(ruta.read_bytes())
            if (anterior.vector_store_id, anterior.corpus_sha256, anterior.caso_id, anterior.variante, anterior.modo_local, anterior.peticion) != (store_id, huella, consulta.caso_id, consulta.variante, consulta.modo, entrada):
                raise AppError(CodigoError.ENTRADA_INVALIDA, "Una respuesta previa pertenece a otra consulta.")
            continue
        caso = casos[consulta.caso_id]
        inicio = perf_counter()
        recibo = cliente.enviar(f"/vector_stores/{store_id}/search", entrada)
        segundos = perf_counter() - inicio
        resultado = RespuestaBusqueda.model_validate_json(recibo.contenido)
        posicion = None
        cita = False
        literal = False
        for orden, fuente in enumerate(resultado.data, 1):
            if fuente.filename != caso.archivo:
                continue
            if posicion is None:
                posicion = orden
            cita = cita or any(normalizar(caso.cita) in normalizar(c.text) for c in fuente.content)
            literal = literal or any(espacios(caso.cita) in espacios(c.text) for c in fuente.content)
        medicion = MedicionOpenAI(
            vector_store_id=store_id, corpus_sha256=huella, caso_id=caso.id, variante=consulta.variante, modo_local=consulta.modo,
            archivo_esperado=caso.archivo, peticion=entrada, respuesta=resultado,
            request_id=recibo.request_id, segundos=segundos, posicion_documento=posicion,
            cita_normalizada_en_top5=cita, cita_literal_en_top5=literal,
        )
        guardar(medicion, ruta)
        if numero % 12 == 0:
            print(f"Consultas OpenAI conservadas: {numero}/{len(local.consultas)}", flush=True)


def guardar(modelo: BaseModel, destino: Path) -> None:
    temporal = destino.with_suffix(".tmp")
    temporal.write_text(modelo.model_dump_json(indent=2))
    temporal.replace(destino)


if __name__ == "__main__":
    raiz = Path(sys.argv[1])
    informe = Path(sys.argv[2])
    ejecutar(raiz, Path(os.environ["OPENAI_API_KEY_FILE"]), informe, sys.argv[3])
