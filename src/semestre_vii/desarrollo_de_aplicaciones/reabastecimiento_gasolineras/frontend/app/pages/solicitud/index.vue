<script setup lang="ts">
const currentOrder = [{
  product: 'Regular',
  recommended: '21,800 L',
  requested: '22,000 L',
  status: 'Pendiente'
}, {
  product: 'Premium',
  recommended: '9,400 L',
  requested: '9,000 L',
  status: 'Pendiente'
}, {
  product: 'Diésel',
  recommended: '16,400 L',
  requested: '18,000 L',
  status: 'En revisión'
}]
</script>

<template>
  <UDashboardPanel id="request-home">
    <template #header>
      <UDashboardNavbar title="Portal de sucursal">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #trailing>
          <UBadge color="neutral" variant="subtle">
            GAS-001
          </UBadge>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <UPageGrid class="lg:grid-cols-3">
        <UPageCard title="Sucursal" icon="i-lucide-fuel" variant="subtle">
          <p class="text-xl font-semibold text-highlighted">
            León Centro 01
          </p>
          <p class="text-xs text-muted">
            Cuenta asociada de maqueta
          </p>
        </UPageCard>

        <UPageCard title="Semana operativa" icon="i-lucide-calendar-days" variant="subtle">
          <p class="text-xl font-semibold text-highlighted">
            2026-W39
          </p>
          <p class="text-xs text-muted">
            siguiente suministro
          </p>
        </UPageCard>

        <UPageCard title="Estado" icon="i-lucide-clock-3" variant="subtle">
          <p class="text-xl font-semibold text-highlighted">
            Pedido en preparación
          </p>
          <p class="text-xs text-muted">
            flujo visual
          </p>
        </UPageCard>
      </UPageGrid>

      <div class="grid gap-4 lg:grid-cols-2">
        <UPageCard
          title="Nuevo pedido"
          description="Captura el pedido de la semana siguiente con la recomendación como apoyo."
          icon="i-lucide-file-plus-2"
          to="/solicitud/pedido"
          variant="subtle"
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
          description="Registra el resultado observado para cerrar el ciclo de evaluación."
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

      <UCard>
        <template #header>
          <div>
            <p class="font-semibold text-highlighted">
              Pedido actual
            </p>
            <p class="text-sm text-muted">
              Comparación visual entre recomendación y cantidad solicitada.
            </p>
          </div>
        </template>

        <div class="divide-y divide-default">
          <div
            v-for="item in currentOrder"
            :key="item.product"
            class="grid gap-3 py-4 sm:grid-cols-4 sm:items-center"
          >
            <p class="font-medium text-highlighted">
              {{ item.product }}
            </p>
            <div>
              <p class="text-xs text-muted">
                Recomendado
              </p>
              <p class="text-sm">
                {{ item.recommended }}
              </p>
            </div>
            <div>
              <p class="text-xs text-muted">
                Solicitado
              </p>
              <p class="text-sm">
                {{ item.requested }}
              </p>
            </div>
            <UBadge
              :color="item.status === 'En revisión' ? 'info' : 'warning'"
              variant="subtle"
              class="w-fit"
            >
              {{ item.status }}
            </UBadge>
          </div>
        </div>
      </UCard>

      <UAlert
        icon="i-lucide-info"
        color="neutral"
        variant="subtle"
        title="Datos de prototipo"
        description="Los valores de esta vista son ficticios y no representan una recomendación operativa real."
      />
    </template>
  </UDashboardPanel>
</template>
