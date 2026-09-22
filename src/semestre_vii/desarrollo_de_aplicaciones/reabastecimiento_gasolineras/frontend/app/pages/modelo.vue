<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import { modelCandidates } from '~/data/reabastecimiento'
import type { ModelCandidate } from '~/types'

const UBadge = resolveComponent('UBadge')

const columns: TableColumn<ModelCandidate>[] = [{
  accessorKey: 'name',
  header: 'Modelo'
}, {
  accessorKey: 'family',
  header: 'Familia'
}, {
  accessorKey: 'wape',
  header: 'WAPE'
}, {
  accessorKey: 'bias',
  header: 'Bias'
}, {
  accessorKey: 'status',
  header: 'Estado',
  cell: ({ row }) => {
    const labels = { baseline: 'Baseline', candidate: 'Candidato', pending: 'Pendiente' }
    const colors = { baseline: 'neutral' as const, candidate: 'success' as const, pending: 'warning' as const }

    return h(UBadge, { color: colors[row.original.status], variant: 'subtle' }, () => labels[row.original.status])
  }
}]
</script>

<template>
  <UDashboardPanel id="model">
    <template #header>
      <UDashboardNavbar title="Modelo">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #trailing>
          <UBadge color="neutral" variant="subtle">
            Prototipo
          </UBadge>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <UPageGrid class="lg:grid-cols-3">
        <UPageCard title="Modelo vigente" icon="i-lucide-box" variant="subtle">
          <p class="text-2xl font-semibold text-highlighted">
            Lagged GBM
          </p>
          <p class="text-xs text-muted">
            referencia de maqueta
          </p>
        </UPageCard>

        <UPageCard title="WAPE global" icon="i-lucide-chart-no-axes-combined" variant="subtle">
          <p class="text-2xl font-semibold text-highlighted">
            9.6 %
          </p>
          <p class="text-xs text-muted">
            dato simulado
          </p>
        </UPageCard>

        <UPageCard title="Horizonte" icon="i-lucide-calendar-range" variant="subtle">
          <p class="text-2xl font-semibold text-highlighted">
            1 semana
          </p>
          <p class="text-xs text-muted">
            operación
          </p>
        </UPageCard>
      </UPageGrid>

      <OperationForecastChart />

      <UCard>
        <template #header>
          <div>
            <p class="font-semibold text-highlighted">
              Comparación de candidatos
            </p>
            <p class="text-sm text-muted">
              Estructura visual para rolling-origin backtesting; los valores son únicamente de prototipo.
            </p>
          </div>
        </template>

        <UTable :data="modelCandidates" :columns="columns" />
      </UCard>
    </template>
  </UDashboardPanel>
</template>
