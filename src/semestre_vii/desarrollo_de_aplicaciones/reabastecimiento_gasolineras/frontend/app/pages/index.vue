<template>
  <UDashboardPanel id="overview">
    <template #header>
      <UDashboardNavbar title="Resumen">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UBadge color="neutral" variant="subtle">
            Maqueta frontend
          </UBadge>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <UAlert
        icon="i-lucide-flask-conical"
        color="neutral"
        variant="subtle"
        title="Prototipo visual"
        description="Todos los valores de esta iteración son simulados. No existe backend, autenticación ni modelo conectado todavía."
      />

      <PrototypeStats />
      <ForecastChart />
      <RecentOrders />
    </template>
  </UDashboardPanel>
</template>
