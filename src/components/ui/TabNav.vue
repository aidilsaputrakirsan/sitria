<template>
  <div class="tab-scroll -mx-1 overflow-x-auto px-1 py-2">
    <GooeyNav
      :items="items"
      :active-index="activeIndex"
      :on-change="onChange"
      theme="light"
      color="#2563eb"
      active-text-color="#ffffff"
      :colors="['#2563eb', '#60a5fa', '#93c5fd', '#1d4ed8']"
      size="md"
      :particle-count="12"
      :gooeyness="0.45"
    />
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GooeyNav from '../vue-bits/GooeyNav.vue'

/**
 * Tab bersama untuk semua halaman bertab.
 * Tab aktif disimpan di query `?tab=` agar bisa dibagikan / di-bookmark
 * dan tetap sama saat halaman di-refresh.
 */
const props = defineProps({
  tabs: { type: Array, required: true }, // [{ key, label, icon? }]
  modelValue: { type: String, required: true },
})
const emit = defineEmits(['update:modelValue'])

const route = useRoute()
const router = useRouter()

const items = computed(() => props.tabs.map(t => ({ label: t.label, icon: t.icon })))
const activeIndex = computed(() => Math.max(0, props.tabs.findIndex(t => t.key === props.modelValue)))

function onChange(index) {
  const key = props.tabs[index]?.key
  if (!key || key === props.modelValue) return
  emit('update:modelValue', key)
  router.replace({ query: { ...route.query, tab: key } })
}

// Sinkronkan dari URL (misal saat halaman dibuka dari tautan berisi ?tab=)
watch(
  () => route.query.tab,
  (tab) => {
    if (tab && tab !== props.modelValue && props.tabs.some(t => t.key === tab)) {
      emit('update:modelValue', tab)
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.tab-scroll {
  scrollbar-width: none;
}
.tab-scroll::-webkit-scrollbar {
  display: none;
}
</style>
