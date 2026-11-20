<template>
  <!-- Pemilih prodi yang sudah tersinkron, dikelompokkan per jurusan -->
  <label class="inline-flex items-center gap-2 text-sm">
    <span class="font-medium text-slate-500">Prodi</span>
    <select
      :value="modelValue || ''"
      @change="$emit('update:modelValue', $event.target.value)"
      class="rounded-xl border border-slate-200 bg-white px-3 py-2 font-semibold text-slate-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
    >
      <option v-if="allowAll" value="">Semua prodi</option>
      <optgroup v-for="g in groups" :key="g.slug" :label="`Jurusan ${g.short}`">
        <option v-for="p in g.prodi" :key="p.slug" :value="p.slug">{{ p.name }}</option>
      </optgroup>
    </select>
  </label>
</template>

<script setup>
import { prodiList, jurusanList } from '../../data/prodi/index.js'

defineProps({
  modelValue: { type: String, default: null },
  // tampilkan opsi "Semua prodi" (nilai '' = semua)
  allowAll: { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])

const groups = jurusanList
  .map(j => ({ ...j, prodi: prodiList.filter(p => p.hasData && p.jurusanSlug === j.slug) }))
  .filter(g => g.prodi.length)
</script>
