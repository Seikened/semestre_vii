<script setup lang="ts">
const stats = [
  { title: 'Estaciones', value: '120', detail: 'red objetivo', icon: 'i-lucide-fuel' },
  { title: 'Pedidos por revisar', value: '8', detail: 'semana actual', icon: 'i-lucide-clipboard-clock' },
  { title: 'Demanda próxima', value: '1.84 M L', detail: 'estimación simulada', icon: 'i-lucide-gauge' },
  { title: 'WAPE', value: '8.4 %', detail: 'valor de maqueta', icon: 'i-lucide-chart-no-axes-combined' }
]
</script>

<template>
  <UPageGrid class="gap-4 sm:grid-cols-2 xl:grid-cols-4">
    <UPageCard
      v-for="stat in stats"
      :key="stat.title"
      :icon="stat.icon"
      :title="stat.title"
      variant="subtle"
      :ui="{
        container: 'gap-y-1.5',
        wrapper: 'items-start',
        leading: 'p-2.5 rounded-full bg-primary/10 ring ring-inset ring-primary/25 flex-col',
        title: 'font-normal text-muted text-xs uppercase'
      }"
    >
      <p class="text-2xl font-semibold text-highlighted">
        {{ stat.value }}
      </p>
      <p class="text-xs text-muted">
        {{ stat.detail }}
      </p>
    </UPageCard>
  </UPageGrid>
</template>
