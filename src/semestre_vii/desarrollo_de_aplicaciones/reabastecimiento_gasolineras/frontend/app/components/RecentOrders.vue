<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { orders } from '~/data/mock'
import type { Order } from '~/types'

const UBadge = resolveComponent('UBadge')
const rows = orders.slice(0, 5)

const liters = (value: number) => `${new Intl.NumberFormat('es-MX').format(value)} L`

const columns: TableColumn<Order>[] = [
  { accessorKey: 'id', header: 'Pedido' },
  { accessorKey: 'station', header: 'Estación' },
  { accessorKey: 'product', header: 'Producto' },
  { accessorKey: 'recommendedLiters', header: 'Recomendado', cell: ({ row }) => liters(row.original.recommendedLiters) },
  { accessorKey: 'requestedLiters', header: 'Solicitado', cell: ({ row }) => liters(row.original.requestedLiters) },
  {
    accessorKey: 'decision',
    header: 'Decisión',
    cell: ({ row }) => {
      const labels = { accepted: 'Aceptada', modified: 'Modificada', manual: 'Manual' }
      const colors = { accepted: 'success' as const, modified: 'warning' as const, manual: 'neutral' as const }

      return h(UBadge, { color: colors[row.original.decision], variant: 'subtle' }, () => labels[row.original.decision])
    }
  }
]
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="text-sm font-semibold text-highlighted">
            Pedidos recientes
          </p>
          <p class="text-xs text-muted">
            Cómo se compara la recomendación con la decisión humana.
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
