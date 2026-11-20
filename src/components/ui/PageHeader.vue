<template>
  <header
    class="relative overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
    :class="interactive ? 'min-h-[168px]' : ''"
  >
    <!-- Latar interaktif (Vue Bits DotGrid): titik bereaksi pada kursor & klik -->
    <div v-if="interactive" class="absolute inset-0 opacity-70 [mask-image:linear-gradient(90deg,transparent_0%,black_55%)]">
      <DotGrid
        :dot-size="3"
        :gap="22"
        base-color="#dbe3ef"
        active-color="#2563eb"
        :proximity="110"
        :shock-radius="220"
        :shock-strength="3"
        :glow="0.2"
      />
    </div>

    <div class="relative z-10 flex flex-col gap-4 p-6 md:flex-row md:items-end md:justify-between md:p-8 pointer-events-none">
      <div class="min-w-0 max-w-3xl">
        <p v-if="eyebrow" class="mb-1 text-sm font-semibold text-blue-600">{{ eyebrow }}</p>
        <div role="heading" aria-level="1">
          <BlurText
            :key="title"
            :text="title"
            animate-by="words"
            direction="top"
            :delay="90"
            :step-duration="0.3"
            :blur="8"
            :distance="18"
            trigger="load"
            class-name="text-2xl md:text-3xl font-black tracking-tight text-slate-900"
          />
        </div>
        <p v-if="description || $slots.description" class="mt-2 text-sm leading-relaxed text-slate-500">
          <slot name="description">{{ description }}</slot>
        </p>
        <p v-if="meta" class="mt-3 inline-flex items-center gap-2 text-xs font-medium text-slate-500">
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
          {{ meta }}
        </p>
      </div>
      <div v-if="$slots.actions" class="shrink-0 pointer-events-auto">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>

<script setup>
import BlurText from '../vue-bits/BlurText.vue'
import DotGrid from '../vue-bits/DotGrid.vue'

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
  meta: { type: String, default: '' },
  // true = pakai latar DotGrid interaktif (dipakai di halaman Ringkasan)
  interactive: { type: Boolean, default: false },
})
</script>
