<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const toast = useToast()
const open = ref(false)

const operationLinks = [{
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
  label: 'Modelo',
  icon: 'i-lucide-chart-no-axes-combined',
  to: '/modelo',
  onSelect: () => {
    open.value = false
  }
}] satisfies NavigationMenuItem[]

const settingsLinks = [{
  label: 'Settings',
  to: '/settings',
  icon: 'i-lucide-settings',
  defaultOpen: true,
  type: 'trigger',
  children: [{
    label: 'General',
    to: '/settings',
    exact: true,
    onSelect: () => {
      open.value = false
    }
  }, {
    label: 'Members',
    to: '/settings/members',
    onSelect: () => {
      open.value = false
    }
  }, {
    label: 'Notifications',
    to: '/settings/notifications',
    onSelect: () => {
      open.value = false
    }
  }, {
    label: 'Security',
    to: '/settings/security',
    onSelect: () => {
      open.value = false
    }
  }]
}] satisfies NavigationMenuItem[]

const groups = computed(() => [{
  id: 'operation',
  label: 'Operación',
  items: operationLinks
}, {
  id: 'settings',
  label: 'Settings',
  items: settingsLinks
}])

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
          :items="operationLinks"
          orientation="vertical"
          tooltip
          popover
        />

        <USeparator class="my-2" />

        <UNavigationMenu
          :collapsed="collapsed"
          :items="settingsLinks"
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
