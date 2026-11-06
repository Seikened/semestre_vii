import hashlib
import os
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from time import perf_counter
from uuid import UUID
from zoneinfo import ZoneInfo

import numpy as np
from app.contratos import Consulta, ModoBusqueda
from app.errores import AppError, CodigoError
from cliente_evaluacion import ClienteMotor
from modelos_corpus import (
    CargaDocumento,
    ControlExtraccion,
    CorpusFicticio,
    InformeEvaluacion,
    MedicionConsulta,
    RegistroCarga,
)
from pydantic import BaseModel

COLECCION = "Evaluación ampliada, 240 ficticios"


class ControlPagina(BaseModel):
    archivo: str
    formato: str
    variante: str
    pagina: int
    metodo_esperado: str
    metodo_observado: str
    anclas: int
    preservadas: int
    literales: int
    caracteres: int


class InformePaginas(BaseModel):
    fecha: str
    paginas: list[ControlPagina]


def ejecutar(raiz: Path) -> None:
    manifiesto = raiz / "corpus.json"
    contenido = manifiesto.read_bytes()
    corpus = CorpusFicticio.model_validate_json(contenido)
    huella = hashlib.sha256(contenido).hexdigest()
    cliente = ClienteMotor(Path(os.environ.get("API_KEY_FILE", "/clave_api/clave")))
    coleccion = cliente.coleccion(COLECCION)
    cargar(cliente, corpus, raiz, coleccion.id)
    evaluar(cliente, corpus, raiz, coleccion.id, huella)
    informe = InformeEvaluacion.model_validate_json((raiz / "evaluacion.json").read_text())
    escribir_resumen(informe, raiz)


def cargar(cliente: ClienteMotor, corpus: CorpusFicticio, raiz: Path, coleccion_id: UUID) -> None:
    existentes = cliente.documentos(coleccion_id)
    por_nombre = {d.nombre_original: d for d in existentes}
    if len(por_nombre) != len(existentes):
        raise AppError(CodigoError.ENTRADA_INVALIDA, "Hay nombres duplicados en la colección de evaluación.")
    destino = raiz / "carga.json"
    if destino.exists():
        registro = RegistroCarga.model_validate_json(destino.read_text())
        if registro.coleccion_id != str(coleccion_id):
            raise AppError(CodigoError.ENTRADA_INVALIDA, "El registro pertenece a otra colección.")
    else:
        registro = RegistroCarga(fecha=ahora(), coleccion_id=str(coleccion_id), documentos=[])
    if registro.pendiente and registro.pendiente not in por_nombre:
        raise AppError(
            CodigoError.ENTRADA_INVALIDA,
            f"El envío de {registro.pendiente} quedó incierto. Reconciliar el servidor antes de volver a enviarlo.",
        )
    recibos = {d.archivo: d for d in registro.documentos}
    for numero, esperado in enumerate(corpus.documentos, 1):
        inicio = perf_counter()
        existente = por_nombre.get(esperado.archivo)
        verificacion = 0
        if existente:
            original = cliente.original(existente.id)
            if hashlib.sha256(original).hexdigest() != esperado.sha256:
                raise AppError(CodigoError.DOCUMENTO_LECTURA, f"El documento cargado {esperado.archivo} no coincide con el corpus.")
            documento = existente
            previo = recibos.get(esperado.archivo)
            segundos = previo.segundos if previo else None
            verificacion = perf_counter() - inicio
        else:
            registro.pendiente = esperado.archivo
            guardar_registro(registro, destino)
            documento = cliente.subir(raiz / "archivos" / esperado.archivo, esperado.titulo, coleccion_id, esperado.sha256)
            segundos = perf_counter() - inicio
        recibos[esperado.archivo] = CargaDocumento(
            archivo=esperado.archivo, documento_id=str(documento.id), paginas=documento.paginas,
            paginas_ocr=documento.paginas_ocr, segundos=segundos, reutilizado=existente is not None,
            segundos_verificacion=verificacion,
        )
        registro.documentos = list(recibos.values())
        if registro.pendiente == esperado.archivo:
            registro.pendiente = None
        guardar_registro(registro, destino)
        if numero % 10 == 0:
            print(f"Indexados {numero}/{len(corpus.documentos)}: {esperado.archivo}", flush=True)


def guardar_registro(registro: RegistroCarga, destino: Path) -> None:
    temporal = destino.with_suffix(".tmp")
    temporal.write_text(registro.model_dump_json(indent=2))
    temporal.replace(destino)


def evaluar(cliente: ClienteMotor, corpus: CorpusFicticio, raiz: Path, coleccion_id: UUID, huella: str) -> None:
    documentos = cliente.documentos(coleccion_id)
    identificadores = {d.nombre_original: d.id for d in documentos}
    paginas = {}
    controles_pagina = []
    for documento in corpus.documentos:
        detalle = cliente.detalle(identificadores[documento.archivo])
        for esperada in documento.paginas:
            observada = next(p for p in detalle.paginas if p.numero == esperada.numero)
            paginas[documento.archivo, esperada.numero] = observada
            anclas = [c.texto for c in esperada.clausulas]
            texto = normalizar(observada.texto)
            literal = espacios(observada.texto)
            controles_pagina.append(ControlPagina(
                archivo=documento.archivo, formato=documento.formato.value, variante=documento.variante,
                pagina=esperada.numero, metodo_esperado=esperada.metodo, metodo_observado=observada.metodo.value,
                anclas=len(anclas), preservadas=sum(normalizar(a) in texto for a in anclas),
                literales=sum(espacios(a) in literal for a in anclas), caracteres=len(observada.texto),
            ))
    (raiz / "paginas.json").write_text(InformePaginas(fecha=ahora(), paginas=controles_pagina).model_dump_json(indent=2))
    controles = []
    resultados = []
    for numero, caso in enumerate(corpus.casos, 1):
        pagina = paginas[caso.archivo, caso.pagina]
        esperado = next(p for p in controles_pagina if p.archivo == caso.archivo and p.pagina == caso.pagina)
        controles.append(ControlExtraccion(
            caso_id=caso.id, archivo=caso.archivo, pagina=caso.pagina,
            metodo_esperado=esperado.metodo_esperado, metodo_observado=pagina.metodo.value,
            cita_preservada=normalizar(caso.cita) in normalizar(pagina.texto),
            cita_literal=espacios(caso.cita) in espacios(pagina.texto),
        ))
        for variante, texto in (("libre", caso.libre), ("natural_con_folio", caso.natural), ("precisa", caso.precisa)):
            for modo in ModoBusqueda:
                inicio = perf_counter()
                resultado = cliente.buscar(Consulta(texto=texto, modo=modo, limite=5, coleccion_id=coleccion_id))
                segundos = perf_counter() - inicio
                posicion_pagina = None
                posicion_documento = None
                cita = False
                cita_literal = False
                for posicion, fuente in enumerate(resultado.coincidencias, 1):
                    if fuente.nombre_original != caso.archivo:
                        continue
                    if posicion_documento is None:
                        posicion_documento = posicion
                    if fuente.pagina == caso.pagina:
                        if posicion_pagina is None:
                            posicion_pagina = posicion
                        cita = cita or normalizar(caso.cita) in normalizar(fuente.texto)
                        cita_literal = cita_literal or espacios(caso.cita) in espacios(fuente.texto)
                resultados.append(MedicionConsulta(
                    caso_id=caso.id, archivo=caso.archivo, formato=caso.formato, pagina=caso.pagina,
                    variante=variante, modo=modo.value, consulta=texto, posicion_pagina=posicion_pagina,
                    posicion_documento=posicion_documento, cita_en_top5=cita, cita_literal_en_top5=cita_literal,
                    segundos=segundos, fuentes=[f"{f.nombre_original}#p{f.pagina}" for f in resultado.coincidencias],
                ))
        if numero % 8 == 0:
            print(f"Evaluados {numero}/{len(corpus.casos)} casos, nueve consultas por caso", flush=True)
        informe = InformeEvaluacion(
            fecha=ahora(), coleccion_id=str(coleccion_id),
            corpus_sha256=huella,
            documentos=len(documentos), paginas=sum(d.paginas for d in documentos),
            paginas_ocr=sum(d.paginas_ocr for d in documentos), controles=controles, consultas=resultados,
        )
        (raiz / "evaluacion.json").write_text(informe.model_dump_json(indent=2))


def escribir_resumen(informe: InformeEvaluacion, raiz: Path) -> None:
    lineas = ["# Evaluación ampliada", "", f"Fecha: {informe.fecha}.", "", f"{informe.documentos} documentos, {informe.paginas} páginas lógicas, {informe.paginas_ocr} páginas OCR.", "",
              "| Consulta | Modo | Casos | Página@1 | Documento@5 | Página@5 | Cita completa normalizada en un pasaje@5 | Cita completa literal en un pasaje@5 | MRR página@5 | p50 ms | p95 ms |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for variante in ("libre", "natural_con_folio", "precisa"):
        for modo in ModoBusqueda:
            grupo = [r for r in informe.consultas if r.variante == variante and r.modo == modo.value]
            n = len(grupo)
            documento = sum(r.posicion_documento is not None for r in grupo)
            pagina = sum(r.posicion_pagina is not None for r in grupo)
            primera = sum(r.posicion_pagina == 1 for r in grupo)
            cita = sum(r.cita_en_top5 for r in grupo)
            literal = sum(r.cita_literal_en_top5 for r in grupo)
            mrr = sum(1 / r.posicion_pagina for r in grupo if r.posicion_pagina) / n
            tiempos = [r.segundos * 1000 for r in grupo]
            lineas.append(f"| {variante} | {modo.value} | {n} | {primera}/{n} | {documento}/{n} | {pagina}/{n} | {cita}/{n} | {literal}/{n} | {mrr:.3f} | {np.percentile(tiempos, 50):.1f} | {np.percentile(tiempos, 95):.1f} |")
    lineas.extend(["", "Cita literal conserva mayúsculas, acentos y puntuación; solo normaliza espacios. La comparación normalizada elimina además acentos, puntuación y diferencias de mayúsculas. Ninguna mide certeza de una respuesta jurídica.", "", "Carga serial y consultas contra la API interna, sin LLM. Corpus sintético con plantillas repetidas y distractores; no equivale a una evaluación independiente de archivos reales ni a una prueba de concurrencia."])
    (raiz / "resumen.md").write_text("\n".join(lineas) + "\n")
    print("\n".join(lineas), flush=True)


def normalizar(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in descompuesto if c.isalnum())


def espacios(texto: str) -> str:
    return " ".join(texto.split())


def ahora() -> str:
    return datetime.now(ZoneInfo("America/Mexico_City")).isoformat()


if __name__ == "__main__":
    ejecutar(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/corpus_amplio"))
