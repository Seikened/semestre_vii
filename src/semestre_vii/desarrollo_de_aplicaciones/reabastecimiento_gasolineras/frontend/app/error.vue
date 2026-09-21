<script setup lang="ts">
import type { NuxtError } from '#app'

defineProps<{
  error: NuxtError
}>()

useSeoMeta({
  title: 'Página no encontrada',
  description: 'La vista solicitada no existe en esta maqueta.'
})

useHead({
  htmlAttrs: {
    lang: 'es'
  }
})
</script>

<template>
  <UApp>
    <UError :error="error" />
  </UApp>
</template>
