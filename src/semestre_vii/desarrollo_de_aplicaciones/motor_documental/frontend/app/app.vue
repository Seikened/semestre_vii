<template>
  <UApp :locale="es">
    <div class="escritorio" :class="{ arrastrando }">
      <div v-if="arrastrando" class="zona-arrastre" aria-live="polite"><span class="marca-asterisco" aria-hidden="true">*</span><h2>Suelta tu documento aquí</h2><p>{{ coleccion ? 'Se indexará en ' + nombreContexto : 'PDF o TXT. Elegirás la colección si hay varios destinos.' }}</p><small>PostgreSQL + pgvector</small></div>
      <input ref="selectorArchivo" type="file" accept=".pdf,.txt,application/pdf,text/plain" class="sr-only" tabindex="-1" aria-label="Seleccionar documento para indexar" :disabled="ocupado || modalAbierto" @change="archivoSeleccionado">
      <aside id="biblioteca-documental" class="biblioteca" :class="{ 'biblioteca-abierta': bibliotecaAbierta }" aria-label="Biblioteca documental">
        <div class="marca-fila">
          <a href="/" class="marca marca-asterisco" aria-label="A* inicio">A*</a>
          <UButton class="cerrar-biblioteca" icon="i-lucide-x" color="neutral" variant="ghost" aria-label="Cerrar biblioteca" @click="bibliotecaAbierta = false" />
        </div>
        <div class="biblioteca-titulo"><h2>Biblioteca</h2><UButton icon="i-lucide-folder-plus" color="neutral" variant="ghost" aria-label="Crear colección" :disabled="ocupado || modalAbierto" @click="panelDocumento?.abrirColeccion()" /></div>
        <UFormField label="Colección" name="filtro-coleccion"><USelect v-model="filtroColeccion" :items="opcionesColecciones" :disabled="ocupado || modalAbierto" class="w-full" /></UFormField>
        <UButton class="boton-carga" icon="i-lucide-plus" color="neutral" variant="ghost" block :disabled="ocupado || modalAbierto" @click="panelDocumento?.abrirCarga(coleccion)">Cargar documento</UButton>
        <UInput v-model="filtroTitulo" icon="i-lucide-search" placeholder="Filtrar documentos" aria-label="Filtrar documentos por título" class="w-full" />
        <div class="biblioteca-resumen"><span>{{ estadoDocumentos === 'pending' ? 'Actualizando biblioteca...' : documentosFiltrados.length + (documentosFiltrados.length === 1 ? ' documento' : ' documentos') }}</span><UButton icon="i-lucide-refresh-cw" color="neutral" variant="ghost" size="xs" aria-label="Actualizar biblioteca" :loading="estadoDocumentos === 'pending'" @click="recargar" /></div>
        <div v-if="estadoDocumentos === 'pending'" class="carga-biblioteca" role="status"><USkeleton v-for="linea of 3" :key="linea" class="h-14 rounded-lg" /><span class="sr-only">Cargando biblioteca...</span></div>
        <UAlert v-if="errorDocumentos || errorColecciones" color="error" variant="soft" title="Biblioteca sin actualizar" description="Comprueba que el motor esté encendido y vuelve a intentar." icon="i-lucide-circle-alert" class="aviso-biblioteca">
          <template #actions><UButton color="error" variant="outline" size="sm" @click="recargar">Reintentar</UButton></template>
        </UAlert>
        <div v-else-if="estadoDocumentos !== 'pending' && !documentosFiltrados.length" class="vacio-biblioteca"><UIcon name="i-lucide-folder-open" /><p>{{ filtroTitulo ? 'No hay títulos con ese texto.' : 'Esta colección aún no tiene documentos.' }}</p><UButton v-if="filtroTitulo" color="neutral" variant="link" @click="filtroTitulo = ''">Limpiar filtro</UButton></div>
        <div v-if="estadoDocumentos !== 'pending' && documentosFiltrados.length" class="lista-documentos">
          <button v-for="documento of documentosFiltrados" :key="documento.id" class="documento" @click="abrirDocumento(documento.id)">
            <span class="icono-documento"><UIcon name="i-lucide-file-text" /></span>
            <span><strong>{{ documento.titulo }}</strong><small>{{ documento.paginas }} {{ documento.paginas === 1 ? 'página' : 'páginas' }} · {{ documento.paginas_ocr ? documento.paginas_ocr + ' con OCR' : 'Texto digital' }}</small></span><UIcon name="i-lucide-chevron-right" class="flecha-documento" />
          </button>
        </div>
      </aside>
      <main class="area-consulta">
        <header class="cabecera">
          <div class="navegacion-consulta">
            <UButton class="abrir-biblioteca" icon="i-lucide-panel-left" color="neutral" variant="outline" :aria-expanded="bibliotecaAbierta" aria-controls="biblioteca-documental" @click="bibliotecaAbierta = !bibliotecaAbierta">Biblioteca</UButton>
            <nav aria-label="Tipo de consulta">
              <UButton :variant="operacion === 'chat' ? 'solid' : 'ghost'" :color="operacion === 'chat' ? 'primary' : 'neutral'" :aria-pressed="operacion === 'chat'" @click="operacion = 'chat'">A*</UButton>
              <UButton :variant="operacion === 'busqueda' ? 'solid' : 'ghost'" :color="operacion === 'busqueda' ? 'primary' : 'neutral'" icon="i-lucide-scan-search" :aria-pressed="operacion === 'busqueda'" @click="operacion = 'busqueda'">Buscar fragmentos</UButton>
            </nav>
          </div>
          <div class="acciones"><UBadge color="neutral" variant="subtle" class="estado-conexion">{{ operacion === 'busqueda' ? 'Motor local' : estadoAgente === 'disponible' ? 'A* disponible' : estadoAgente === 'no-disponible' ? 'A* no disponible' : 'Chat documental' }}</UBadge><ClientOnly><UButton :icon="colorMode.value === 'dark' ? 'i-lucide-sun' : 'i-lucide-moon'" color="neutral" variant="ghost" :aria-label="colorMode.value === 'dark' ? 'Activar tema claro' : 'Activar tema oscuro'" @click="colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'" /></ClientOnly></div>
        </header>
        <div class="contexto-coleccion"><UIcon name="i-lucide-folder" /><span>{{ nombreContexto }}</span></div>
        <ChatDocumental v-show="operacion === 'chat'" v-model:modo="modo" :coleccion :activo="operacion === 'chat'" :bloqueado="buscando || guardandoDocumento || modalAbierto" @estado="estadoAgente = $event" @ocupado="chatOcupado = $event" @adjuntar="adjuntarDocumento" />
        <template v-if="operacion === 'busqueda'">
          <section ref="panelBusqueda" class="conversacion" aria-label="Consulta de documentos" :aria-busy="buscando">
            <div v-if="!turnos.length && !buscando" class="bienvenida">
              <div class="icono-bienvenida"><UIcon name="i-lucide-scan-search" /></div><p class="etiqueta">Recuperación local</p>
              <h1>¿Qué quieres encontrar?</h1><p class="introduccion">Busca un pasaje y vuelve a su página original.</p>
              <div class="sugerencias"><UButton v-for="ejemplo of ejemplos" :key="ejemplo" color="neutral" variant="outline" trailing-icon="i-lucide-arrow-up-right" @click="consultar(ejemplo)">{{ ejemplo }}</UButton></div>
              <UButton class="nota-arrastre" icon="i-lucide-paperclip" color="neutral" variant="link" :disabled="ocupado || modalAbierto" @click="adjuntarDocumento">Arrastra un PDF o TXT aquí, o adjúntalo</UButton>
            </div>
            <UChatMessages v-else :status="buscando ? 'submitted' : 'ready'" :should-auto-scroll="false" :should-scroll-to-bottom="false" :auto-scroll="false" class="historial">
              <div v-for="turno of turnos" :id="turno.id" :key="turno.id" class="turno-consulta">
                <UChatMessage :id="turno.id + '-pregunta'" role="user" :parts="[{ type: 'text', text: turno.pregunta }]" variant="soft" side="right" />
                <UChatMessage :id="turno.id + '-fuentes'" role="assistant" :parts="[]" :avatar="{ icon: 'i-lucide-library' }"><template #content><ResultadosConsulta :resultado="turno.resultado" /></template></UChatMessage>
              </div>
              <UChatMessage v-if="buscando" id="busqueda-pendiente" role="user" :parts="[{ type: 'text', text: ultimaConsulta }]" variant="soft" side="right" />
              <template #indicator><ActividadMotor tipo="busqueda" :modo /></template>
            </UChatMessages>
          </section>
          <div class="compositor">
            <UAlert v-if="aviso" color="error" variant="soft" title="La consulta no se completó" :description="aviso" icon="i-lucide-circle-alert" class="aviso-consulta"><template #actions><UButton color="error" variant="outline" size="sm" :disabled="buscando" @click="consultar(ultimaConsulta)">Reintentar</UButton></template></UAlert>
            <UChatPrompt v-model="pregunta" :disabled="ocupado || modalAbierto" :maxlength="1000" placeholder="Busca en tus documentos" :autofocus="false" :ui="{ base: 'text-base leading-7' }" aria-label="Consulta documental" @submit="consultar(pregunta)">
              <template #footer><div class="acciones-compositor"><UButton type="button" class="boton-adjuntar" icon="i-lucide-plus" color="neutral" variant="ghost" aria-label="Adjuntar documento" :disabled="ocupado || modalAbierto" @click="adjuntarDocumento" /><USelect v-model="modo" :items="opcionesModos" :disabled="ocupado || modalAbierto" icon="i-lucide-scan-search" variant="ghost" color="neutral" size="sm" aria-label="Modo de búsqueda" class="selector-modo" /></div><UChatPromptSubmit :loading="buscando" :disabled="ocupado || modalAbierto || !pregunta.trim()" size="lg" aria-label="Buscar documentos" /></template>
            </UChatPrompt>
            <p class="pie-consulta">Las puntuaciones ordenan resultados; no representan certeza.</p>
          </div>
        </template>
      </main>
    </div>
    <DocumentoModal ref="panelDocumento" :colecciones="colecciones || []" @actualizado="recargar" @abierto="modalAbierto = $event" @ocupado="guardandoDocumento = $event" />
  </UApp>
</template>

<script setup lang="ts">
import { es } from '@nuxt/ui/locale'
import type { Coleccion, Documento, EstadoAgente, ModoBusqueda, ResultadoBusqueda, Turno } from '~/types/documental'

const filtroColeccion = ref('todas')
const coleccion = computed(() => filtroColeccion.value === 'todas' ? '' : filtroColeccion.value)
const filtroTitulo = ref('')
const operacion = ref<'chat' | 'busqueda'>('chat')
const estadoAgente = ref<EstadoAgente>('sin-comprobar')
const chatOcupado = ref(false)
const bibliotecaAbierta = ref(false)
const panelDocumento = useTemplateRef('panelDocumento')
const colorMode = useColorMode()
const toast = useToast()
const selectorArchivo = useTemplateRef('selectorArchivo')
const guardandoDocumento = ref(false)
const modalAbierto = ref(false)
const arrastrando = ref(false)
let entradasArrastre = 0
const { data: colecciones, error: errorColecciones, refresh: refreshColecciones } = await useFetch<Coleccion[]>('/api/motor/colecciones')
const { data: documentos, status: estadoDocumentos, error: errorDocumentos, refresh: refreshDocumentos } = await useFetch<Documento[]>('/api/motor/documentos', { query: computed(() => coleccion.value ? { coleccion_id: coleccion.value } : {}) })
const opcionesColecciones = computed(() => [{ label: 'Todas las colecciones', value: 'todas' }, ...(colecciones.value || []).map(grupo => ({ label: grupo.nombre, value: grupo.id }))])
const nombreContexto = computed(() => colecciones.value?.find(grupo => grupo.id === coleccion.value)?.nombre || 'Todas las colecciones')
const documentosFiltrados = computed(() => (documentos.value || []).filter(documento => documento.titulo.toLocaleLowerCase('es').includes(filtroTitulo.value.trim().toLocaleLowerCase('es'))))

const pregunta = ref('')
const modo = ref<ModoBusqueda>('hibrida')
const buscando = ref(false)
const ocupado = computed(() => chatOcupado.value || buscando.value || guardandoDocumento.value)
const aviso = ref('')
const ultimaConsulta = ref('')
const turnos = ref<Turno[]>([])
const panelBusqueda = useTemplateRef('panelBusqueda')
const opcionesModos = [{ label: 'Híbrida', value: 'hibrida' }, { label: 'Semántica', value: 'vector' }, { label: 'Textual', value: 'texto' }]
const ejemplos = ['¿Qué penalización tiene salir antes del local Cedro?', '¿Cuándo se devuelve el depósito de Aurora?', '¿Qué pasa si se retrasa la entrega de Bruma?']

watch(coleccion, () => {
  turnos.value = []
  aviso.value = ''
  ultimaConsulta.value = ''
  filtroTitulo.value = ''
})

watch([modalAbierto, ocupado], limpiarArrastre)

onMounted(() => {
  window.addEventListener('dragenter', entrarArrastre)
  window.addEventListener('dragleave', salirArrastre)
  window.addEventListener('dragover', sobreArrastre)
  window.addEventListener('drop', soltarArchivo)
  window.addEventListener('dragend', limpiarArrastre)
  window.addEventListener('blur', limpiarArrastre)
})

onBeforeUnmount(() => {
  window.removeEventListener('dragenter', entrarArrastre)
  window.removeEventListener('dragleave', salirArrastre)
  window.removeEventListener('dragover', sobreArrastre)
  window.removeEventListener('drop', soltarArchivo)
  window.removeEventListener('dragend', limpiarArrastre)
  window.removeEventListener('blur', limpiarArrastre)
})

function adjuntarDocumento() {
  if (!ocupado.value && !modalAbierto.value) selectorArchivo.value?.click()
}

function archivoSeleccionado(evento: Event) {
  const input = evento.target
  if (!(input instanceof HTMLInputElement)) return
  const archivos = Array.from(input.files || [])
  input.value = ''
  recibirArchivos(archivos)
}

function recibirArchivos(archivos: File[]) {
  limpiarArrastre()
  if (!archivos.length) return
  if (ocupado.value) {
    toast.add({ title: 'Hay una operación en curso', description: 'Espera a que termine para añadir otro documento.', color: 'warning' })
    return
  }
  if (archivos.length !== 1) {
    toast.add({ title: 'Un documento a la vez', description: 'Suelta un PDF o TXT. Los archivos no se han enviado.', color: 'warning' })
    return
  }
  bibliotecaAbierta.value = false
  panelDocumento.value?.recibirArchivo(archivos[0]!, coleccion.value)
}

function esArrastreArchivo(evento: DragEvent) {
  return Array.from(evento.dataTransfer?.types || []).includes('Files')
}

function entrarArrastre(evento: DragEvent) {
  if (!esArrastreArchivo(evento)) return
  evento.preventDefault()
  if (ocupado.value || modalAbierto.value) return
  entradasArrastre++
  arrastrando.value = true
}

function salirArrastre(evento: DragEvent) {
  if (!esArrastreArchivo(evento)) return
  entradasArrastre = Math.max(0, entradasArrastre - 1)
  if (!entradasArrastre) arrastrando.value = false
}

function sobreArrastre(evento: DragEvent) {
  if (!esArrastreArchivo(evento)) return
  evento.preventDefault()
  if (evento.dataTransfer) evento.dataTransfer.dropEffect = ocupado.value ? 'none' : 'copy'
}

function soltarArchivo(evento: DragEvent) {
  if (!esArrastreArchivo(evento)) return
  evento.preventDefault()
  recibirArchivos(Array.from(evento.dataTransfer?.files || []))
}

function limpiarArrastre() {
  entradasArrastre = 0
  arrastrando.value = false
}

async function recargar() {
  const gruposAnteriores = colecciones.value
  const documentosAnteriores = documentos.value
  const coleccionAnterior = coleccion.value
  await Promise.all([refreshColecciones(), refreshDocumentos()])
  if (errorColecciones.value) colecciones.value = gruposAnteriores
  if (errorDocumentos.value && coleccion.value === coleccionAnterior) documentos.value = documentosAnteriores
}

function abrirDocumento(id: string) {
  bibliotecaAbierta.value = false
  panelDocumento.value?.verDocumento(id)
}

async function consultar(texto: string) {
  texto = texto.trim()
  if (!texto || texto.length > 1000 || ocupado.value || modalAbierto.value) return
  buscando.value = true
  aviso.value = ''
  ultimaConsulta.value = texto
  pregunta.value = ''
  await nextTick()
  panelBusqueda.value?.scrollTo({ top: panelBusqueda.value.scrollHeight })
  try {
    const resultado = await $fetch<ResultadoBusqueda>('/api/motor/buscar', { method: 'POST', body: { texto, modo: modo.value, limite: 5, coleccion_id: coleccion.value || null }, retry: 0 })
    const id = crypto.randomUUID()
    turnos.value.push({ id, pregunta: texto, resultado })
    await nextTick()
    const turno = document.getElementById(id)
    const panel = panelBusqueda.value
    if (turno && panel) panel.scrollTop += turno.getBoundingClientRect().top - panel.getBoundingClientRect().top - 16
  } catch {
    aviso.value = 'Tu pregunta se conserva. Comprueba que el motor esté encendido y vuelve a intentar.'
    pregunta.value = texto
  } finally {
    buscando.value = false
  }
}
</script>
