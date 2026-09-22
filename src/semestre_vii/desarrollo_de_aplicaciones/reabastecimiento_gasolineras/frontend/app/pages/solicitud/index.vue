<script setup lang="ts">
const currentOrder = [{
  product: 'Regular',
  requested: '22,000 L',
  status: 'Pendiente'
}, {
  product: 'Premium',
  requested: '9,000 L',
  status: 'Pendiente'
}, {
  product: 'Diésel',
  requested: '18,000 L',
  status: 'En revisión'
}]

useSeoMeta({
  title: 'Solicitud'
})
</script>

<template>
  <UDashboardPanel id="request-home">
    <template #header>
      <UDashboardNavbar title="Solicitud">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #trailing>
          <div class="hidden items-center gap-2 sm:flex">
            <UBadge color="neutral" variant="subtle">
              GAS-001
            </UBadge>
            <UBadge color="neutral" variant="subtle">
              2026-W39
            </UBadge>
          </div>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <UPageCard
        title="León Centro 01"
        description="Semana 2026-W39"
        icon="i-lucide-fuel"
        variant="subtle"
        orientation="horizontal"
      >
        <UBadge color="warning" variant="subtle">
          Pedido en preparación
        </UBadge>
      </UPageCard>

      <div class="grid gap-4 lg:grid-cols-2">
        <UPageCard
          title="Nuevo pedido"
          description="Prepara el suministro de la próxima semana."
          icon="i-lucide-file-plus-2"
          to="/solicitud/pedido"
          variant="soft"
          highlight
          highlight-color="primary"
        >
          <template #footer>
            <UButton
              to="/solicitud/pedido"
              label="Preparar pedido"
              trailing-icon="i-lucide-arrow-right"
              color="neutral"
              variant="ghost"
            />
          </template>
        </UPageCard>

        <UPageCard
          title="Cierre semanal"
          description="Registra el resultado real de la semana."
          icon="i-lucide-clipboard-check"
          to="/solicitud/cierre"
          variant="subtle"
        >
          <template #footer>
            <UButton
              to="/solicitud/cierre"
              label="Registrar cierre"
              trailing-icon="i-lucide-arrow-right"
              color="neutral"
              variant="ghost"
            />
          </template>
        </UPageCard>
      </div>

      <UCard title="Pedido actual">
        <div class="divide-y divide-default">
          <div
            v-for="item in currentOrder"
            :key="item.product"
            class="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0"
          >
            <span class="font-medium text-highlighted">
              {{ item.product }}
            </span>

            <div class="flex items-center gap-3">
              <span class="text-sm text-muted">
                {{ item.requested }}
              </span>
              <UBadge
                :color="item.status === 'En revisión' ? 'info' : 'warning'"
                variant="subtle"
                size="sm"
              >
                {{ item.status }}
              </UBadge>
            </div>
          </div>
        </div>
      </UCard>
    </template>
  </UDashboardPanel>
</template>
