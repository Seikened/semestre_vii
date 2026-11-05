<template>
  <UModal v-model:open="abierto" :title="tituloPanel" :description="descripcionPanel" :dismissible="!guardando" :close="!guardando" :ui="{ content: 'max-w-2xl text-default', body: 'space-y-5', footer: 'justify-end flex-wrap' }" @after:leave="limpiarAlCerrar">
    <template #body>
      <UAlert v-if="error" color="error" variant="soft" title="No se completó la operación" :description="error" icon="i-lucide-circle-alert" />
      <div v-if="documentoCreado" class="carga-exitosa" role="status">
        <span class="icono-exito"><UIcon name="i-lucide-check" /></span>
        <h3>Documento indexado</h3><p>{{ documentoCreado.titulo }}</p>
        <div class="datos-procesamiento"><div><strong>{{ documentoCreado.paginas }}</strong><span>{{ documentoCreado.paginas === 1 ? 'página' : 'páginas' }}</span></div><div><strong>{{ documentoCreado.paginas_ocr }}</strong><span>con OCR</span></div></div>
        <p class="ayuda">{{ documentoCreado.nombre_original }} ya se puede consultar en su colección.</p>
        <UBadge color="neutral" variant="subtle" icon="i-lucide-database" class="mt-4">PostgreSQL + pgvector</UBadge>
      </div>
      <UForm v-else-if="vista === 'coleccion'" id="formulario-coleccion" :state="{ nombre: nombreColeccion }" :validate="validarColeccion" novalidate class="formulario" @submit="crearColeccion">
        <UFormField label="Nombre de la colección" name="nombre" required><UInput v-model="nombreColeccion" required maxlength="120" placeholder="Ej. Arrendamientos 2026" :disabled="guardando" class="w-full" autofocus /></UFormField>
      </UForm>
      <UForm v-else-if="vista === 'carga'" id="formulario-carga" :state="{ titulo, coleccion_id: grupoCarga, archivo }" :validate="validarCarga" novalidate class="formulario" :aria-busy="guardando" @submit="cargarDocumento">
        <div v-if="guardando" ref="panelProcesamiento"><ActividadMotor tipo="indexacion" :nombre-archivo="archivo?.name" /></div>
        <UFormField label="Título" name="titulo" required><UInput v-model="titulo" required maxlength="200" placeholder="Se toma del nombre del archivo" :disabled="guardando" class="w-full" /></UFormField>
        <UFormField label="Colección" name="coleccion_id" required><USelect v-model="grupoCarga" :items="colecciones" value-key="id" label-key="nombre" placeholder="Selecciona una colección" :disabled="guardando" required class="w-full" /></UFormField>
        <p v-if="!colecciones.length" class="ayuda">Crea una colección desde la biblioteca antes de incorporar el archivo.</p>
        <p v-else-if="!grupoCarga" class="ayuda">Elige dónde guardar el documento. Después pulsa Indexar documento.</p>
        <UFormField label="Archivo" name="archivo" required>
          <UFileUpload v-model="archivo" :dropzone="false" accept=".pdf,.txt,application/pdf,text/plain" label="Selecciona o arrastra tu archivo" description="PDF o TXT UTF-8, hasta 10 MiB" layout="list" :file-image="false" icon="i-lucide-paperclip" :disabled="guardando" :file-delete="!guardando" required class="w-full" @reject="error = 'Elige un archivo PDF o TXT.'" />
        </UFormField>
      </UForm>
      <div v-else-if="cargandoDetalle" class="carga-detalle" role="status"><UIcon name="i-lucide-loader-circle" class="motion-safe:animate-spin" /><span>Cargando documento...</span></div>
      <div v-else-if="detalle" class="detalle-documento">
        <UAlert v-if="guardado" color="success" variant="soft" title="Cambios guardados" icon="i-lucide-check" />
        <div class="metadatos-documento"><UBadge color="neutral" variant="subtle">{{ detalle.documento.paginas }} {{ detalle.documento.paginas === 1 ? 'página' : 'páginas' }}</UBadge><UBadge color="neutral" variant="outline">{{ detalle.documento.paginas_ocr }} con OCR</UBadge><span>{{ detalle.documento.nombre_original }}</span></div>
        <UForm id="formulario-edicion" :state="{ titulo, coleccion_id: grupoCarga }" :validate="validarDocumento" novalidate class="formulario" @submit="editarDocumento">
          <UFormField label="Título" name="titulo" required><UInput v-model="titulo" required maxlength="200" :disabled="guardando" class="w-full" /></UFormField>
          <UFormField label="Colección" name="coleccion_id" required><USelect v-model="grupoCarga" :items="colecciones" value-key="id" label-key="nombre" :disabled="guardando" required class="w-full" /></UFormField>
          <div class="acciones"><UButton type="submit" :loading="guardando" :disabled="guardando">Guardar cambios</UButton><UButton :to="'/api/motor/documentos/' + detalle.documento.id + '/archivo'" target="_blank" color="neutral" variant="outline" trailing-icon="i-lucide-arrow-up-right">Abrir original</UButton></div>
        </UForm>
        <div class="paginas-documento"><h3>Texto por página</h3><UAccordion :items="paginas" type="multiple"><template #body="{ item }"><p class="texto-pagina">{{ item.texto }}</p></template></UAccordion></div>
        <div class="zona-retirar"><h3>Retirar documento</h3><p>Dejará de aparecer en consultas y descargas. Su registro se conserva.</p><UCheckbox v-model="confirmarRetiro" label="Confirmo retirar este documento" :disabled="guardando" /><UButton color="error" variant="soft" :disabled="!confirmarRetiro || guardando" :loading="guardando" icon="i-lucide-archive" @click="retirarDocumento">Retirar documento</UButton></div>
      </div>
      <UButton v-else-if="vista === 'detalle' && error" color="neutral" variant="outline" icon="i-lucide-refresh-cw" @click="cargarDetalle">Reintentar apertura</UButton>
    </template>
    <template #footer>
      <template v-if="documentoCreado"><UButton color="neutral" variant="outline" @click="abrirCarga(grupoCarga)">Cargar otro</UButton><UButton icon="i-lucide-file-text" @click="verDocumento(documentoCreado.id)">Ver documento</UButton></template>
      <template v-else-if="vista === 'coleccion'"><UButton color="neutral" variant="outline" :disabled="guardando" @click="abierto = false">Cancelar</UButton><UButton type="submit" form="formulario-coleccion" :loading="guardando" :disabled="guardando" icon="i-lucide-folder-plus">Crear colección</UButton></template>
      <template v-else-if="vista === 'carga'"><UButton color="neutral" variant="outline" :disabled="guardando" @click="abierto = false">Cancelar</UButton><UButton type="submit" form="formulario-carga" :loading="guardando" :disabled="guardando || !colecciones.length" icon="i-lucide-upload">{{ guardando ? 'Indexando...' : 'Indexar documento' }}</UButton></template>
      <UButton v-else color="neutral" variant="outline" :disabled="guardando" @click="abierto = false">Cerrar</UButton>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { Coleccion, DetalleDocumento, Documento } from '~/types/documental'

const { colecciones } = defineProps<{ colecciones: Coleccion[] }>()
const emit = defineEmits<{ actualizado: [], abierto: [valor: boolean], ocupado: [valor: boolean] }>()
const toast = useToast()
const abierto = ref(false)
const vista = ref<'carga' | 'coleccion' | 'detalle'>('carga')
const detalle = ref<DetalleDocumento>()
const documentoCreado = ref<Documento>()
const titulo = ref('')
const nombreColeccion = ref('')
const grupoCarga = ref('')
const archivo = ref<File | null | undefined>(null)
const confirmarRetiro = ref(false)
const guardando = ref(false)
const guardado = ref(false)
const cargandoDetalle = ref(false)
const error = ref('')
const documentoId = ref('')
const panelProcesamiento = useTemplateRef('panelProcesamiento')
let solicitudDetalle = 0
const tituloPanel = computed(() => vista.value === 'carga' ? 'Incorporar documento' : vista.value === 'coleccion' ? 'Nueva colección' : 'Documento')
const descripcionPanel = computed(() => vista.value === 'carga' ? 'Usa únicamente documentos ficticios.' : vista.value === 'coleccion' ? 'Agrupa contratos para acotar tus consultas.' : 'Revisa el texto extraído, sus páginas y el original.')
const paginas = computed(() => detalle.value?.paginas.map(pagina => ({ value: String(pagina.numero), label: 'Página ' + pagina.numero + ' · ' + (pagina.metodo === 'ocr' ? 'OCR' : 'Texto digital'), texto: pagina.texto })) || [])

watch(abierto, valor => emit('abierto', valor), { flush: 'sync' })
watch(guardando, valor => emit('ocupado', valor), { flush: 'sync' })
watch(archivo, (nuevo, anterior) => {
  error.value = nuevo ? validarArchivo() || '' : ''
  if (!nuevo) return
  if (!titulo.value.trim() || (anterior && titulo.value === tituloArchivo(anterior))) titulo.value = tituloArchivo(nuevo)
}, { flush: 'sync' })

watch([titulo, grupoCarga], () => {
  guardado.value = false
}, { flush: 'sync' })

function limpiar() {
  solicitudDetalle++
  detalle.value = undefined
  documentoCreado.value = undefined
  archivo.value = null
  titulo.value = ''
  nombreColeccion.value = ''
  confirmarRetiro.value = false
  guardado.value = false
  error.value = ''
  cargandoDetalle.value = false
}

function limpiarAlCerrar() {
  if (!abierto.value) limpiar()
}

function abrirCarga(grupo = '') {
  if (guardando.value) return
  limpiar()
  grupoCarga.value = grupo || (colecciones.length === 1 ? colecciones[0]!.id : '')
  vista.value = 'carga'
  abierto.value = true
}

function abrirColeccion() {
  if (guardando.value) return
  limpiar()
  vista.value = 'coleccion'
  abierto.value = true
}

function tituloArchivo(entrada: File) {
  return (entrada.name.replace(/\.[^.]+$/, '') || entrada.name).slice(0, 200)
}

async function recibirArchivo(entrada: File, grupo = '') {
  if (guardando.value || cargandoDetalle.value || (abierto.value && (vista.value !== 'carga' || documentoCreado.value))) {
    toast.add({ title: 'Termina la operación abierta', description: 'El documento actual se conserva. Cierra este panel antes de añadir otro.', color: 'warning' })
    return
  }
  const nuevaCarga = !abierto.value
  if (nuevaCarga) abrirCarga(grupo)
  archivo.value = entrada
  error.value = validarArchivo() || ''
  if (!error.value && nuevaCarga && grupoCarga.value) await cargarDocumento()
}

function validarColeccion() {
  return nombreColeccion.value.trim() ? [] : [{ name: 'nombre', message: 'Escribe un nombre para la colección.' }]
}

function validarDocumento() {
  const errores = []
  if (!titulo.value.trim()) errores.push({ name: 'titulo', message: 'Escribe un título para el documento.' })
  if (!grupoCarga.value) errores.push({ name: 'coleccion_id', message: 'Selecciona una colección.' })
  return errores
}

function validarCarga() {
  const errores = validarDocumento()
  const mensaje = validarArchivo()
  if (mensaje) errores.push({ name: 'archivo', message: mensaje })
  return errores
}

function validarArchivo() {
  if (!archivo.value) return 'Selecciona un PDF o TXT.'
  if (!/\.(pdf|txt)$/i.test(archivo.value.name)) return 'El formato debe ser PDF o TXT.'
  if (!archivo.value.size) return 'El archivo está vacío. Elige uno que contenga texto o páginas.'
  if (archivo.value.size > 10 * 1024 * 1024) return 'El archivo supera 10 MiB. Elige uno más pequeño.'
}

function informarError(fallo: unknown) {
  const codigo = fallo instanceof Error && 'statusCode' in fallo ? fallo.statusCode : undefined
  if (codigo === 409) error.value = 'Ya existe una colección con ese nombre. Elige otro.'
  else if (codigo === 413) error.value = 'El archivo supera el tamaño permitido de 10 MiB. Elige uno más pequeño.'
  else if (codigo === 415 || codigo === 422) error.value = 'Revisa el título, la colección y que el archivo sea un PDF o TXT válido. Los datos se conservan para reintentar.'
  else error.value = 'El motor no pudo confirmar la operación. Los datos se conservan. Actualiza la biblioteca antes de volver a enviarlos para comprobar si se guardaron.'
}

async function crearColeccion() {
  if (guardando.value) return
  guardando.value = true
  error.value = ''
  try {
    const creada = await $fetch<Coleccion>('/api/motor/colecciones', { method: 'POST', body: { nombre: nombreColeccion.value.trim() }, retry: 0 })
    emit('actualizado')
    toast.add({ title: 'Colección creada', description: creada.nombre, color: 'success', icon: 'i-lucide-folder-check' })
    abierto.value = false
  } catch (fallo) {
    informarError(fallo)
  } finally {
    guardando.value = false
  }
}

async function cargarDocumento() {
  if (guardando.value) return
  const errores = validarCarga()
  if (errores.length || !archivo.value) {
    error.value = errores.map(entrada => entrada.message).join(' ')
    return
  }
  guardando.value = true
  error.value = ''
  const datos = new FormData()
  datos.append('archivo', archivo.value)
  datos.append('titulo', titulo.value.trim())
  datos.append('coleccion_id', grupoCarga.value)
  await nextTick()
  panelProcesamiento.value?.scrollIntoView({ block: 'nearest' })
  try {
    const respuesta = await $fetch<DetalleDocumento>('/api/motor/documentos', { method: 'POST', body: datos, retry: 0 })
    documentoCreado.value = respuesta.documento
    emit('actualizado')
  } catch (fallo) {
    informarError(fallo)
  } finally {
    guardando.value = false
  }
}

async function verDocumento(id: string) {
  if (guardando.value) return
  limpiar()
  documentoId.value = id
  vista.value = 'detalle'
  abierto.value = true
  await cargarDetalle()
}

async function cargarDetalle() {
  const solicitud = ++solicitudDetalle
  cargandoDetalle.value = true
  error.value = ''
  try {
    const respuesta = await $fetch<DetalleDocumento>('/api/motor/documentos/' + documentoId.value)
    if (solicitud !== solicitudDetalle || !abierto.value) return
    detalle.value = respuesta
    titulo.value = respuesta.documento.titulo
    grupoCarga.value = respuesta.documento.coleccion_id
  } catch {
    if (solicitud !== solicitudDetalle || !abierto.value) return
    error.value = 'No se pudo abrir el documento. Comprueba que el motor esté encendido y reintenta; si fue retirado, actualiza la biblioteca.'
  } finally {
    if (solicitud === solicitudDetalle) cargandoDetalle.value = false
  }
}

async function editarDocumento() {
  if (!detalle.value || guardando.value) return
  guardando.value = true
  guardado.value = false
  error.value = ''
  try {
    detalle.value = await $fetch<DetalleDocumento>('/api/motor/documentos/' + detalle.value.documento.id, { method: 'PATCH', body: { titulo: titulo.value.trim(), coleccion_id: grupoCarga.value }, retry: 0 })
    guardado.value = true
    emit('actualizado')
  } catch (fallo) {
    informarError(fallo)
  } finally {
    guardando.value = false
  }
}

async function retirarDocumento() {
  if (!detalle.value || !confirmarRetiro.value || guardando.value) return
  guardando.value = true
  error.value = ''
  try {
    await $fetch('/api/motor/documentos/' + detalle.value.documento.id, { method: 'DELETE', retry: 0 })
    emit('actualizado')
    toast.add({ title: 'Documento retirado', description: detalle.value.documento.titulo, color: 'success', icon: 'i-lucide-archive' })
    abierto.value = false
  } catch (fallo) {
    informarError(fallo)
  } finally {
    guardando.value = false
  }
}

defineExpose({ abrirCarga, abrirColeccion, verDocumento, recibirArchivo })
</script>
