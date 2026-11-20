<template>
  <div class="space-y-6">
    <PageHeader
      title="SDM & Pakar"
      description="Simulasi rasio DTPS untuk akreditasi dan pencarian dosen pakar berdasarkan ide penelitian."
      :meta="meta"
    />
    <TabNav v-model="activeTab" :tabs="tabs" />

    <!-- Tab Content -->
    <transition name="tab" mode="out-in">
      <div :key="activeTab">
        <DTPSAkreditasi v-if="activeTab === 'akreditasi'" />
        <ExpertiseFinder v-else-if="activeTab === 'pakar'" />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { syncLabel } from '../utils/format.js'
import PageHeader from '../components/ui/PageHeader.vue'
import TabNav from '../components/ui/TabNav.vue'
import DTPSAkreditasi from '../components/DTPSAkreditasi.vue'
import ExpertiseFinder from '../components/ExpertiseFinder.vue'

const DTPSIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>' }
const ExpertiseIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>' }

const tabs = [
  { key: 'akreditasi', label: 'DTPS Akreditasi', icon: DTPSIcon },
  { key: 'pakar', label: 'Cari Pakar', icon: ExpertiseIcon },
]

const activeTab = ref('akreditasi')
const meta = syncLabel('SINTA')
</script>

<style scoped>
.tab-enter-active,
.tab-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.tab-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.tab-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
