<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

type ViewMode = 'administration' | 'request'

const route = useRoute()
const toast = useToast()
const open = ref(false)
const selectedMode = useState<ViewMode>('reabastecimiento-view-mode', () => 'administration')

const administrationLinks = [{
  label: 'Resumen operativo',
  icon: 'i-lucide-layout-dashboard',
  to: '/operacion',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Pedidos',
  icon: 'i-lucide-clipboard-list',
  to: '/pedidos',
  badge: '8',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Estaciones',
  icon: 'i-lucide-fuel',
  to: '/estaciones',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Cuentas',
  icon: 'i-lucide-users-round',
  to: '/cuentas',
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Modelo',
  icon: 'i-lucide-chart-no-axes-combined',
  to: '/modelo',
  onSelect: () => {
    open.value = false
  }
}] satisfies NavigationMenuItem[]

const requestLinks = [{
  label: 'Inicio',
  icon: 'i-lucide-house',
  to: '/solicitud',
  exact: true,
  onSelect: () => {
    open.value = false
  }
}, {
  label: 'Operación semanal',
  icon: 'i-lucide-calendar-sync',
  to: '/solicitud/semanal',
  onSelect: () => {
    open.value = false
  }
}] satisfies NavigationMenuItem[]

const activeLinks = computed(() => selectedMode.value === 'request' ? requestLinks : administrationLinks)

const groups = computed(() => [{
  id: selectedMode.value,
  label: selectedMode.value === 'request' ? 'Solicitud' : 'Administración',
  items: activeLinks.value
}])

watch(() => route.path, (path) => {
  if (path.startsWith('/solicitud')) {
    selectedMode.value = 'request'
  } else if (['/operacion', '/pedidos', '/estaciones', '/cuentas', '/modelo'].includes(path)) {
    selectedMode.value = 'administration'
  }
}, { immediate: true })

onMounted(async () => {
  const cookie = useCookie('cookie-consent')
  if (cookie.value === 'accepted') {
    return
  }

  toast.add({
    title: 'We use first-party cookies to enhance your experience on our website.',
    duration: 0,
    close: false,
    actions: [{
      label: 'Accept',
      color: 'neutral',
      variant: 'outline',
      onClick: () => {
        cookie.value = 'accepted'
      }
    }, {
      label: 'Opt out',
      color: 'neutral',
      variant: 'ghost'
    }]
  })
})
</script>

<template>
  <UDashboardGroup unit="rem">
    <UDashboardSidebar
      id="default"
      v-model:open="open"
      collapsible
      resizable
      class="bg-elevated/25"
      :ui="{ footer: 'lg:border-t lg:border-default' }"
    >
      <template #header="{ collapsed }">
        <TeamsMenu :collapsed="collapsed" />
      </template>

      <template #default="{ collapsed }">
        <UDashboardSearchButton :collapsed="collapsed" class="bg-transparent ring-default" />

        <UNavigationMenu
          :collapsed="collapsed"
          :items="activeLinks"
          orientation="vertical"
          tooltip
          popover
        />
      </template>

      <template #footer="{ collapsed }">
        <UserMenu :collapsed="collapsed" />
      </template>
    </UDashboardSidebar>

    <UDashboardSearch :groups="groups" />

    <slot />

    <NotificationsSlideover />
  </UDashboardGroup>
</template>
