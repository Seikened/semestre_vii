<script setup lang="ts">
import { format, isToday } from 'date-fns'
import type { FuelOrder } from '~/types'

const props = defineProps<{
  orders: FuelOrder[]
}>()

const orderRefs = ref<Record<string, Element | null>>({})
const selectedOrder = defineModel<FuelOrder | null>()

watch(selectedOrder, () => {
  if (!selectedOrder.value) {
    return
  }

  const ref = orderRefs.value[selectedOrder.value.id]
  ref?.scrollIntoView({ block: 'nearest' })
})

defineShortcuts({
  arrowdown: () => {
    const index = props.orders.findIndex(order => order.id === selectedOrder.value?.id)

    if (index === -1) {
      selectedOrder.value = props.orders[0]
    } else if (index < props.orders.length - 1) {
      selectedOrder.value = props.orders[index + 1]
    }
  },
  arrowup: () => {
    const index = props.orders.findIndex(order => order.id === selectedOrder.value?.id)

    if (index === -1) {
      selectedOrder.value = props.orders[props.orders.length - 1]
    } else if (index > 0) {
      selectedOrder.value = props.orders[index - 1]
    }
  }
})

const statusLabel = {
  pending: 'Pendiente',
  reviewing: 'En revisión',
  approved: 'Aprobado'
}
</script>

<template>
  <div class="overflow-y-auto divide-y divide-default">
    <div
      v-for="order in orders"
      :key="order.id"
      :ref="(el) => { orderRefs[order.id] = el as Element | null }"
    >
      <div
        class="p-4 sm:px-6 text-sm cursor-pointer border-l-2 transition-colors"
        :class="selectedOrder?.id === order.id
          ? 'border-primary bg-primary/10'
          : 'border-bg hover:border-primary hover:bg-primary/5'"
        @click="selectedOrder = order"
      >
        <div class="flex items-center justify-between gap-3 font-semibold text-highlighted">
          <span class="truncate">{{ order.station }}</span>
          <span class="shrink-0 text-xs font-normal text-muted">
            {{ isToday(new Date(order.createdAt)) ? format(new Date(order.createdAt), 'HH:mm') : format(new Date(order.createdAt), 'dd MMM') }}
          </span>
        </div>

        <div class="mt-1 flex items-center justify-between gap-3">
          <p class="truncate">
            {{ order.id }} · {{ order.product }}
          </p>
          <UBadge
            :color="order.status === 'approved' ? 'success' : order.status === 'reviewing' ? 'info' : 'warning'"
            variant="subtle"
            size="xs"
          >
            {{ statusLabel[order.status] }}
          </UBadge>
        </div>

        <p class="mt-1 text-dimmed line-clamp-1">
          {{ order.note }}
        </p>
      </div>
    </div>
  </div>
</template>
