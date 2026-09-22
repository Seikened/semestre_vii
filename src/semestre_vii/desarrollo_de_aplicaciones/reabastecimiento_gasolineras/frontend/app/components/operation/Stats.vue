<script setup lang="ts">
const stats = [{
  title: 'Estaciones',
  icon: 'i-lucide-fuel',
  value: '120',
  detail: 'red objetivo'
}, {
  title: 'Pedidos por revisar',
  icon: 'i-lucide-clipboard-clock',
  value: '8',
  detail: 'semana actual'
}, {
  title: 'Demanda próxima',
  icon: 'i-lucide-gauge',
  value: '1.84 M L',
  detail: 'estimación de maqueta'
}, {
  title: 'WAPE',
  icon: 'i-lucide-chart-no-axes-combined',
  value: '8.4 %',
  detail: 'referencia visual'
}]
</script>

<template>
  <UPageGrid class="lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-px">
    <UPageCard
      v-for="(stat, index) in stats"
      :key="index"
      :icon="stat.icon"
      :title="stat.title"
      variant="subtle"
      :ui="{
        container: 'gap-y-1.5',
        wrapper: 'items-start',
        leading: 'p-2.5 rounded-full bg-primary/10 ring ring-inset ring-primary/25 flex-col',
        title: 'font-normal text-muted text-xs uppercase'
      }"
      class="lg:rounded-none first:rounded-l-lg last:rounded-r-lg hover:z-1"
    >
      <div>
        <p class="text-2xl font-semibold text-highlighted">
          {{ stat.value }}
        </p>
        <p class="mt-1 text-xs text-muted">
          {{ stat.detail }}
        </p>
      </div>
    </UPageCard>
  </UPageGrid>
</template>
