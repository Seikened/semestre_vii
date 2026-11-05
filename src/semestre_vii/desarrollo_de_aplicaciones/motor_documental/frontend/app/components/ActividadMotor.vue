<template>
  <div class="actividad-motor" :class="{ 'actividad-compacta': tipo !== 'indexacion' }" role="status" aria-live="polite">
    <span class="actividad-orbita" aria-hidden="true">*</span>
    <div class="actividad-texto">
      <p class="actividad-titulo">{{ titulo }}</p>
      <p class="actividad-descripcion">{{ descripcion }}</p>
      <template v-if="tipo === 'indexacion'">
        <UProgress size="xs" color="neutral" animation="carousel" aria-label="Indexación en curso" />
        <ol class="actividad-recorrido" aria-label="Operaciones de la indexación">
          <li>Texto y OCR</li><li>Fragmentos</li><li>Embeddings</li><li>Índice vectorial</li>
        </ol>
      </template>
      <span class="actividad-final"><UIcon name="i-lucide-database" />{{ motor }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ModoBusqueda } from '~/types/documental'

const { tipo, modo = 'hibrida', nombreArchivo = '' } = defineProps<{
  tipo: 'indexacion' | 'busqueda' | 'chat'
  modo?: ModoBusqueda
  nombreArchivo?: string
}>()
const titulo = computed(() => tipo === 'indexacion' ? 'Indexando documento' : tipo === 'chat' ? 'Consultando tus documentos' : 'Buscando en tu biblioteca')
const descripcion = computed(() => {
  if (tipo === 'indexacion') return nombreArchivo + '. El motor prepara el texto y sus vectores para consulta.'
  if (tipo === 'chat') return 'Recuperación documental y respuesta con fuentes.'
  if (modo === 'texto') return 'Localizando palabras y coincidencias en el texto.'
  if (modo === 'vector') return 'Recuperando fragmentos por similitud semántica.'
  return 'Combinando coincidencias de texto y similitud semántica.'
})
const motor = computed(() => tipo === 'indexacion' || modo !== 'texto' ? 'PostgreSQL + pgvector' : 'PostgreSQL · Búsqueda textual')
</script>
