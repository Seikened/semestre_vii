<script setup lang="ts">
import { format } from 'date-fns'
import type { FuelOrder } from '~/types'

defineProps<{
  order: FuelOrder
}>()

const emits = defineEmits(['close'])

const liters = (value: number) => `${new Intl.NumberFormat('es-MX').format(value)} L`
const difference = (order: FuelOrder) => order.requestedLiters - order.recommendedLiters

const decisionLabel = {
  accepted: 'Recomendación aceptada',
  modified: 'Recomendación modificada',
  manual: 'Captura manual'
}

const statusLabel = {
  pending: 'Pendiente',
  reviewing: 'En revisión',
  approved: 'Aprobado'
}
</script>

<template>
  <UDashboardPanel id="orders-detail">
    <UDashboardNavbar :title="order.id" :toggle="false">
      <template #leading>
        <UButton
          icon="i-lucide-x"
          color="neutral"
          variant="ghost"
          class="-ms-1.5"
          @click="emits('close')"
        />
      </template>

      <template #right>
        <UBadge
          :color="order.status === 'approved' ? 'success' : order.status === 'reviewing' ? 'info' : 'warning'"
          variant="subtle"
        >
          {{ statusLabel[order.status] }}
        </UBadge>
      </template>
    </UDashboardNavbar>

    <div class="flex flex-col gap-1 p-4 sm:px-6 border-b border-default">
      <p class="font-semibold text-highlighted">
        {{ order.station }}
      </p>
      <p class="text-sm text-muted">
        {{ order.stationId }} · {{ order.week }} · {{ order.product }}
      </p>
      <p class="text-xs text-muted">
        {{ format(new Date(order.createdAt), 'dd MMM yyyy · HH:mm') }}
      </p>
    </div>

    <div class="flex-1 p-4 sm:p-6 overflow-y-auto space-y-6">
      <UPageGrid class="sm:grid-cols-3">
        <UPageCard title="Recomendado" icon="i-lucide-sparkles" variant="subtle">
          <p class="text-2xl font-semibold text-highlighted">
            {{ liters(order.recommendedLiters) }}
          </p>
        </UPageCard>

        <UPageCard title="Solicitado" icon="i-lucide-clipboard-check" variant="subtle">
          <p class="text-2xl font-semibold text-highlighted">
            {{ liters(order.requestedLiters) }}
          </p>
        </UPageCard>

        <UPageCard title="Diferencia" icon="i-lucide-git-compare-arrows" variant="subtle">
          <p class="text-2xl font-semibold text-highlighted">
            {{ difference(order) > 0 ? '+' : '' }}{{ liters(difference(order)) }}
          </p>
        </UPageCard>
      </UPageGrid>

      <UCard>
        <template #header>
          <div class="flex items-center justify-between gap-3">
            <p class="font-semibold text-highlighted">
              Decisión de la sucursal
            </p>
            <UBadge
              :color="order.decision === 'accepted' ? 'success' : order.decision === 'modified' ? 'warning' : 'neutral'"
              variant="subtle"
            >
              {{ decisionLabel[order.decision] }}
            </UBadge>
          </div>
        </template>

        <p class="text-sm text-toned">
          {{ order.note }}
        </p>
      </UCard>

      <UAlert
        icon="i-lucide-flask-conical"
        color="neutral"
        variant="subtle"
        title="Prototipo"
        description="Esta vista no aprueba ni modifica pedidos. Sólo representa cómo se visualizaría la revisión administrativa."
      />
    </div>

    <div class="flex justify-end gap-2 border-t border-default p-4 sm:px-6">
      <UButton label="Solicitar revisión" color="neutral" variant="outline" />
      <UButton label="Aprobar pedido" />
    </div>
  </UDashboardPanel>
</template>
