<script setup lang="ts">
import { VisAxis, VisCrosshair, VisLine, VisTooltip, VisXYContainer } from '@unovis/vue'
import { forecastPoints } from '~/data/reabastecimiento'
import type { ForecastPoint } from '~/types'

const cardRef = useTemplateRef<HTMLElement | null>('cardRef')
const { width } = useElementSize(cardRef)

const x = (_: ForecastPoint, index: number) => index
const actual = (point: ForecastPoint) => point.actual
const predicted = (point: ForecastPoint) => point.forecast
const tick = (index: number) => forecastPoints[index]?.week ?? ''
const format = new Intl.NumberFormat('es-MX', { maximumFractionDigits: 0 })

const tooltip = (point: ForecastPoint) =>
  `${point.week}: real ${format.format(point.actual)}k L · pronóstico ${format.format(point.forecast)}k L`
</script>

<template>
  <UCard ref="cardRef" :ui="{ root: 'overflow-visible', body: 'px-0! pt-0! pb-3!' }">
    <template #header>
      <div>
        <p class="text-xs text-muted uppercase mb-1.5">
          Demanda semanal · estación demo
        </p>
        <p class="text-3xl text-highlighted font-semibold">
          Real vs. pronóstico
        </p>
      </div>
    </template>

    <VisXYContainer
      :data="forecastPoints"
      :padding="{ top: 40 }"
      :margin="{ left: -5, right: -5 }"
      class="h-96"
      :width="width"
    >
      <VisLine :x="x" :y="actual" color="var(--ui-text-highlighted)" />
      <VisLine :x="x" :y="predicted" color="var(--ui-primary)" />
      <VisAxis type="x" :x="x" :tick-format="tick" />
      <VisCrosshair color="var(--ui-primary)" :template="tooltip" />
      <VisTooltip />
    </VisXYContainer>

    <div class="flex items-center gap-5 px-6 pb-2 text-xs text-muted">
      <span class="inline-flex items-center gap-2">
        <span class="size-2 rounded-full bg-neutral-500" />
        Real
      </span>
      <span class="inline-flex items-center gap-2">
        <span class="size-2 rounded-full bg-primary" />
        Pronóstico
      </span>
    </div>
  </UCard>
</template>

<style scoped>
.unovis-xy-container {
  --vis-crosshair-line-stroke-color: var(--ui-primary);
  --vis-crosshair-circle-stroke-color: var(--ui-bg);
  --vis-axis-grid-color: var(--ui-border);
  --vis-axis-tick-color: var(--ui-border);
  --vis-axis-tick-label-color: var(--ui-text-dimmed);
  --vis-tooltip-background-color: var(--ui-bg);
  --vis-tooltip-border-color: var(--ui-border);
  --vis-tooltip-text-color: var(--ui-text-highlighted);
}
</style>
