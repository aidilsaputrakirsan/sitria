<template>
  <div class="space-y-6">
    <PageHeader
      title="Pengabdian kepada Masyarakat"
      description="Kegiatan PkM dosen, klaster tema & mitra, serta pemetaannya terhadap roadmap fakultas."
      :meta="meta"
    />
    <TabNav v-model="activeTab" :tabs="tabs" />

    <!-- Tab Content -->
    <transition name="tab" mode="out-in">
      <div :key="activeTab">
        <ResearchGallery v-if="activeTab === 'kegiatan'" initial-tab="services" />
        <ResearchClusters v-else-if="activeTab === 'klaster'" initial-type="pengabdian" lock-type />
        <RoadmapMapping v-else-if="activeTab === 'pemetaan'" :prodiSlug="defaultProdi" dataset="services" />
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
import ResearchGallery from '../components/ResearchGallery.vue'
import ResearchClusters from '../components/ResearchClusters.vue'
import RoadmapMapping from '../components/RoadmapMapping.vue'

const ServiceIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>' }
const NetworkIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }

const MappingIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }

const tabs = [
  { key: 'kegiatan', label: 'Kegiatan PkM', icon: ServiceIcon },
  { key: 'klaster', label: 'Klaster & Mitra', icon: NetworkIcon },
  { key: 'pemetaan', label: 'Pemetaan Roadmap', icon: MappingIcon },
]

const activeTab = ref('kegiatan')
const meta = syncLabel('SINTA')
const defaultProdi = computed(() => prodiList.find(p => p.hasData)?.slug || null)
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
