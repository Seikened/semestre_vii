<script setup lang="ts">
const products = [{
  name: 'Regular',
  forecast: '21,800 L',
  requested: '22,000 L',
  actual: '21,640'
}, {
  name: 'Premium',
  forecast: '9,400 L',
  requested: '9,000 L',
  actual: '9,180'
}, {
  name: 'Diésel',
  forecast: '16,400 L',
  requested: '18,000 L',
  actual: '17,260'
}]
</script>

<template>
  <UDashboardPanel id="weekly-close">
    <template #header>
      <UDashboardNavbar title="Cierre semanal">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton
            to="/solicitud"
            label="Volver"
            color="neutral"
            variant="ghost"
            icon="i-lucide-arrow-left"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <UPageCard
        title="Semana 2026-W38"
        description="Registro visual del resultado observado para cerrar el ciclo."
        icon="i-lucide-calendar-check"
        variant="subtle"
      >
        <template #footer>
          <UBadge color="neutral" variant="subtle">
            León Centro 01 · GAS-001
          </UBadge>
        </template>
      </UPageCard>

      <UCard>
        <template #header>
          <div>
            <p class="font-semibold text-highlighted">
              Resultado por producto
            </p>
            <p class="text-sm text-muted">
              Predicción, decisión enviada y valor real se muestran como datos distintos.
            </p>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="product in products"
            :key="product.name"
            class="grid gap-4 rounded-lg border border-default p-4 md:grid-cols-4 md:items-end"
          >
            <div>
              <p class="font-semibold text-highlighted">
                {{ product.name }}
              </p>
              <p class="text-xs text-muted">
                Combustible
              </p>
            </div>

            <div>
              <p class="text-xs text-muted">
                Pronóstico
              </p>
              <p class="mt-1 font-medium text-highlighted">
                {{ product.forecast }}
              </p>
            </div>

            <div>
              <p class="text-xs text-muted">
                Pedido
              </p>
              <p class="mt-1 font-medium text-highlighted">
                {{ product.requested }}
              </p>
            </div>

            <UFormField label="Resultado real">
              <UInput :model-value="product.actual" />
            </UFormField>
          </div>
        </div>
      </UCard>

      <UAlert
        icon="i-lucide-info"
        color="neutral"
        variant="subtle"
        title="La retroalimentación no reentrena automáticamente"
        description="En el producto real este cierre alimentará métricas y evaluación; cualquier actualización de modelo requerirá criterios explícitos."
      />

      <div class="flex justify-end">
        <UButton
          label="Registrar cierre"
          icon="i-lucide-check"
        />
      </div>
    </template>
  </UDashboardPanel>
</template>
