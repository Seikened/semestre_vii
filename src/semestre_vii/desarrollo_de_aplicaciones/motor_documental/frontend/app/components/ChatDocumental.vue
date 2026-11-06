<template>
  <div class="interfaz-chat">
    <section ref="panelConversacion" class="conversacion" aria-label="Conversación con A*" :aria-busy="enviando">
      <div v-if="!turnos.length && !enviando" class="bienvenida">
        <div class="icono-bienvenida marca-asterisco" aria-hidden="true">*</div>
        <h1>¿Qué quieres encontrar?</h1>
        <p class="introduccion">Pregunta a A*. Cada respuesta, con sus fuentes.</p>
        <div class="sugerencias"><UButton v-for="ejemplo of ejemplos" :key="ejemplo" color="neutral" variant="outline" trailing-icon="i-lucide-arrow-up-right" @click="conversar(ejemplo)">{{ ejemplo }}</UButton></div>
        <UButton class="nota-arrastre" icon="i-lucide-paperclip" color="neutral" variant="link" :disabled="enviando || bloqueado" @click="emit('adjuntar')">Arrastra un PDF o TXT aquí, o adjúntalo</UButton>
      </div>
      <UChatMessages v-else :status="enviando ? 'submitted' : 'ready'" :should-auto-scroll="false" :should-scroll-to-bottom="false" :auto-scroll="false" class="historial">
        <div v-for="turno of turnos" :id="turno.id" :key="turno.id" class="turno-consulta">
          <UChatMessage :id="turno.id + '-pregunta'" role="user" :parts="[{ type: 'text', text: turno.pregunta }]" variant="soft" side="right" />
          <UChatMessage :id="turno.id + '-respuesta'" role="assistant" :parts="[]" :avatar="{ icon: 'i-lucide-asterisk' }">
            <template #content>
              <div class="respuesta-chat">
                <p class="etiqueta">A*</p>
                <p class="respuesta-agente"><template v-for="(parte, indice) of partesRespuesta(turno)" :key="indice"><a v-if="parte.fuente" :href="'#fuente-' + turno.id + '-' + parte.fuente" class="cita-respuesta" :aria-label="'Ver fuente ' + parte.fuente" @click.prevent="irAFuente(turno.id, parte.fuente)">{{ parte.texto }}</a><span v-else>{{ parte.texto }}</span></template></p>
                <UAccordion v-if="turno.resultado.coincidencias.length" v-model="fuentesAbiertas[turno.id]" :items="[{ label: turno.resultado.coincidencias.length + (turno.resultado.coincidencias.length === 1 ? ' fuente citada' : ' fuentes citadas'), value: 'fuentes', icon: 'i-lucide-book-open' }]" :ui="{ content: 'data-[state=open]:animate-none data-[state=closed]:animate-none' }" class="fuentes-chat">
                  <template #body><ResultadosConsulta :resultado="turno.resultado" :id-prefijo="'fuente-' + turno.id + '-'" /></template>
                </UAccordion>
                <p v-else class="ayuda">Esta respuesta no cita documentos. Usa Buscar fragmentos para revisar la evidencia disponible.</p>
              </div>
            </template>
          </UChatMessage>
        </div>
        <UChatMessage v-if="enviando" id="pregunta-pendiente" role="user" :parts="[{ type: 'text', text: pendiente }]" variant="soft" side="right" />
        <template #indicator><ActividadMotor tipo="chat" :modo /></template>
      </UChatMessages>
    </section>
    <div class="compositor">
      <UAlert v-if="aviso" color="error" variant="soft" title="El mensaje no se completó" :description="aviso" icon="i-lucide-circle-alert" class="aviso-consulta"><template #actions><UButton v-if="ultimaPregunta" color="error" variant="outline" size="sm" :disabled="enviando" @click="conversar(ultimaPregunta)">Reintentar</UButton></template></UAlert>
      <UChatPrompt v-model="pregunta" :disabled="enviando || bloqueado" :maxlength="1000" placeholder="Pregunta a A*" :autofocus="false" :ui="{ base: 'text-base leading-7' }" aria-label="Mensaje para A*" @submit="conversar(pregunta)">
        <template #footer>
          <div class="acciones-compositor"><UButton type="button" class="boton-adjuntar" icon="i-lucide-plus" color="neutral" variant="ghost" aria-label="Adjuntar documento" :disabled="enviando || bloqueado" @click="emit('adjuntar')" /><USelect v-model="modo" :items="opcionesModos" :disabled="enviando || bloqueado" icon="i-lucide-scan-search" variant="ghost" color="neutral" size="sm" aria-label="Modo de recuperación para A*" class="selector-modo" /></div>
          <UChatPromptSubmit :loading="enviando" :disabled="enviando || bloqueado || !pregunta.trim()" size="lg" aria-label="Enviar mensaje a A*" />
        </template>
      </UChatPrompt>
      <p class="pie-consulta">Comprueba las fuentes. El historial se conserva solo en esta sesión.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EstadoAgente, MensajeChat, ModoBusqueda, RespuestaChat, TurnoChat } from '~/types/documental'

const { coleccion, activo, bloqueado } = defineProps<{ coleccion: string, activo: boolean, bloqueado: boolean }>()
const modo = defineModel<ModoBusqueda>('modo', { required: true })
const emit = defineEmits<{ estado: [valor: EstadoAgente], ocupado: [valor: boolean], adjuntar: [] }>()
const pregunta = ref('')
const turnos = ref<TurnoChat[]>([])
const enviando = ref(false)
const pendiente = ref('')
const ultimaPregunta = ref('')
const aviso = ref('')
const fuentesAbiertas = ref<Record<string, string | undefined>>({})
const panelConversacion = useTemplateRef('panelConversacion')
const opcionesModos = [{ label: 'Híbrida', value: 'hibrida' }, { label: 'Semántica', value: 'vector' }, { label: 'Textual', value: 'texto' }]
const ejemplos = ['¿Qué penalización tiene salir antes del local Cedro?', '¿Cuándo se devuelve el depósito de Aurora?', '¿Qué pasa si se retrasa la entrega de Bruma?']

watch(() => coleccion, () => {
  turnos.value = []
  fuentesAbiertas.value = {}
  aviso.value = ''
  ultimaPregunta.value = ''
})

watch(() => activo, async (visible) => {
  if (!visible) return
  await nextTick()
  if (enviando.value) desplazarHasta('pregunta-pendiente')
  else if (turnos.value.length) desplazarHasta(turnos.value[turnos.value.length - 1]!.id)
})

function partesRespuesta(turno: TurnoChat) {
  return turno.respuesta.split(/(\[\d+\])/g).map(texto => {
    const numero = /^\[(\d+)\]$/.exec(texto)?.[1]
    const fuente = Number(numero)
    return { texto, fuente: fuente > 0 && fuente <= turno.resultado.coincidencias.length ? fuente : 0 }
  })
}

function desplazarHasta(id: string) {
  const destino = document.getElementById(id)
  const panel = panelConversacion.value
  if (destino && panel) panel.scrollTop += destino.getBoundingClientRect().top - panel.getBoundingClientRect().top - 16
}

async function irAFuente(turnoId: string, fuente: number) {
  fuentesAbiertas.value[turnoId] = 'fuentes'
  await nextTick()
  const id = 'fuente-' + turnoId + '-' + fuente
  desplazarHasta(id)
  document.getElementById(id)?.focus({ preventScroll: true })
}

async function conversar(texto: string) {
  texto = texto.trim()
  if (!texto || texto.length > 1000 || enviando.value || bloqueado) return
  const historial = turnos.value.slice(-3).flatMap<MensajeChat>(turno => [
    { rol: 'user', texto: turno.pregunta.slice(0, 4000) },
    { rol: 'assistant', texto: turno.respuesta.slice(0, 4000) }
  ])
  enviando.value = true
  emit('ocupado', true)
  pendiente.value = texto
  ultimaPregunta.value = texto
  aviso.value = ''
  pregunta.value = ''
  await nextTick()
  panelConversacion.value?.scrollTo({ top: panelConversacion.value.scrollHeight })
  try {
    const resultado = await $fetch<RespuestaChat>('/api/motor/chat', { method: 'POST', body: { texto, modo: modo.value, coleccion_id: coleccion || null, historial }, retry: 0 })
    const id = crypto.randomUUID()
    turnos.value.push({ id, pregunta: texto, ...resultado })
    emit('estado', 'disponible')
    await nextTick()
    desplazarHasta(id)
  } catch (error) {
    const codigo = error instanceof Error && 'statusCode' in error ? error.statusCode : undefined
    const noDisponible = codigo === undefined || codigo === 502 || codigo === 503 || codigo === 504
    if (noDisponible) {
      emit('estado', 'no-disponible')
      aviso.value = 'A* no está disponible. Tu pregunta se conserva; usa Buscar fragmentos o reintenta después.'
    } else {
      aviso.value = 'Tu pregunta se conserva. Revisa el texto y vuelve a intentar cuando el motor esté disponible.'
    }
    pregunta.value = texto
  } finally {
    enviando.value = false
    emit('ocupado', false)
    pendiente.value = ''
  }
}
</script>
