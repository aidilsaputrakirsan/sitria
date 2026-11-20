<template>
  <div class="space-y-6">
    <PageHeader
      title="Penelitian"
      description="Statistik publikasi, koleksi karya, evolusi topik, dan pemetaan judul terhadap roadmap."
      :meta="meta"
    >
      <template v-if="activeTab === 'statistik'" #actions>
        <ProdiSelect v-model="statProdi" allow-all />
      </template>
      <template v-else-if="activeTab === 'pemetaan'" #actions>
        <ProdiSelect v-model="mapProdi" />
      </template>
    </PageHeader>
    <TabNav v-model="activeTab" :tabs="tabs" />

    <!-- Tab Content -->
    <transition name="tab" mode="out-in">
      <div :key="activeTab">
        <SintaStatistics v-if="activeTab === 'statistik'" :selectedProdi="statProdi || null" :key="statProdi || 'all'" />
        <ResearchGallery v-else-if="activeTab === 'gallery'" />
        <ResearchRoadmap v-else-if="activeTab === 'roadmap'" />
        <RoadmapMapping v-else-if="activeTab === 'pemetaan'" :prodiSlug="mapProdi" :key="mapProdi" />
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
import SintaStatistics from '../components/SintaStatistics.vue'
import ResearchGallery from '../components/ResearchGallery.vue'
import ResearchRoadmap from '../components/ResearchRoadmap.vue'
import RoadmapMapping from '../components/RoadmapMapping.vue'

const StatIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>' }
const GalleryIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>' }
const RoadmapIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg>' }
const MappingIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }

const tabs = [
  { key: 'statistik', label: 'Statistik', icon: StatIcon },
  { key: 'gallery', label: 'Koleksi Karya', icon: GalleryIcon },
  { key: 'roadmap', label: 'Roadmap & Topik', icon: RoadmapIcon },
  { key: 'pemetaan', label: 'Pemetaan Roadmap', icon: MappingIcon },
]

const activeTab = ref('statistik')
const meta = syncLabel('SINTA')
// Statistik: default semua prodi ('' = semua). Pemetaan: per prodi (baru SI yang punya data).
const statProdi = ref('')
const mapProdi = ref(prodiList.find(p => p.hasData)?.slug || null)
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
