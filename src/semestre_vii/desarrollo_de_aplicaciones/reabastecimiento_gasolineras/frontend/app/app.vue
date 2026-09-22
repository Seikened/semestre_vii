<script setup lang="ts">
const colorMode = useColorMode()

const color = computed(() => colorMode.value === 'dark' ? '#1b1718' : 'white')

useHead({
  titleTemplate: title => title ? `${title} · Reabastecimiento` : 'Reabastecimiento',
  meta: [
    { charset: 'utf-8' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1' },
    { key: 'theme-color', name: 'theme-color', content: color }
  ],
  link: [
    { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }
  ],
  htmlAttrs: {
    lang: 'es'
  }
})

const description = 'Prototipo visual para operación, solicitud y evaluación de reabastecimiento de combustible.'

useSeoMeta({
  title: 'Reabastecimiento',
  description,
  ogTitle: 'Reabastecimiento',
  ogDescription: description
})
</script>

<template>
  <UApp>
    <NuxtLoadingIndicator />

    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
