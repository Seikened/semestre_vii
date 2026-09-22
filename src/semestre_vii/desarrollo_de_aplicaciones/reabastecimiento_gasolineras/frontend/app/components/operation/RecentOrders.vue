<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import { fuelOrders } from '~/data/reabastecimiento'
import type { FuelOrder } from '~/types'

const UBadge = resolveComponent('UBadge')

const rows = fuelOrders.slice(0, 5)
const liters = (value: number) => `${new Intl.NumberFormat('es-MX').format(value)} L`

const columns: TableColumn<FuelOrder>[] = [{
  accessorKey: 'id',
  header: 'Pedido'
}, {
  accessorKey: 'station',
  header: 'Estación'
}, {
  accessorKey: 'product',
  header: 'Producto'
}, {
  accessorKey: 'requestedLiters',
  header: 'Solicitado',
  cell: ({ row }) => liters(row.original.requestedLiters)
}, {
  accessorKey: 'decision',
  header: 'Captura',
  cell: ({ row }) => {
    const labels = { accepted: 'Asistida', modified: 'Modificada', manual: 'Manual' }
    const colors = { accepted: 'success' as const, modified: 'warning' as const, manual: 'neutral' as const }

    return h(UBadge, { color: colors[row.original.decision], variant: 'subtle' }, () => labels[row.original.decision])
  }
}]
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="font-semibold text-highlighted">
            Pedidos recientes
          </p>
          <p class="text-sm text-muted">
            Recomendación y decisión humana en la misma vista.
          </p>
        </div>

        <UButton
          to="/pedidos"
          label="Ver todos"
          color="neutral"
          variant="ghost"
          trailing-icon="i-lucide-arrow-right"
        />
      </div>
    </template>

    <UTable :data="rows" :columns="columns" />
  </UCard>
</template>
