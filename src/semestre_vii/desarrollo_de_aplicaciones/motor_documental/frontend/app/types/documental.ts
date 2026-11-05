export interface Coleccion {
  id: string
  nombre: string
}
export interface Documento {
  id: string
  coleccion_id: string
  titulo: string
  nombre_original: string
  paginas: number
  paginas_ocr: number
}
export interface Pagina {
  numero: number
  texto: string
  metodo: 'texto' | 'ocr'
}
export interface DetalleDocumento {
  documento: Documento
  paginas: Pagina[]
}
export interface Coincidencia {
  documento_id: string
  titulo: string
  nombre_original: string
  pagina: number
  metodo: string
  texto: string
  puntuacion: number
}
export interface ResultadoBusqueda {
  consulta: string
  modo: string
  coincidencias: Coincidencia[]
}
export type ModoBusqueda = 'hibrida' | 'vector' | 'texto'
export type EstadoAgente = 'sin-comprobar' | 'disponible' | 'no-disponible'
export interface MensajeChat {
  rol: 'user' | 'assistant'
  texto: string
}
export interface RespuestaChat {
  respuesta: string
  resultado: ResultadoBusqueda
  modelo: string
}
export interface TurnoChat extends RespuestaChat {
  id: string
  pregunta: string
}
export interface Turno {
  id: string
  pregunta: string
  resultado: ResultadoBusqueda
}
