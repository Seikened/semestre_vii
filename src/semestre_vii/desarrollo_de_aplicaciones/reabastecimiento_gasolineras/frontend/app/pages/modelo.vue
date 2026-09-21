<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { modelCandidates } from '~/data/mock'
import type { ModelCandidate } from '~/types'

const UBadge = resolveComponent('UBadge')

const columns: TableColumn<ModelCandidate>[] = [
  { accessorKey: 'name', header: 'Modelo' },
  { accessorKey: 'family', header: 'Familia' },
  { accessorKey: 'wape', header: 'WAPE demo' },
  {
    accessorKey: 'status',
    header: 'Estado',
    cell: ({ row }) => {
      const labels = { baseline: 'Baseline', candidate: 'Candidato', pending: 'Pendiente' }
      const colors = { baseline: 'neutral' as const, candidate: 'success' as const, pending: 'warning' as const }

      return h(UBadge, { color: colors[row.original.status], variant: 'subtle' }, () => labels[row.original.status])
    }
  }
]
</script>

<template>
  <UDashboardPanel id="model">
    <template #header>
      <UDashboardNavbar title="Modelo">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UBadge color="warning" variant="subtle">
            Sin entrenamiento conectado
          </UBadge>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <UAlert
        icon="i-lucide-info"
        color="neutral"
        variant="subtle"
        title="Vista conceptual"
        description="Los números son únicamente datos de maqueta. La selección real se hará con rolling-origin backtesting sobre el histórico validado."
      />

      <ForecastChart />

      <UCard>
        <template #header>
          <div>
            <p class="text-sm font-semibold text-highlighted">
              Comparación de candidatos
            </p>
            <p class="text-xs text-muted">
              Ejemplo de cómo podría verse la evaluación antes de promover un modelo.
            </p>
          </div>
        </template>

        <UTable :data="modelCandidates" :columns="columns" />
      </UCard>
    </template>
  </UDashboardPanel>
</template>
