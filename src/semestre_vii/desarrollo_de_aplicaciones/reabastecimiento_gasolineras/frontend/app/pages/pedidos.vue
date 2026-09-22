<script setup lang="ts">
import { breakpointsTailwind } from '@vueuse/core'
import { fuelOrders } from '~/data/reabastecimiento'
import type { FuelOrder, FuelOrderStatus } from '~/types'

const tabs = [{
  label: 'Todos',
  value: 'all'
}, {
  label: 'Pendientes',
  value: 'pending'
}, {
  label: 'En revisión',
  value: 'reviewing'
}, {
  label: 'Aprobados',
  value: 'approved'
}]

const selectedTab = ref('all')
const selectedOrder = ref<FuelOrder | null>()

const filteredOrders = computed(() => {
  if (selectedTab.value === 'all') {
    return fuelOrders
  }

  return fuelOrders.filter(order => order.status === selectedTab.value as FuelOrderStatus)
})

const isOrderPanelOpen = computed({
  get: () => !!selectedOrder.value,
  set: (value: boolean) => {
    if (!value) {
      selectedOrder.value = null
    }
  }
})

watch(filteredOrders, () => {
  if (!filteredOrders.value.find(order => order.id === selectedOrder.value?.id)) {
    selectedOrder.value = null
  }
})

const breakpoints = useBreakpoints(breakpointsTailwind)
const isMobile = breakpoints.smaller('lg')
</script>

<template>
  <UDashboardPanel
    id="orders-1"
    :default-size="28"
    :min-size="22"
    :max-size="36"
    resizable
  >
    <UDashboardNavbar title="Pedidos">
      <template #leading>
        <UDashboardSidebarCollapse />
      </template>

      <template #trailing>
        <UBadge :label="filteredOrders.length" variant="subtle" />
      </template>

      <template #right>
        <UTabs
          v-model="selectedTab"
          :items="tabs"
          :content="false"
          size="xs"
        />
      </template>
    </UDashboardNavbar>

    <OrdersList v-model="selectedOrder" :orders="filteredOrders" />
  </UDashboardPanel>

  <OrdersDetail v-if="selectedOrder" :order="selectedOrder" @close="selectedOrder = null" />

  <div v-else class="hidden lg:flex flex-1 items-center justify-center">
    <UIcon name="i-lucide-clipboard-list" class="size-32 text-dimmed" />
  </div>

  <ClientOnly>
    <USlideover v-if="isMobile" v-model:open="isOrderPanelOpen">
      <template #content>
        <OrdersDetail v-if="selectedOrder" :order="selectedOrder" @close="selectedOrder = null" />
      </template>
    </USlideover>
  </ClientOnly>
</template>
