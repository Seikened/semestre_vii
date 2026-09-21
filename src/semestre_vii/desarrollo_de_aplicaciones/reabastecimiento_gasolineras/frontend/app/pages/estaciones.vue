<script setup lang="ts">
import { getPaginationRowModel } from '@tanstack/table-core'
import type { TableColumn } from '@nuxt/ui'
import { stations } from '~/data/mock'
import type { Station } from '~/types'

const UBadge = resolveComponent('UBadge')
const table = useTemplateRef('table')
const pagination = ref({ pageIndex: 0, pageSize: 10 })

const search = computed({
  get: () => (table.value?.tableApi?.getColumn('name')?.getFilterValue() as string) || '',
  set: (value: string) => table.value?.tableApi?.getColumn('name')?.setFilterValue(value || undefined)
})

const columns: TableColumn<Station>[] = [
  { accessorKey: 'id', header: 'ID' },
  { accessorKey: 'name', header: 'Estación' },
  { accessorKey: 'region', header: 'Región' },
  { accessorKey: 'manager', header: 'Responsable' },
  { accessorKey: 'lastClose', header: 'Último cierre' },
  { accessorKey: 'wape', header: 'WAPE', cell: ({ row }) => `${row.original.wape.toFixed(1)} %` },
  {
    accessorKey: 'status',
    header: 'Seguimiento',
    cell: ({ row }) => h(
      UBadge,
      { color: row.original.status === 'ok' ? 'success' : 'warning', variant: 'subtle' },
      () => row.original.status === 'ok' ? 'Estable' : 'Revisar'
    )
  }
]
</script>

<template>
  <UDashboardPanel id="stations">
    <template #header>
      <UDashboardNavbar title="Estaciones">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UBadge color="neutral" variant="subtle">
            120 objetivo
          </UBadge>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Buscar estación..."
        class="max-w-sm"
      />

      <UTable
        ref="table"
        v-model:pagination="pagination"
        :data="stations"
        :columns="columns"
        :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
        class="shrink-0"
      />

      <div class="mt-auto flex items-center justify-between gap-3 border-t border-default pt-4">
        <p class="text-sm text-muted">
          Vista reducida para la maqueta. El producto contempla aproximadamente 120 estaciones.
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
