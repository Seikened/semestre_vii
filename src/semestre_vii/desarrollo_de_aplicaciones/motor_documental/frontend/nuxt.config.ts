export default defineNuxtConfig({
  compatibilityDate: '2026-10-15',
  modules: ['@nuxt/ui', '@nuxt/eslint'],
  css: ['~/assets/main.css'],
  devtools: { enabled: false },
  ui: { fonts: false },
  colorMode: { preference: 'system', fallback: 'light' },
  runtimeConfig: {
    motorUrl: 'http://api:8000',
    apiKeyFile: '/clave_api/clave'
  },
  app: { head: { htmlAttrs: { lang: 'es' }, title: 'A*' } }
})
