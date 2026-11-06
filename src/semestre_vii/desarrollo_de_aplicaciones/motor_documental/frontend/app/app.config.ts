export default defineAppConfig({
  ui: {
    colors: { primary: 'oai', neutral: 'oai' },
    button: {
      slots: { base: 'rounded-lg oa-button' },
      compoundVariants: [
        { color: ['primary', 'neutral'], variant: 'solid', class: 'oa-button-solid' },
        { color: ['primary', 'neutral'], variant: 'outline', class: 'oa-button-outline' },
        { color: ['primary', 'neutral'], variant: 'soft', class: 'oa-button-soft' },
        { color: ['primary', 'neutral'], variant: 'ghost', class: 'oa-button-ghost' }
      ]
    },
    input: { slots: { base: 'oa-control' } },
    select: {
      slots: { base: 'oa-control', content: 'oa-menu', item: 'oa-menu-item' },
      variants: { variant: { ghost: 'oa-control-ghost' } }
    },
    chatMessage: { compoundVariants: [{ side: 'right', variant: 'soft', class: { content: 'oa-message-user' } }] },
    chatPrompt: {
      slots: {
        root: 'rounded-[24px] px-4 py-3 gap-3',
        base: 'text-base leading-7 px-1',
        footer: 'gap-2'
      },
      variants: { variant: { outline: { root: 'bg-elevated ring ring-default shadow-none' } } },
      defaultVariants: { color: 'neutral' }
    },
    chatPromptSubmit: { slots: { base: 'rounded-full' } },
    modal: { slots: { content: 'rounded-2xl' } }
  }
})
