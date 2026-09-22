<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui'

type ProductKey = 'regular' | 'premium' | 'diesel'

const formatter = new Intl.NumberFormat('es-MX', { maximumFractionDigits: 0 })

const products = [{
  value: 'regular' as const,
  label: 'Regular',
  icon: 'i-lucide-droplets',
  close: 20950,
  recommendation: 21800,
  requested: '22,000'
}, {
  value: 'premium' as const,
  label: 'Premium',
  icon: 'i-lucide-gem',
  close: 8870,
  recommendation: 9400,
  requested: '9,000'
}, {
  value: 'diesel' as const,
  label: 'Diésel',
  icon: 'i-lucide-truck',
  close: 16920,
  recommendation: 16400,
  requested: '18,000'
}]

const productTabs: TabsItem[] = products.map(product => ({
  label: product.label,
  icon: product.icon,
  value: product.value
}))

const activeProduct = ref<ProductKey>('regular')
const note = ref('')

const orderDraft = reactive<Record<ProductKey, string>>({
  regular: '22,000',
  premium: '9,000',
  diesel: '18,000'
})

const currentProduct = computed(() => products.find(product => product.value === activeProduct.value) ?? products[0])

const numericValue = (value: string) => Number(value.replaceAll(',', '')) || 0
const liters = (value: number) => `${formatter.format(value)} L`

const difference = computed(() => numericValue(orderDraft[activeProduct.value]) - currentProduct.value.recommendation)
const total = computed(() => Object.values(orderDraft).reduce((sum, value) => sum + numericValue(value), 0))

function useRecommendation() {
  orderDraft[activeProduct.value] = formatter.format(currentProduct.value.recommendation)
}

useSeoMeta({
  title: 'Nuevo pedido'
})
</script>

<template>
  <UDashboardPanel id="request-order">
    <template #header>
      <UDashboardNavbar title="Nuevo pedido">
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

      <UDashboardToolbar>
        <template #left>
          <UTabs
            v-model="activeProduct"
            :items="productTabs"
            :content="false"
            color="neutral"
            variant="pill"
            class="w-full sm:w-auto"
          />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <div class="grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_20rem]">
        <UCard :title="currentProduct.label">
          <div class="grid gap-4 md:grid-cols-2">
            <div class="rounded-lg bg-elevated p-4">
              <p class="text-xs text-muted">
                Cierre semanal
              </p>
              <p class="mt-1 text-2xl font-semibold text-highlighted">
                {{ liters(currentProduct.close) }}
              </p>
            </div>

            <UPageCard
              title="IA recomienda"
              icon="i-lucide-sparkles"
              variant="soft"
              highlight
              highlight-color="primary"
            >
              <p class="text-3xl font-semibold text-highlighted">
                {{ liters(currentProduct.recommendation) }}
              </p>

              <UButton
                label="Usar recomendación"
                color="neutral"
                variant="ghost"
                size="sm"
                class="mt-2"
                @click="useRecommendation"
              />
            </UPageCard>
          </div>

          <USeparator class="my-5" />

          <UFormField label="Cantidad a solicitar">
            <UInput
              v-model="orderDraft[activeProduct]"
              icon="i-lucide-clipboard-pen-line"
              size="xl"
              class="w-full"
            >
              <template #trailing>
                <span class="text-xs text-muted">L</span>
              </template>
            </UInput>
          </UFormField>

          <div class="mt-2 flex items-center justify-between gap-3 text-sm">
            <span class="text-muted">
              Diferencia vs. recomendación
            </span>
            <span
              class="font-medium"
              :class="difference === 0 ? 'text-highlighted' : 'text-warning'"
            >
              {{ difference > 0 ? '+' : '' }}{{ liters(difference) }}
            </span>
          </div>

          <UFormField label="Comentario" class="mt-5">
            <UTextarea
              v-model="note"
              placeholder="Opcional"
              autoresize
              :rows="2"
              class="w-full"
            />
          </UFormField>
        </UCard>

        <UCard title="Resumen">
          <div class="space-y-4">
            <div
              v-for="product in products"
              :key="product.value"
              class="flex items-center justify-between gap-3"
            >
              <span class="text-sm text-muted">
                {{ product.label }}
              </span>
              <span class="text-sm font-medium text-highlighted">
                {{ orderDraft[product.value] }} L
              </span>
            </div>

            <USeparator />

            <div class="flex items-center justify-between">
              <span class="font-medium text-highlighted">
                Total
              </span>
              <span class="text-lg font-semibold text-highlighted">
                {{ liters(total) }}
              </span>
            </div>
          </div>

          <template #footer>
            <div class="grid gap-2">
              <UButton
                label="Guardar borrador"
                color="neutral"
                variant="outline"
                icon="i-lucide-save"
                block
              />
              <UButton
                label="Enviar pedido"
                icon="i-lucide-send"
                block
              />
            </div>
          </template>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>
