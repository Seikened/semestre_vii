<script setup lang="ts">
const products = [{
  name: 'Regular',
  recommendation: '21,800 L',
  requested: '22,000',
  close: '20,950'
}, {
  name: 'Premium',
  recommendation: '9,400 L',
  requested: '9,000',
  close: '8,870'
}, {
  name: 'Diésel',
  recommendation: '16,400 L',
  requested: '18,000',
  close: '16,920'
}]

const captureMode = ref('assisted')
</script>

<template>
  <UDashboardPanel id="request-order">
    <template #header>
      <UDashboardNavbar title="Nuevo pedido">
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
      <UAlert
        icon="i-lucide-flask-conical"
        color="neutral"
        variant="subtle"
        title="Formulario de maqueta"
        description="Los campos exactos del cierre y del pedido todavía deben confirmarse con la fuente real. Esta composición valida únicamente la experiencia."
      />

      <UPageCard
        title="Contexto"
        description="Sucursal y semana asociadas a la cuenta."
        icon="i-lucide-fuel"
        variant="subtle"
      >
        <div class="grid gap-4 sm:grid-cols-3">
          <div>
            <p class="text-xs uppercase text-muted">
              Sucursal
            </p>
            <p class="mt-1 font-medium text-highlighted">
              León Centro 01
            </p>
          </div>
          <div>
            <p class="text-xs uppercase text-muted">
              Semana
            </p>
            <p class="mt-1 font-medium text-highlighted">
              2026-W39
            </p>
          </div>
          <div>
            <p class="text-xs uppercase text-muted">
              Incertidumbre
            </p>
            <p class="mt-1 font-medium text-highlighted">
              Pendiente de definición
            </p>
          </div>
        </div>
      </UPageCard>

      <UCard>
        <template #header>
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p class="font-semibold text-highlighted">
                Captura por producto
              </p>
              <p class="text-sm text-muted">
                Hecho observado, recomendación y decisión humana permanecen separados.
              </p>
            </div>

            <USelect
              v-model="captureMode"
              :items="[
                { label: 'Asistida por recomendación', value: 'assisted' },
                { label: 'Modificar recomendación', value: 'modified' },
                { label: 'Captura manual', value: 'manual' }
              ]"
              class="min-w-56"
            />
          </div>
        </template>

        <div class="space-y-6">
          <div
            v-for="product in products"
            :key="product.name"
            class="grid gap-4 rounded-lg border border-default p-4 lg:grid-cols-3"
          >
            <div>
              <p class="font-semibold text-highlighted">
                {{ product.name }}
              </p>
              <p class="text-xs text-muted">
                Producto de maqueta
              </p>
            </div>

            <UFormField
              label="Dato de cierre"
              description="Campo provisional hasta confirmar el contrato."
            >
              <UInput :model-value="product.close" trailing-icon="i-lucide-gauge" />
            </UFormField>

            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <p class="text-xs text-muted">
                  Recomendación
                </p>
                <p class="mt-2 text-xl font-semibold text-highlighted">
                  {{ product.recommendation }}
                </p>
              </div>

              <UFormField label="Solicitar">
                <UInput :model-value="product.requested" />
              </UFormField>
            </div>
          </div>
        </div>
      </UCard>

      <UFormField
        label="Comentario de la sucursal"
        description="Justificación o contexto cuando la solicitud difiera de la recomendación."
      >
        <UTextarea
          placeholder="Añade contexto operativo..."
          :rows="4"
          class="w-full"
        />
      </UFormField>

      <div class="flex flex-wrap justify-end gap-2">
        <UButton
          label="Guardar borrador"
          color="neutral"
          variant="outline"
          icon="i-lucide-save"
        />
        <UButton
          label="Enviar pedido"
          icon="i-lucide-send"
        />
      </div>
    </template>
  </UDashboardPanel>
</template>
