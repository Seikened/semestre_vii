<script setup lang="ts">
import { getPaginationRowModel } from '@tanstack/table-core'
import type { TableColumn } from '@nuxt/ui'
import { orders } from '~/data/mock'
import type { Order } from '~/types'

const UBadge = resolveComponent('UBadge')
const table = useTemplateRef('table')
const statusFilter = ref('all')
const pagination = ref({ pageIndex: 0, pageSize: 10 })

const station = computed({
  get: () => (table.value?.tableApi?.getColumn('station')?.getFilterValue() as string) || '',
  set: (value: string) => table.value?.tableApi?.getColumn('station')?.setFilterValue(value || undefined)
})

watch(statusFilter, (value) => {
  const column = table.value?.tableApi?.getColumn('status')
  column?.setFilterValue(value === 'all' ? undefined : value)
})

const liters = (value: number) => `${new Intl.NumberFormat('es-MX').format(value)} L`

const columns: TableColumn<Order>[] = [
  { accessorKey: 'id', header: 'Pedido' },
  { accessorKey: 'station', header: 'Estación' },
  { accessorKey: 'week', header: 'Semana' },
  { accessorKey: 'product', header: 'Producto' },
  { accessorKey: 'recommendedLiters', header: 'Recomendado', cell: ({ row }) => liters(row.original.recommendedLiters) },
  { accessorKey: 'requestedLiters', header: 'Solicitado', cell: ({ row }) => liters(row.original.requestedLiters) },
  {
    accessorKey: 'decision',
    header: 'Captura',
    cell: ({ row }) => {
      const labels = { accepted: 'Asistida', modified: 'Modificada', manual: 'Manual' }
      const colors = { accepted: 'success' as const, modified: 'warning' as const, manual: 'neutral' as const }

      return h(UBadge, { color: colors[row.original.decision], variant: 'subtle' }, () => labels[row.original.decision])
    }
  },
  {
    accessorKey: 'status',
    header: 'Estado',
    cell: ({ row }) => {
      const labels = { pending: 'Pendiente', reviewing: 'En revisión', approved: 'Aprobado' }
      const colors = { pending: 'warning' as const, reviewing: 'info' as const, approved: 'success' as const }

      return h(UBadge, { color: colors[row.original.status], variant: 'subtle' }, () => labels[row.original.status])
    }
  }
]
</script>

<template>
  <UDashboardPanel id="orders">
    <template #header>
      <UDashboardNavbar title="Pedidos">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton label="Nuevo pedido" icon="i-lucide-plus" disabled />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="flex flex-wrap items-center justify-between gap-2">
        <UInput
          v-model="station"
          icon="i-lucide-search"
          placeholder="Filtrar estación..."
          class="max-w-sm"
        />

        <USelect
          v-model="statusFilter"
          :items="[
            { label: 'Todos los estados', value: 'all' },
            { label: 'Pendiente', value: 'pending' },
            { label: 'En revisión', value: 'reviewing' },
            { label: 'Aprobado', value: 'approved' }
          ]"
          class="min-w-44"
        />
      </div>

      <UTable
        ref="table"
        v-model:pagination="pagination"
        :data="orders"
        :columns="columns"
        :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
        class="shrink-0"
      />

      <div class="mt-auto flex items-center justify-between gap-3 border-t border-default pt-4">
        <p class="text-sm text-muted">
          {{ table?.tableApi?.getFilteredRowModel().rows.length || 0 }} pedidos simulados
        </p>

        <UPagination
          :default-page="(table?.tableApi?.getState().pagination.pageIndex || 0) + 1"
          :items-per-page="table?.tableApi?.getState().pagination.pageSize"
          :total="table?.tableApi?.getFilteredRowModel().rows.length"
          @update:page="(page: number) => table?.tableApi?.setPageIndex(page - 1)"
        />
      </div>
    </template>
  </UDashboardPanel>
</template>
