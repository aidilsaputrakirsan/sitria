<template>
  <div class="space-y-6">
    <PageHeader
      title="Pengabdian kepada Masyarakat"
      description="Kegiatan PkM dosen dan pemetaannya terhadap roadmap fakultas."
      :meta="meta"
    >
      <template v-if="['pemetaan'].includes(activeTab)" #actions>
        <ProdiSelect v-model="selectedProdi" />
      </template>
    </PageHeader>
    <TabNav v-model="activeTab" :tabs="tabs" />

    <!-- Tab Content -->
    <transition name="tab" mode="out-in">
      <div :key="activeTab">
        <ResearchGallery v-if="activeTab === 'kegiatan'" initial-tab="services" />
        <RoadmapMapping v-else-if="activeTab === 'pemetaan'" :prodiSlug="selectedProdi" :key="selectedProdi" dataset="services" />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { prodiList } from '../data/prodi/index.js'
import { syncLabel } from '../utils/format.js'
import PageHeader from '../components/ui/PageHeader.vue'
import TabNav from '../components/ui/TabNav.vue'
import ProdiSelect from '../components/ui/ProdiSelect.vue'
import ResearchGallery from '../components/ResearchGallery.vue'
import RoadmapMapping from '../components/RoadmapMapping.vue'

const ServiceIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>' }

const MappingIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }

const tabs = [
  { key: 'kegiatan', label: 'Kegiatan PkM', icon: ServiceIcon },
  { key: 'pemetaan', label: 'Pemetaan Roadmap', icon: MappingIcon },
]

const activeTab = ref('kegiatan')
const meta = syncLabel('SINTA')
// Prodi untuk tab yang datanya per prodi (Statistik, Pemetaan Roadmap)
const selectedProdi = ref(prodiList.find(p => p.hasData)?.slug || null)
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
