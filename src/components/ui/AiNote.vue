<template>
  <p class="flex items-start gap-2 text-xs leading-relaxed text-slate-500">
    <svg class="mt-0.5 h-3.5 w-3.5 shrink-0 text-violet-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
    </svg>
    <span>
      <ShinyText text="Disusun dengan bantuan AI (Claude)" color="#7c3aed" shine-color="#c4b5fd" :speed="3" class-name="font-bold" />
      <span class="text-slate-400"> · </span>
      <slot>Pengelompokan, narasi, dan saran disimpulkan dari seluruh judul karya. Gunakan sebagai bahan diskusi, bukan keputusan final.</slot>
    </span>
  </p>
</template>

<script setup>
import ShinyText from '../vue-bits/ShinyText.vue'
</script>
