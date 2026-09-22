<script setup lang="ts">
definePageMeta({
  layout: 'auth'
})
</script>

<template>
  <UCard>
    <template #header>
      <div class="text-center">
        <h1 class="text-xl font-semibold text-highlighted">
          Iniciar sesión
        </h1>
        <p class="mt-1 text-sm text-muted">
          Accede al prototipo con una cuenta de sucursal o administración.
        </p>
      </div>
    </template>

    <div class="space-y-4">
      <UFormField label="Correo o usuario" required>
        <UInput icon="i-lucide-user" placeholder="usuario@empresa.com" class="w-full" />
      </UFormField>

      <UFormField label="Contraseña" required>
        <UInput type="password" icon="i-lucide-lock-keyhole" placeholder="••••••••" class="w-full" />
      </UFormField>

      <UButton
        to="/operacion"
        label="Entrar al prototipo"
        icon="i-lucide-log-in"
        block
      />

      <UButton
        to="/recuperar-acceso"
        label="¿Olvidaste tus credenciales?"
        color="neutral"
        variant="ghost"
        block
      />
    </div>

    <template #footer>
      <p class="text-center text-xs text-muted">
        Maqueta visual: no existe autenticación real en esta iteración.
      </p>
    </template>
  </UCard>
</template>
