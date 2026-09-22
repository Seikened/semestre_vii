<script setup lang="ts">
import type { TabsItem } from '@nuxt/ui'
import { useInfiniteScroll } from '@vueuse/core'

type ProductKey = 'regular' | 'premium' | 'diesel'
type CaptureMode = 'assisted' | 'modified' | 'manual'

const formatter = new Intl.NumberFormat('es-MX', { maximumFractionDigits: 0 })

const products = [{
  value: 'regular' as const,
  label: 'Regular',
  icon: 'i-lucide-droplets',
  close: 20950,
  recommendation: 21800,
  requested: 22000,
  signal: 'Demanda estable',
  trend: '+2.4 % vs. semana anterior'
}, {
  value: 'premium' as const,
  label: 'Premium',
  icon: 'i-lucide-gem',
  close: 8870,
  recommendation: 9400,
  requested: 9000,
  signal: 'Demanda contenida',
  trend: '-1.1 % vs. semana anterior'
}, {
  value: 'diesel' as const,
  label: 'Diésel',
  icon: 'i-lucide-truck',
  close: 16920,
  recommendation: 16400,
  requested: 18000,
  signal: 'Revisar diferencia',
  trend: '+6.7 % vs. semana anterior'
}]

const productTabs: TabsItem[] = products.map(product => ({
  label: product.label,
  icon: product.icon,
  value: product.value
}))

const captureTabs: TabsItem[] = [{
  label: 'Asistida',
  icon: 'i-lucide-sparkles',
  value: 'assisted'
}, {
  label: 'Modificar',
  icon: 'i-lucide-pencil-line',
  value: 'modified'
}, {
  label: 'Manual',
  icon: 'i-lucide-keyboard',
  value: 'manual'
}]

const activeProduct = ref<ProductKey>('regular')
const captureMode = ref<CaptureMode>('assisted')
const note = ref('')

const closeDraft = reactive<Record<ProductKey, string>>({
  regular: '20,950',
  premium: '8,870',
  diesel: '16,920'
})

const orderDraft = reactive<Record<ProductKey, string>>({
  regular: '22,000',
  premium: '9,000',
  diesel: '18,000'
})

const currentProduct = computed(() => products.find(product => product.value === activeProduct.value) ?? products[0])

const numericValue = (value: string) => Number(value.replaceAll(',', '')) || 0
const liters = (value: number) => `${formatter.format(value)} L`

const currentDifference = computed(() => numericValue(orderDraft[activeProduct.value]) - currentProduct.value.recommendation)
const requestedTotal = computed(() => Object.values(orderDraft).reduce((total, value) => total + numericValue(value), 0))
const recommendedTotal = products.reduce((total, product) => total + product.recommendation, 0)

const captureDescription = computed(() => ({
  assisted: 'Partes de la recomendación y la ajustas sólo si hace falta.',
  modified: 'Conservas la recomendación como referencia y explicas el ajuste.',
  manual: 'Capturas la solicitud desde cero; la recomendación permanece visible como contexto.'
})[captureMode.value])

const historyForProduct = computed(() => {
  const base = currentProduct.value.close

  return Array.from({ length: 24 }, (_, index) => {
    const week = 38 - index
    const observed = Math.round(base * (0.92 + ((index * 7) % 13) / 100))
    const predicted = Math.round(observed * (0.97 + ((index * 3) % 7) / 100))
    const requested = Math.round(observed * (0.99 + ((index * 5) % 6) / 100))

    return {
      id: `${activeProduct.value}-${week}`,
      week: `2026-W${String(week).padStart(2, '0')}`,
      observed: liters(observed),
      predicted: liters(predicted),
      requested: liters(requested)
    }
  })
})

const visibleHistory = ref(historyForProduct.value.slice(0, 8))
const historyScroll = useTemplateRef('historyScroll')

function resetHistory() {
  visibleHistory.value = historyForProduct.value.slice(0, 8)
}

watch(activeProduct, resetHistory)

onMounted(() => {
  useInfiniteScroll(historyScroll.value?.$el, () => {
    const start = visibleHistory.value.length
    visibleHistory.value.push(...historyForProduct.value.slice(start, start + 6))
  }, {
    distance: 120,
    canLoadMore: () => visibleHistory.value.length < historyForProduct.value.length
  })
})

useSeoMeta({
  title: 'Nuevo pedido',
  description: 'Prototipo visual de captura asistida para el pedido semanal de combustible.'
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
    </template>

    <template #body>
      <UPageCard
        title="León Centro 01"
        description="Prepara el suministro de la semana siguiente con el cierre observado y la recomendación como referencias distintas."
        icon="i-lucide-fuel"
        variant="subtle"
        orientation="horizontal"
      >
        <div class="flex flex-wrap items-center gap-2 lg:justify-end">
          <UBadge color="success" variant="subtle">
            Cierre disponible
          </UBadge>
          <UBadge color="neutral" variant="subtle">
            3 productos
          </UBadge>
          <UBadge color="neutral" variant="subtle">
            Prototipo
          </UBadge>
        </div>
      </UPageCard>

      <UCard
        title="Producto"
        description="Trabaja un combustible a la vez sin perder el resumen general del pedido."
      >
        <UTabs
          v-model="activeProduct"
          :items="productTabs"
          :content="false"
          color="neutral"
          variant="pill"
          class="w-full"
          :ui="{ list: 'w-full', trigger: 'flex-1' }"
        />
      </UCard>

      <div class="grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_22rem]">
        <div class="space-y-4">
          <UCard
            :title="`Solicitud de ${currentProduct.label}`"
            :description="captureDescription"
          >
            <template #header>
              <div class="space-y-4">
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p class="text-base font-semibold text-highlighted">
                      Solicitud de {{ currentProduct.label }}
                    </p>
                    <p class="mt-1 text-sm text-muted">
                      {{ captureDescription }}
                    </p>
                  </div>

                  <UBadge
                    :color="activeProduct === 'diesel' ? 'warning' : 'neutral'"
                    variant="subtle"
                  >
                    {{ currentProduct.signal }}
                  </UBadge>
                </div>

                <UTabs
                  v-model="captureMode"
                  :items="captureTabs"
                  :content="false"
                  color="neutral"
                  variant="pill"
                  size="sm"
                  class="w-full"
                />
              </div>
            </template>

            <div class="grid gap-4 lg:grid-cols-2">
              <UCard
                title="Dato observado"
                description="Cierre reportado para esta semana."
                variant="subtle"
              >
                <UFormField
                  label="Cierre reportado"
                  description="Campo provisional hasta confirmar el contrato real."
                >
                  <UInput
                    v-model="closeDraft[activeProduct]"
                    icon="i-lucide-gauge"
                    class="w-full"
                  >
                    <template #trailing>
                      <span class="text-xs text-muted">L</span>
                    </template>
                  </UInput>
                </UFormField>
              </UCard>

              <UPageCard
                title="Recomendación"
                description="Salida del modelo para apoyar la decisión; no representa un hecho observado."
                icon="i-lucide-sparkles"
                variant="soft"
                highlight
                highlight-color="primary"
              >
                <p class="text-3xl font-semibold text-highlighted">
                  {{ liters(currentProduct.recommendation) }}
                </p>
                <div class="mt-3 flex flex-wrap gap-2">
                  <UBadge color="neutral" variant="subtle">
                    {{ currentProduct.trend }}
                  </UBadge>
                  <UBadge color="neutral" variant="subtle">
                    Incertidumbre pendiente
                  </UBadge>
                </div>
              </UPageCard>
            </div>

            <USeparator class="my-5" />

            <div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
              <UFormField
                label="Cantidad a solicitar"
                description="Esta es la decisión de la sucursal y puede diferir de la recomendación."
              >
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

              <UPageCard
                title="Diferencia"
                :description="currentDifference === 0 ? 'Sin ajuste' : 'Contra recomendación'"
                icon="i-lucide-git-compare-arrows"
                variant="subtle"
                class="min-w-44"
              >
                <p
                  class="text-xl font-semibold"
                  :class="currentDifference === 0 ? 'text-highlighted' : 'text-warning'"
                >
                  {{ currentDifference > 0 ? '+' : '' }}{{ liters(currentDifference) }}
                </p>
              </UPageCard>
            </div>

            <UFormField
              class="mt-5"
              label="Comentario de la sucursal"
              description="Úsalo para explicar un ajuste o añadir contexto operativo."
            >
              <UTextarea
                v-model="note"
                placeholder="Añade contexto operativo..."
                autoresize
                :rows="3"
                class="w-full"
              />
            </UFormField>

            <template #footer>
              <UAlert
                icon="i-lucide-circle-help"
                color="neutral"
                variant="subtle"
                title="La recomendación es asistencia"
                description="Puedes aceptarla, modificarla o capturar manualmente. La interfaz mantiene visibles las tres decisiones sin privilegiar una por autoridad."
              />
            </template>
          </UCard>

          <UCard
            title="Histórico reciente"
            description="Contexto visual de semanas anteriores. El scroll carga más fixtures locales sin consultar backend."
          >
            <UScrollArea
              ref="historyScroll"
              v-slot="{ item }"
              :items="visibleHistory"
              :virtualize="{
                estimateSize: 78,
                skipMeasurement: true,
                overscan: 4
              }"
              shadow
              class="h-80 w-full"
            >
              <UPageCard
                :title="item.week"
                :description="`Observado ${item.observed}`"
                icon="i-lucide-calendar-days"
                orientation="horizontal"
                variant="outline"
                class="rounded-none"
              >
                <div class="grid min-w-64 grid-cols-2 gap-4 text-sm">
                  <div>
                    <p class="text-xs text-muted">
                      Pronóstico
                    </p>
                    <p class="font-medium text-highlighted">
                      {{ item.predicted }}
                    </p>
                  </div>
                  <div>
                    <p class="text-xs text-muted">
                      Pedido
                    </p>
                    <p class="font-medium text-highlighted">
                      {{ item.requested }}
                    </p>
                  </div>
                </div>
              </UPageCard>
            </UScrollArea>

            <template #footer>
              <div class="flex items-center justify-between gap-3 text-xs text-muted">
                <span>{{ visibleHistory.length }} de {{ historyForProduct.length }} semanas de maqueta</span>
                <span>Desplázate para ver más</span>
              </div>
            </template>
          </UCard>
        </div>

        <div class="space-y-4 xl:sticky xl:top-4">
          <UCard
            title="Resumen del pedido"
            description="Vista rápida antes de enviar."
          >
            <div class="space-y-4">
              <div
                v-for="product in products"
                :key="product.value"
                class="flex items-center justify-between gap-3"
              >
                <div class="flex items-center gap-3">
                  <div class="flex size-8 items-center justify-center rounded-lg bg-elevated">
                    <UIcon :name="product.icon" class="size-4 text-muted" />
                  </div>
                  <div>
                    <p class="text-sm font-medium text-highlighted">
                      {{ product.label }}
                    </p>
                    <p class="text-xs text-muted">
                      Recom. {{ liters(product.recommendation) }}
                    </p>
                  </div>
                </div>

                <p class="text-sm font-semibold text-highlighted">
                  {{ orderDraft[product.value] }} L
                </p>
              </div>
            </div>

            <template #footer>
              <div class="space-y-3">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-muted">Recomendado</span>
                  <span class="font-medium text-highlighted">{{ liters(recommendedTotal) }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-muted">Solicitado</span>
                  <span class="font-semibold text-highlighted">{{ liters(requestedTotal) }}</span>
                </div>
              </div>
            </template>
          </UCard>

          <UPageCard
            title="Decisión actual"
            :description="captureTabs.find(tab => tab.value === captureMode)?.label"
            icon="i-lucide-route"
            variant="soft"
          >
            <p class="text-sm text-toned">
              {{ captureDescription }}
            </p>
          </UPageCard>

          <UCard>
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

            <template #footer>
              <p class="text-xs text-muted">
                Los botones no producen efectos de dominio en esta maqueta.
              </p>
            </template>
          </UCard>
        </div>
      </div>
    </template>
  </UDashboardPanel>
</template>
