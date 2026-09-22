<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui'

defineProps<{
  collapsed?: boolean
}>()

type ViewMode = 'administration' | 'request'

const modes = [{
  value: 'administration' as const,
  label: 'Administración',
  icon: 'i-lucide-layout-dashboard'
}, {
  value: 'request' as const,
  label: 'Solicitud',
  icon: 'i-lucide-file-plus-2'
}]

const selectedMode = useState<ViewMode>('reabastecimiento-view-mode', () => 'administration')

const currentMode = computed(() => modes.find(mode => mode.value === selectedMode.value) ?? modes[0])

const items = computed<DropdownMenuItem[][]>(() => [[{
  type: 'label',
  label: 'Modo de vista'
}], modes.map(mode => ({
  label: mode.label,
  icon: mode.icon,
  type: 'checkbox' as const,
  checked: selectedMode.value === mode.value,
  onSelect(event: Event) {
    event.preventDefault()
    selectedMode.value = mode.value
  }
}))])
</script>

<template>
  <UDropdownMenu
    :items="items"
    :content="{ align: 'center', collisionPadding: 12 }"
    :ui="{ content: collapsed ? 'w-44' : 'w-(--reka-dropdown-menu-trigger-width)' }"
  >
    <UButton
      v-bind="{
        label: collapsed ? undefined : currentMode.label,
        icon: currentMode.icon,
        trailingIcon: collapsed ? undefined : 'i-lucide-chevrons-up-down'
      }"
      color="neutral"
      variant="ghost"
      block
      :square="collapsed"
      class="data-[state=open]:bg-elevated"
      :class="[!collapsed && 'py-2']"
      :ui="{
        trailingIcon: 'text-dimmed'
      }"
    />
  </UDropdownMenu>
</template>
