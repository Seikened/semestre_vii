<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui'

type ProductKey = 'regular' | 'premium' | 'diesel'

const formatter = new Intl.NumberFormat('es-MX', { maximumFractionDigits: 0 })

const products = [{
  value: 'regular' as const,
  label: 'Regular',
  icon: 'i-lucide-droplets',
  forecast: 21800,
  requested: 22000,
  actual: '21,640'
}, {
  value: 'premium' as const,
  label: 'Premium',
  icon: 'i-lucide-gem',
  forecast: 9400,
  requested: 9000,
  actual: '9,180'
}, {
  value: 'diesel' as const,
  label: 'Diésel',
  icon: 'i-lucide-truck',
  forecast: 16400,
  requested: 18000,
  actual: '17,260'
}]

const productTabs: TabsItem[] = products.map(product => ({
  label: product.label,
  icon: product.icon,
  value: product.value
}))

const activeProduct = ref<ProductKey>('regular')

const actualDraft = reactive<Record<ProductKey, string>>({
  regular: '21,640',
  premium: '9,180',
  diesel: '17,260'
})

const currentProduct = computed(() => products.find(product => product.value === activeProduct.value) ?? products[0])

const liters = (value: number) => `${formatter.format(value)} L`

useSeoMeta({
  title: 'Cierre semanal'
})
</script>

<template>
  <UDashboardPanel id="weekly-close">
    <template #header>
      <UDashboardNavbar title="Cierre semanal">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #trailing>
          <div class="hidden items-center gap-2 sm:flex">
            <UBadge color="neutral" variant="subtle">
              GAS-001
            </UBadge>
            <UBadge color="neutral" variant="subtle">
              2026-W38
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
            <UPageCard
              title="Pronóstico"
              icon="i-lucide-sparkles"
              variant="soft"
            >
              <p class="text-2xl font-semibold text-highlighted">
                {{ liters(currentProduct.forecast) }}
              </p>
            </UPageCard>

            <UPageCard
              title="Pedido enviado"
              icon="i-lucide-clipboard-check"
              variant="subtle"
            >
              <p class="text-2xl font-semibold text-highlighted">
                {{ liters(currentProduct.requested) }}
              </p>
            </UPageCard>
          </div>

          <USeparator class="my-5" />

          <UFormField label="Resultado real">
            <UInput
              v-model="actualDraft[activeProduct]"
              icon="i-lucide-gauge"
              size="xl"
              class="w-full"
            >
              <template #trailing>
                <span class="text-xs text-muted">L</span>
              </template>
            </UInput>
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
                {{ actualDraft[product.value] }} L
              </span>
            </div>
          </div>

          <template #footer>
            <UButton
              label="Registrar cierre"
              icon="i-lucide-check"
              block
            />
          </template>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>
