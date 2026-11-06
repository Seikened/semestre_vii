import hashlib
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from app.errores import AppError, CodigoError
from modelos_corpus import CorpusFicticio, InformeEvaluacion
from modelos_openai import BusquedaOpenAI, MedicionOpenAI, RegistroOpenAI, StoreOpenAI
from pydantic import BaseModel


class Metricas(BaseModel):
    documento_1: int
    documento_5: int
    cita_normalizada_5: int
    cita_literal_5: int
    mrr_documento_5: float
    p50_ms: float
    p95_ms: float


class FilaComparacion(BaseModel):
    variante: str
    modo_local: str
    formato: str
    casos: int
    local: Metricas
    openai: Metricas


class ResumenComparacion(BaseModel):
    fecha: str
    corpus_sha256: str
    informe_local_sha256: str
    vector_store_id: str
    archivos_enviados: int
    archivos_indexados: int
    archivos_fallidos: int
    archivos_cancelados: int
    bytes_indexados_openai: int
    peticiones_busqueda: int
    filas: list[FilaComparacion]


def resumir(raiz: Path, informe_local: Path, destino: Path) -> None:
    datos = raiz / "comparacion_openai"
    corpus = CorpusFicticio.model_validate_json((raiz / "corpus.json").read_bytes())
    local = InformeEvaluacion.model_validate_json(informe_local.read_bytes())
    carga = RegistroOpenAI.model_validate_json((datos / "carga_openai.json").read_bytes())
    store = StoreOpenAI.model_validate_json((datos / "store_indexado.json").read_bytes())
    if store.id != carga.vector_store_id or store.file_counts.total != len(corpus.documentos):
        raise AppError(CodigoError.ENTRADA_INVALIDA, "El estado del Store pertenece a otra carga.")
    if local.corpus_sha256 != hashlib.sha256((raiz / "corpus.json").read_bytes()).hexdigest():
        raise AppError(CodigoError.ENTRADA_INVALIDA, "Cambió el manifiesto evaluado.")
    respuestas = []
    recibos = []
    identificadores = {r.archivo: r.file_id for r in carga.archivos}
    for numero, referencia in enumerate(local.consultas, 1):
        archivo = datos / "respuestas" / f"{numero:03}.json"
        contenido = archivo.read_bytes()
        respuesta = MedicionOpenAI.model_validate_json(contenido)
        if (respuesta.vector_store_id, respuesta.corpus_sha256, respuesta.caso_id, respuesta.variante, respuesta.modo_local, respuesta.peticion) != (carga.vector_store_id, local.corpus_sha256, referencia.caso_id, referencia.variante, referencia.modo, BusquedaOpenAI(query=referencia.consulta)):
            raise AppError(CodigoError.ENTRADA_INVALIDA, "La respuesta no coincide con su comparación local.")
        if len(respuesta.respuesta.data) > 5:
            raise AppError(CodigoError.ENTRADA_INVALIDA, "El proveedor devolvió más de cinco resultados.")
        if any(identificadores.get(f.filename) != f.file_id for f in respuesta.respuesta.data):
            raise AppError(CodigoError.ENTRADA_INVALIDA, "Una fuente no pertenece a los archivos enviados.")
        respuestas.append(respuesta)
        recibos.append((archivo.name, hashlib.sha256(contenido).hexdigest(), respuesta.request_id))
    if len(respuestas) != 612 or len(list((datos / "respuestas").glob("*.json"))) != 612:
        raise AppError(CodigoError.ENTRADA_INVALIDA, "Se requieren exactamente 612 respuestas.")
    if {r.archivo for r in carga.archivos} != {d.archivo for d in corpus.documentos}:
        raise AppError(CodigoError.ENTRADA_INVALIDA, "La carga no contiene los mismos documentos.")
    filas = []
    for variante in ("libre", "natural_con_folio", "precisa"):
        for modo in ("texto", "vector", "hibrida"):
            indices = [i for i, r in enumerate(local.consultas) if r.variante == variante and r.modo == modo]
            filas.append(comparar(local, respuestas, indices, variante, modo, "todos"))
    for formato in ("digital", "escaneado", "mixto", "txt"):
        indices = [i for i, r in enumerate(local.consultas) if r.variante == "libre" and r.modo == "hibrida" and r.formato.value == formato]
        filas.append(comparar(local, respuestas, indices, "libre", "hibrida", formato))
    informe = ResumenComparacion(
        fecha=datetime.now(ZoneInfo("America/Mexico_City")).isoformat(),
        corpus_sha256=local.corpus_sha256,
        informe_local_sha256=hashlib.sha256(informe_local.read_bytes()).hexdigest(),
        vector_store_id=carga.vector_store_id, archivos_enviados=len(carga.archivos),
        archivos_indexados=store.file_counts.completed, archivos_fallidos=store.file_counts.failed,
        archivos_cancelados=store.file_counts.cancelled, bytes_indexados_openai=store.usage_bytes,
        peticiones_busqueda=len(respuestas), filas=filas,
    )
    destino.mkdir(exist_ok=True, parents=True)
    (destino / "comparacion.json").write_text(informe.model_dump_json(indent=2))
    (destino / "recibos_respuestas.tsv").write_text("archivo\tsha256\trequest_id\n" + "\n".join("\t".join((nombre, huella, identificador or "")) for nombre, huella, identificador in recibos) + "\n")
    lineas = ["# Comparación de recuperación con OpenAI", "", f"Fecha: {informe.fecha}.", "", "Mismos 240 originales y mismas 612 consultas. OpenAI usa búsqueda predeterminada en las tres repeticiones; modo local identifica la referencia comparada. Página@5 de OpenAI: no disponible.", "", "| Formulación | Referencia local | Formato | Casos | Documento@5 local | Documento@5 OpenAI | Cita literal@5 local | Cita literal@5 OpenAI | p50 local ms | p50 OpenAI ms |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for fila in filas:
        lineas.append(f"| {fila.variante} | {fila.modo_local} | {fila.formato} | {fila.casos} | {fila.local.documento_5} | {fila.openai.documento_5} | {fila.local.cita_literal_5} | {fila.openai.cita_literal_5} | {fila.local.p50_ms:.1f} | {fila.openai.p50_ms:.1f} |")
    lineas.extend(["", "Cita completa dentro de un solo pasaje o bloque devuelto del archivo esperado. Las unidades de recuperación y tamaños de fragmento pueden diferir entre proveedores. Los tiempos comparan API local con servicio remoto, no hardware ni condiciones idénticas.", "", "Corpus sintético, 68 casos sobre 16 documentos. Sin respuestas generadas, sin medición de razonamiento jurídico y sin extrapolación a expedientes reales."])
    (destino / "resumen.md").write_text("\n".join(lineas) + "\n")
    print("\n".join(lineas))


def comparar(local: InformeEvaluacion, respuestas: list[MedicionOpenAI], indices: list[int], variante: str, modo: str, formato: str) -> FilaComparacion:
    grupo_local = [local.consultas[i] for i in indices]
    grupo_openai = [respuestas[i] for i in indices]
    return FilaComparacion(
        variante=variante, modo_local=modo, formato=formato, casos=len(indices),
        local=metricas(
            [r.posicion_documento for r in grupo_local], [r.cita_en_top5 for r in grupo_local],
            [r.cita_literal_en_top5 for r in grupo_local], [r.segundos for r in grupo_local],
        ),
        openai=metricas(
            [r.posicion_documento for r in grupo_openai], [r.cita_normalizada_en_top5 for r in grupo_openai],
            [r.cita_literal_en_top5 for r in grupo_openai], [r.segundos for r in grupo_openai],
        ),
    )


def metricas(posiciones: list[int | None], citas: list[bool], literales: list[bool], segundos: list[float]) -> Metricas:
    tiempos = np.array(segundos) * 1000
    return Metricas(
        documento_1=sum(p == 1 for p in posiciones), documento_5=sum(p is not None for p in posiciones),
        cita_normalizada_5=sum(citas), cita_literal_5=sum(literales),
        mrr_documento_5=sum(1 / p for p in posiciones if p) / len(posiciones),
        p50_ms=float(np.percentile(tiempos, 50)), p95_ms=float(np.percentile(tiempos, 95)),
    )


if __name__ == "__main__":
    resumir(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
