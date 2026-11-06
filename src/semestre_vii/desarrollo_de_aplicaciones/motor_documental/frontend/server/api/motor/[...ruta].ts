import { readFile } from 'node:fs/promises'

const rutas = [
  { patron: /^colecciones$/, metodos: ['GET', 'POST'] },
  { patron: /^documentos$/, metodos: ['GET', 'POST'] },
  { patron: /^documentos\/[0-9a-f-]{36}$/, metodos: ['GET', 'PATCH', 'DELETE'] },
  { patron: /^documentos\/[0-9a-f-]{36}\/archivo$/, metodos: ['GET'] },
  { patron: /^(buscar|chat)$/, metodos: ['POST'] }
]

export default defineEventHandler(async (event) => {
  const ruta = getRouterParam(event, 'ruta') || ''
  if (!rutas.some(regla => regla.patron.test(ruta) && regla.metodos.includes(event.method))) {
    throw createError({ statusCode: 404, statusMessage: 'Operación no disponible' })
  }
  const origen = getHeader(event, 'origin')
  if (origen && origen !== getRequestURL(event).origin) {
    throw createError({ statusCode: 403, statusMessage: 'Origen no autorizado' })
  }
  const longitud = Number(getHeader(event, 'content-length') || 0)
  if (longitud > 11 * 1024 * 1024) {
    throw createError({ statusCode: 413, statusMessage: 'El archivo supera 10 MiB' })
  }
  const config = useRuntimeConfig(event)
  const clave = (await readFile(config.apiKeyFile, 'utf8')).trim()
  const consulta = getRequestURL(event).search
  try {
    return await proxyRequest(event, `${config.motorUrl}/${ruta}${consulta}`, {
      headers: { 'X-API-Key': clave },
      fetchOptions: { redirect: 'error' }
    })
  } catch {
    throw createError({ statusCode: 502, statusMessage: 'El motor no está disponible. Reintenta en un momento.' })
  }
})
