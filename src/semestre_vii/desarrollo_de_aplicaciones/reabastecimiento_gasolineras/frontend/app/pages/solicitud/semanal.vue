<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui'

type WeeklyMode = 'pedido' | 'cierre'
type ProductKey = 'regular' | 'premium' | 'diesel'

const route = useRoute()
const router = useRouter()
const formatter = new Intl.NumberFormat('es-MX', { maximumFractionDigits: 0 })

const modeTabs: TabsItem[] = [{
  label: 'Pedido',
  icon: 'i-lucide-file-plus-2',
  value: 'pedido'
}, {
  label: 'Cierre',
  icon: 'i-lucide-clipboard-check',
  value: 'cierre'
}]

const products = [{
  value: 'regular' as const,
  label: 'Regular',
  icon: 'i-lucide-droplets',
  close: 20950,
  recommendation: 21800,
  requested: 22000,
  actual: 21640
}, {
  value: 'premium' as const,
  label: 'Premium',
  icon: 'i-lucide-gem',
  close: 8870,
  recommendation: 9400,
  requested: 9000,
  actual: 9180
}, {
  value: 'diesel' as const,
  label: 'Diésel',
  icon: 'i-lucide-truck',
  close: 16920,
  recommendation: 16400,
  requested: 18000,
  actual: 17260
}]

const productTabs: TabsItem[] = products.map(product => ({
  label: product.label,
  icon: product.icon,
  value: product.value
}))

const mode = ref<WeeklyMode>(route.query.modo === 'cierre' ? 'cierre' : 'pedido')
const activeProduct = ref<ProductKey>('regular')

const orderDraft = reactive<Record<ProductKey, string>>({
  regular: '22,000',
  premium: '9,000',
  diesel: '18,000'
})

const actualDraft = reactive<Record<ProductKey, string>>({
  regular: '21,640',
  premium: '9,180',
  diesel: '17,260'
})

const currentProduct = computed(() => products.find(product => product.value === activeProduct.value) ?? products[0])
const accentColor = computed<'primary' | 'info'>(() => mode.value === 'pedido' ? 'primary' : 'info')
const week = computed(() => mode.value === 'pedido' ? '2026-W39' : '2026-W38')

const activeDraft = computed({
  get: () => mode.value === 'pedido' ? orderDraft[activeProduct.value] : actualDraft[activeProduct.value],
  set: (value: string) => {
    if (mode.value === 'pedido') {
      orderDraft[activeProduct.value] = value
    } else {
      actualDraft[activeProduct.value] = value
    }
  }
})

const numericValue = (value: string) => Number(value.replaceAll(',', '')) || 0
const liters = (value: number) => `${formatter.format(value)} L`

const leftTitle = computed(() => mode.value === 'pedido' ? 'Cierre semanal' : 'Pronóstico')
const leftValue = computed(() => mode.value === 'pedido' ? currentProduct.value.close : currentProduct.value.recommendation)
const rightTitle = computed(() => mode.value === 'pedido' ? 'IA recomienda' : 'Pedido enviado')
const rightValue = computed(() => mode.value === 'pedido' ? currentProduct.value.recommendation : currentProduct.value.requested)
const inputLabel = computed(() => mode.value === 'pedido' ? 'Cantidad a solicitar' : 'Resultado real')
const inputIcon = computed(() => mode.value === 'pedido' ? 'i-lucide-clipboard-pen-line' : 'i-lucide-gauge')
const differenceLabel = computed(() => mode.value === 'pedido' ? 'Diferencia vs. recomendación' : 'Diferencia vs. pedido')
const actionLabel = computed(() => mode.value === 'pedido' ? 'Enviar pedido' : 'Registrar cierre')
const actionIcon = computed(() => mode.value === 'pedido' ? 'i-lucide-send' : 'i-lucide-check')
const summaryTitle = computed(() => mode.value === 'pedido' ? 'Resumen del pedido' : 'Resumen del cierre')

const difference = computed(() => {
  const value = numericValue(activeDraft.value)
  const reference = mode.value === 'pedido' ? currentProduct.value.recommendation : currentProduct.value.requested
  return value - reference
})

const total = computed(() => {
  const values = mode.value === 'pedido' ? Object.values(orderDraft) : Object.values(actualDraft)
  return values.reduce((sum, value) => sum + numericValue(value), 0)
})

function useRecommendation() {
  orderDraft[activeProduct.value] = formatter.format(currentProduct.value.recommendation)
}

watch(() => route.query.modo, (value) => {
  if (value === 'pedido' || value === 'cierre') {
    mode.value = value
  }
})

watch(mode, (value) => {
  if (route.query.modo !== value) {
    router.replace({
      query: {
        ...route.query,
        modo: value
      }
    })
  }
})

useSeoMeta({
  title: 'Operación semanal'
})
</script>

<template>
  <UDashboardPanel id="weekly-operation">
    <template #header>
      <UDashboardNavbar title="Operación semanal">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #trailing>
          <div class="hidden items-center gap-2 sm:flex">
            <UBadge color="neutral" variant="subtle">
              GAS-001
            </UBadge>
            <UBadge color="neutral" variant="subtle">
              {{ week }}
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
            v-model="mode"
            :items="modeTabs"
            :content="false"
            :color="accentColor"
            variant="pill"
          />
        </template>

        <template #right>
          <UTabs
            v-model="activeProduct"
            :items="productTabs"
            :content="false"
            color="neutral"
            variant="pill"
          />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <div class="grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_20rem]">
        <UCard :title="currentProduct.label">
          <div class="grid gap-4 md:grid-cols-2">
            <UPageCard
              :title="leftTitle"
              :icon="mode === 'pedido' ? 'i-lucide-gauge' : 'i-lucide-sparkles'"
              variant="subtle"
            >
              <p class="text-2xl font-semibold text-highlighted">
                {{ liters(leftValue) }}
              </p>
            </UPageCard>

            <UPageCard
              :title="rightTitle"
              :icon="mode === 'pedido' ? 'i-lucide-sparkles' : 'i-lucide-clipboard-check'"
              variant="soft"
              highlight
              :highlight-color="accentColor"
            >
              <p class="text-3xl font-semibold text-highlighted">
                {{ liters(rightValue) }}
              </p>

              <UButton
                v-if="mode === 'pedido'"
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

          <UFormField :label="inputLabel">
            <UInput
              v-model="activeDraft"
              :icon="inputIcon"
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
              {{ differenceLabel }}
            </span>
            <span
              class="font-medium"
              :class="[
                difference === 0
                  ? 'text-highlighted'
                  : mode === 'pedido'
                    ? 'text-primary'
                    : 'text-info'
              ]"
            >
              {{ difference > 0 ? '+' : '' }}{{ liters(difference) }}
            </span>
          </div>
        </UCard>

        <UCard :title="summaryTitle">
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
                {{ mode === 'pedido' ? orderDraft[product.value] : actualDraft[product.value] }} L
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
            <UButton
              :label="actionLabel"
              :icon="actionIcon"
              :color="accentColor"
              block
            />
          </template>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>
