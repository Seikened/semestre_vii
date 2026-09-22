<script setup lang="ts">
import { sub } from 'date-fns'
import type { Period, Range } from '~/types'

const range = shallowRef<Range>({
  start: sub(new Date(), { days: 28 }),
  end: new Date()
})
const period = ref<Period>('weekly')
</script>

<template>
  <UDashboardPanel id="operation">
    <template #header>
      <UDashboardNavbar title="Resumen operativo">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UBadge color="neutral" variant="subtle">
            Prototipo
          </UBadge>
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <template #left>
          <HomeDateRangePicker v-model="range" class="-ms-1" />
          <HomePeriodSelect v-model="period" :range="range" />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <OperationStats />
      <OperationForecastChart />
      <OperationRecentOrders />
    </template>
  </UDashboardPanel>
</template>
