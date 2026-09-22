<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import { getPaginationRowModel } from '@tanstack/table-core'
import type { Row } from '@tanstack/table-core'
import { fuelStations } from '~/data/reabastecimiento'
import type { FuelStation } from '~/types'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')

const table = useTemplateRef('table')
const columnFilters = ref([{
  id: 'name',
  value: ''
}])
const columnVisibility = ref()
const statusFilter = ref('all')
const pagination = ref({
  pageIndex: 0,
  pageSize: 10
})

const stationName = computed({
  get: (): string => (table.value?.tableApi?.getColumn('name')?.getFilterValue() as string) || '',
  set: (value: string) => table.value?.tableApi?.getColumn('name')?.setFilterValue(value || undefined)
})

watch(statusFilter, (value) => {
  const column = table.value?.tableApi?.getColumn('status')
  column?.setFilterValue(value === 'all' ? undefined : value)
})

function getRowItems(row: Row<FuelStation>) {
  return [[{
    type: 'label',
    label: row.original.name
  }], [{
    label: 'Ver pedidos',
    icon: 'i-lucide-clipboard-list',
    to: '/pedidos'
  }, {
    label: 'Ver modelo',
    icon: 'i-lucide-chart-no-axes-combined',
    to: '/modelo'
  }]]
}

const columns: TableColumn<FuelStation>[] = [{
  accessorKey: 'id',
  header: 'ID'
}, {
  accessorKey: 'name',
  header: 'Estación'
}, {
  accessorKey: 'region',
  header: 'Región'
}, {
  accessorKey: 'manager',
  header: 'Responsable'
}, {
  accessorKey: 'lastClose',
  header: 'Último cierre'
}, {
  accessorKey: 'wape',
  header: 'WAPE',
  cell: ({ row }) => `${row.original.wape.toFixed(1)} %`
}, {
  accessorKey: 'status',
  header: 'Seguimiento',
  filterFn: 'equals',
  cell: ({ row }) => h(
    UBadge,
    {
      color: row.original.status === 'stable' ? 'success' : 'warning',
      variant: 'subtle'
    },
    () => row.original.status === 'stable' ? 'Estable' : 'Revisar'
  )
}, {
  id: 'actions',
  cell: ({ row }) => h(
    'div',
    { class: 'text-right' },
    h(
      UDropdownMenu,
      {
        content: { align: 'end' },
        items: getRowItems(row)
      },
      () => h(UButton, {
        icon: 'i-lucide-ellipsis-vertical',
        color: 'neutral',
        variant: 'ghost',
        class: 'ml-auto'
      })
    )
  )
}]
</script>

<template>
  <UDashboardPanel id="stations">
    <template #header>
      <UDashboardNavbar title="Estaciones">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #trailing>
          <UBadge label="120 objetivo" variant="subtle" />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="flex flex-wrap items-center justify-between gap-1.5">
        <UInput
          v-model="stationName"
          class="max-w-sm"
          icon="i-lucide-search"
          placeholder="Filtrar estaciones..."
        />

        <USelect
          v-model="statusFilter"
          :items="[
            { label: 'Todas', value: 'all' },
            { label: 'Estables', value: 'stable' },
            { label: 'Revisar', value: 'attention' }
          ]"
          class="min-w-32"
        />
      </div>

      <UTable
        ref="table"
        v-model:column-filters="columnFilters"
        v-model:column-visibility="columnVisibility"
        v-model:pagination="pagination"
        :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
        :data="fuelStations"
        :columns="columns"
        class="shrink-0"
        :ui="{
          base: 'table-fixed border-separate border-spacing-0',
          thead: '[&>tr]:bg-elevated/50 [&>tr]:after:content-none',
          tbody: '[&>tr]:last:[&>td]:border-b-0',
          th: 'py-2 first:rounded-l-lg last:rounded-r-lg border-y border-default first:border-l last:border-r',
          td: 'border-b border-default',
          separator: 'h-0'
        }"
      />

      <div class="flex items-center justify-between gap-3 border-t border-default pt-4 mt-auto">
        <p class="text-sm text-muted">
          Muestra visual de {{ fuelStations.length }} estaciones · red objetivo aproximada: 120
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
