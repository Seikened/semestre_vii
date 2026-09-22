<template>
  <div class="min-h-screen bg-default">
    <div class="absolute right-4 top-4">
      <UColorModeButton color="neutral" variant="ghost" />
    </div>

    <div class="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-6 py-12">
      <div class="mb-8 flex items-center justify-center gap-3">
        <div class="flex size-10 items-center justify-center rounded-xl bg-primary text-inverted">
          <UIcon name="i-lucide-fuel" class="size-5" />
        </div>
        <div>
          <p class="font-semibold text-highlighted">
            Reabastecimiento
          </p>
          <p class="text-xs text-muted">
            Prototipo académico
          </p>
        </div>
      </div>

      <slot />
    </div>
  </div>
</template>
