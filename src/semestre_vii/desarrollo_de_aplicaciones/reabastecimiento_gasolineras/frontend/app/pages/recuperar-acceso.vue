<script setup lang="ts">
definePageMeta({
  layout: 'auth'
})
</script>

<template>
  <UCard>
    <template #header>
      <div>
        <UButton
          to="/login"
          icon="i-lucide-arrow-left"
          color="neutral"
          variant="ghost"
          class="-ms-2 mb-3"
        />
        <h1 class="text-xl font-semibold text-highlighted">
          Recuperar acceso
        </h1>
        <p class="mt-1 text-sm text-muted">
          Representación visual del flujo de recuperación de credenciales.
        </p>
      </div>
    </template>

    <div class="space-y-4">
      <UFormField
        label="Correo o usuario"
        description="La implementación real del mecanismo de recuperación sigue pendiente."
        required
      >
        <UInput icon="i-lucide-mail" placeholder="usuario@empresa.com" class="w-full" />
      </UFormField>

      <UButton
        label="Solicitar recuperación"
        icon="i-lucide-send"
        block
      />

      <UAlert
        icon="i-lucide-info"
        color="neutral"
        variant="subtle"
        title="Sólo prototipo"
        description="Este botón no envía correos ni modifica credenciales."
      />
    </div>
  </UCard>
</template>
