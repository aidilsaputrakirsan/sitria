<template>
  <SpotlightCard
    theme="light"
    :spotlight-color="accent"
    :intensity="0.12"
    :spotlight-size="220"
    :border-glow="0.5"
    class-name="h-full !p-5 !rounded-2xl"
  >
    <div class="flex items-start justify-between gap-3">
      <p class="text-sm font-medium text-slate-500">{{ label }}</p>
      <div
        v-if="icon"
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl"
        :style="{ backgroundColor: accent + '14', color: accent }"
      >
        <component :is="icon" class="h-[18px] w-[18px]" />
      </div>
    </div>

    <div class="mt-3 flex items-baseline gap-1 text-slate-900">
      <span v-if="prefix" class="text-lg font-bold text-slate-500">{{ prefix }}</span>
      <!-- Vue Bits Counter: digit bergulir setiap kali nilai berubah (mis. saat filter diganti) -->
      <Counter
        :value="numericValue"
        locale="id-ID"
        :format="format"
        :font-size="size === 'sm' ? 24 : 30"
        font-weight="900"
        :duration="0.8"
        :stagger="0.035"
      />
      <span v-if="suffix" class="text-base font-bold text-slate-500">{{ suffix }}</span>
    </div>

    <p v-if="hint || $slots.hint" class="mt-2 text-xs leading-snug text-slate-500">
      <slot name="hint">{{ hint }}</slot>
    </p>
  </SpotlightCard>
</template>

<script setup>
import { computed } from 'vue'
import SpotlightCard from '../vue-bits/SpotlightCard.vue'
import Counter from '../vue-bits/Counter.vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: Number, default: 0 },
  // 'number' | 'currency' (disingkat: Jt / M) | 'decimal'
  kind: { type: String, default: 'number' },
  hint: { type: String, default: '' },
  icon: { type: [Object, Function], default: null },
  accent: { type: String, default: '#2563eb' },
  suffix: { type: String, default: '' },
  size: { type: String, default: 'md' },
  // jumlah desimal untuk kind='decimal'
  decimals: { type: Number, default: 2 },
})

// Rupiah disingkat agar kartu tetap ringkas: 3.072.992.745 -> "Rp 3,07 M"
const currencyScale = computed(() => {
  const v = Math.abs(props.value || 0)
  if (v >= 1e9) return { div: 1e9, label: 'M' }
  if (v >= 1e6) return { div: 1e6, label: 'Jt' }
  return { div: 1, label: '' }
})

const numericValue = computed(() => {
  const v = Number.isFinite(props.value) ? props.value : 0
  if (props.kind === 'currency') return Math.round((v / currencyScale.value.div) * 100) / 100
  if (props.kind === 'decimal') return Number(v.toFixed(props.decimals))
  return Math.round(v)
})

const format = computed(() => {
  if (props.kind === 'currency') return { minimumFractionDigits: currencyScale.value.div > 1 ? 2 : 0, maximumFractionDigits: 2 }
  if (props.kind === 'decimal') return { minimumFractionDigits: props.decimals, maximumFractionDigits: props.decimals }
  return { maximumFractionDigits: 0 }
})

const prefix = computed(() => (props.kind === 'currency' ? 'Rp' : ''))
const suffix = computed(() => props.suffix || (props.kind === 'currency' ? currencyScale.value.label : ''))
</script>
