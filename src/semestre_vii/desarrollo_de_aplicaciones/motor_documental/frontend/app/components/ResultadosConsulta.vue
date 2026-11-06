<template>
  <div class="resultados">
    <p class="etiqueta">{{ resultado.coincidencias.length }} {{ resultado.coincidencias.length === 1 ? 'fuente' : 'fuentes' }} · {{ nombresModos[resultado.modo] || resultado.modo }}</p>
    <UAlert v-if="!resultado.coincidencias.length" color="neutral" variant="soft" title="Sin coincidencias" description="Prueba otras palabras o una colección diferente." icon="i-lucide-search-x" />
    <article v-for="(fuente, indice) of resultado.coincidencias" :id="idPrefijo ? idPrefijo + (indice + 1) : undefined" :key="`${fuente.documento_id}-${fuente.pagina}-${indice}`" class="fuente" tabindex="-1">
      <div class="fuente-cabecera">
        <span class="numero-fuente">[{{ indice + 1 }}]</span>
        <div><h3>{{ fuente.titulo }}</h3><p>{{ fuente.nombre_original }} · Página {{ fuente.pagina }} · {{ fuente.metodo === 'ocr' ? 'OCR' : 'Texto digital' }}</p></div>
        <UButton :to="`/api/motor/documentos/${fuente.documento_id}/archivo#page=${fuente.pagina}`" target="_blank" trailing-icon="i-lucide-arrow-up-right" :aria-label="`Abrir ${fuente.nombre_original}, página ${fuente.pagina}`" color="neutral" variant="outline" size="sm" class="abrir-original">Original</UButton>
      </div>
      <p class="pasaje">{{ fuente.texto }}</p>
    </article>
  </div>
</template>

<script setup lang="ts">
import type { ResultadoBusqueda } from '~/types/documental'

defineProps<{ resultado: ResultadoBusqueda, idPrefijo?: string }>()
const nombresModos: Record<string, string> = { hibrida: 'Híbrida', vector: 'Semántica', texto: 'Textual' }
</script>
