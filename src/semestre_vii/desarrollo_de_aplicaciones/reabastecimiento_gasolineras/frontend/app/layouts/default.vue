<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = ref(false)

const links = [[{
  label: 'Resumen',
  icon: 'i-lucide-layout-dashboard',
  to: '/',
  exact: true,
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Pedidos',
  icon: 'i-lucide-clipboard-list',
  to: '/pedidos',
  badge: '8',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Estaciones',
  icon: 'i-lucide-fuel',
  to: '/estaciones',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Modelo',
  icon: 'i-lucide-chart-no-axes-combined',
  to: '/modelo',
  onSelect: () => {
    open.value = false
  }
}], [{
  label: 'Documentación',
  icon: 'i-lucide-book-open',
  to: 'https://github.com/Seikened/semestre_vii/tree/main/src/semestre_vii/desarrollo_de_aplicaciones/reabastecimiento_gasolineras/docs',
  target: '_blank'
}]] satisfies NavigationMenuItem[][]

const groups = computed(() => [{
  id: 'navigation',
  label: 'Ir a',
  items: links[0]
}])
</script>

<template>
  <UDashboardGroup unit="rem">
    <UDashboardSidebar
      id="default"
      v-model:open="open"
      collapsible
      resizable
      class="bg-elevated/25"
      :ui="{ footer: 'lg:border-t lg:border-default' }"
    >
      <template #header="{ collapsed }">
        <div class="flex min-h-8 items-center gap-2 px-1">
          <div class="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-inverted">
            <UIcon name="i-lucide-fuel" class="size-4" />
          </div>

          <div v-if="!collapsed" class="min-w-0">
            <p class="truncate text-sm font-semibold text-highlighted">
              Reabastecimiento
            </p>
            <p class="truncate text-xs text-muted">
              Prototipo académico
            </p>
          </div>
        </div>
      </template>

      <template #default="{ collapsed }">
        <UDashboardSearchButton :collapsed="collapsed" class="bg-transparent ring-default" />

        <UNavigationMenu
          :collapsed="collapsed"
          :items="links[0]"
          orientation="vertical"
          tooltip
          popover
        />

        <UNavigationMenu
          :collapsed="collapsed"
          :items="links[1]"
          orientation="vertical"
          tooltip
          class="mt-auto"
        />
      </template>

      <template #footer="{ collapsed }">
        <div class="flex items-center" :class="collapsed ? 'justify-center' : 'justify-between'">
          <div v-if="!collapsed">
            <p class="text-xs font-medium text-highlighted">
              Datos simulados
            </p>
            <p class="text-xs text-muted">
              Sin backend conectado
            </p>
          </div>

          <UColorModeButton color="neutral" variant="ghost" />
        </div>
      </template>
    </UDashboardSidebar>

    <UDashboardSearch :groups="groups" />

    <slot />
  </UDashboardGroup>
</template>
