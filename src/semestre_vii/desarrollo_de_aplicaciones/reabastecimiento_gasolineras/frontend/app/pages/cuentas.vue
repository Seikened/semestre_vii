<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import { stationAccounts } from '~/data/reabastecimiento'
import type { StationAccount } from '~/types'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')

const columns: TableColumn<StationAccount>[] = [{
  accessorKey: 'id',
  header: 'ID'
}, {
  accessorKey: 'name',
  header: 'Responsable'
}, {
  accessorKey: 'email',
  header: 'Cuenta'
}, {
  accessorKey: 'station',
  header: 'Ámbito'
}, {
  accessorKey: 'role',
  header: 'Rol'
}, {
  accessorKey: 'lastAccess',
  header: 'Último acceso'
}, {
  accessorKey: 'status',
  header: 'Estado',
  cell: ({ row }) => h(
    UBadge,
    {
      color: row.original.status === 'active' ? 'success' : 'error',
      variant: 'subtle'
    },
    () => row.original.status === 'active' ? 'Activa' : 'Revocada'
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
        items: [[{
          type: 'label',
          label: row.original.name
        }], [{
          label: 'Emitir nuevas credenciales',
          icon: 'i-lucide-key-round'
        }, {
          label: row.original.status === 'active' ? 'Revocar acceso' : 'Restablecer acceso',
          icon: row.original.status === 'active' ? 'i-lucide-user-x' : 'i-lucide-user-check',
          color: row.original.status === 'active' ? 'error' : 'success'
        }]]
      },
      () => h(UButton, {
        icon: 'i-lucide-ellipsis-vertical',
        color: 'neutral',
        variant: 'ghost'
      })
    )
  )
}]
</script>

<template>
  <UDashboardPanel id="accounts">
    <template #header>
      <UDashboardNavbar title="Cuentas">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton label="Nueva cuenta" icon="i-lucide-user-plus" />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <UAlert
        icon="i-lucide-shield"
        color="neutral"
        variant="subtle"
        title="Gestión visual de acceso"
        description="Las acciones de revocación y emisión de credenciales son sólo estados de prototipo; no existe identidad conectada."
      />

      <UTable :data="stationAccounts" :columns="columns" />

      <UCard>
        <template #header>
          <div>
            <p class="font-semibold text-highlighted">
              Alcance de cuentas
            </p>
            <p class="text-sm text-muted">
              Cada cuenta de sucursal se asocia con una estación; las cuentas de distribuidora representan un ámbito administrativo.
            </p>
          </div>
        </template>

        <div class="grid gap-4 sm:grid-cols-3">
          <div>
            <p class="text-xs uppercase text-muted">
              Cuentas visibles
            </p>
            <p class="mt-1 text-2xl font-semibold text-highlighted">
              {{ stationAccounts.length }}
            </p>
          </div>
          <div>
            <p class="text-xs uppercase text-muted">
              Acceso revocado
            </p>
            <p class="mt-1 text-2xl font-semibold text-highlighted">
              1
            </p>
          </div>
          <div>
            <p class="text-xs uppercase text-muted">
              Mecanismo real
            </p>
            <p class="mt-1 text-sm font-medium text-highlighted">
              Pendiente de definición
            </p>
          </div>
        </div>
      </UCard>
    </template>
  </UDashboardPanel>
</template>
