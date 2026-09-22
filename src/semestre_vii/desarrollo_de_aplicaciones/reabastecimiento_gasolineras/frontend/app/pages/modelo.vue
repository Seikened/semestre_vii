<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import { modelCandidates, stationMetrics } from '~/data/reabastecimiento'
import type { ModelCandidate, StationModelMetric } from '~/types'

const UBadge = resolveComponent('UBadge')

const selectedStation = ref('all')
const selectedProduct = ref('all')
const selectedHorizon = ref('1w')

const candidateColumns: TableColumn<ModelCandidate>[] = [{
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

const stationColumns: TableColumn<StationModelMetric>[] = [{
  accessorKey: 'station',
  header: 'Estación'
}, {
  accessorKey: 'product',
  header: 'Producto'
}, {
  accessorKey: 'horizon',
  header: 'Horizonte'
}, {
  accessorKey: 'wape',
  header: 'WAPE',
  cell: ({ row }) => `${row.original.wape.toFixed(1)} %`
}, {
  accessorKey: 'bias',
  header: 'Bias',
  cell: ({ row }) => `${row.original.bias > 0 ? '+' : ''}${row.original.bias.toFixed(1)} %`
}, {
  accessorKey: 'status',
  header: 'Seguimiento',
  cell: ({ row }) => h(
    UBadge,
    {
      color: row.original.status === 'stable' ? 'success' : 'warning',
      variant: 'subtle'
    },
    () => row.original.status === 'stable' ? 'Estable' : 'Revisar'
  )
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

      <UDashboardToolbar>
        <template #left>
          <USelect
            v-model="selectedStation"
            :items="[
              { label: 'Todas las estaciones', value: 'all' },
              { label: 'León Centro 01', value: 'GAS-001' },
              { label: 'Silao Norte 03', value: 'GAS-003' }
            ]"
            class="min-w-48"
          />
          <USelect
            v-model="selectedProduct"
            :items="[
              { label: 'Todos los productos', value: 'all' },
              { label: 'Regular', value: 'regular' },
              { label: 'Premium', value: 'premium' },
              { label: 'Diésel', value: 'diesel' }
            ]"
            class="min-w-44"
          />
          <USelect
            v-model="selectedHorizon"
            :items="[
              { label: '1 semana', value: '1w' },
              { label: '4 semanas', value: '4w' },
              { label: '12 semanas', value: '12w' },
              { label: '26 semanas', value: '26w' },
              { label: '52 semanas', value: '52w' }
            ]"
            class="min-w-36"
          />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <UPageGrid class="lg:grid-cols-4">
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

        <UPageCard title="Bias" icon="i-lucide-scale" variant="subtle">
          <p class="text-2xl font-semibold text-highlighted">
            -0.8 %
          </p>
          <p class="text-xs text-muted">
            dato simulado
          </p>
        </UPageCard>

        <UPageCard title="Incertidumbre" icon="i-lucide-chart-spline" variant="subtle">
          <p class="text-sm font-semibold text-highlighted">
            Pendiente de definición
          </p>
          <p class="text-xs text-muted">
            sin porcentaje inventado
          </p>
        </UPageCard>
      </UPageGrid>

      <OperationForecastChart />

      <div class="grid gap-4 xl:grid-cols-2">
        <UCard>
          <template #header>
            <div>
              <p class="font-semibold text-highlighted">
                Comparación de candidatos
              </p>
              <p class="text-sm text-muted">
                Estructura visual para rolling-origin backtesting.
              </p>
            </div>
          </template>

          <UTable :data="modelCandidates" :columns="candidateColumns" />
        </UCard>

        <UCard>
          <template #header>
            <div>
              <p class="font-semibold text-highlighted">
                Desempeño por estación
              </p>
              <p class="text-sm text-muted">
                El promedio global no debe ocultar series que requieran revisión.
              </p>
            </div>
          </template>

          <UTable :data="stationMetrics" :columns="stationColumns" />
        </UCard>
      </div>

      <UAlert
        icon="i-lucide-info"
        color="neutral"
        variant="subtle"
        title="Controles visuales"
        description="Los filtros y métricas sirven para validar la composición. No ejecutan evaluación ni consultan un modelo real."
      />
    </template>
  </UDashboardPanel>
</template>
