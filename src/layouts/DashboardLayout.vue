<template>
  <div class="flex h-screen bg-slate-50 text-slate-600 font-sans selection:bg-rose-500/30">
    <!-- Sidebar -->
    <aside 
      class="fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-slate-200 transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-0 flex flex-col"
      :class="mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Sidebar Header -->
      <div class="h-20 flex items-center px-5 border-b border-slate-100">
        <div class="flex items-center gap-3 w-full">
          <div class="w-12 h-12 bg-white rounded-xl flex items-center justify-center border border-slate-200 p-1.5 shrink-0">
            <img :src="`${baseUrl}images/logoSITRIA.png`" alt="SITRIA" class="w-full h-full object-contain" />
          </div>
          <div class="flex-1 min-w-0">
            <h1 class="font-black text-lg tracking-tight leading-tight">
              <GradientText :colors="['#1e3a8a', '#2563eb', '#38bdf8', '#2563eb', '#1e3a8a']" :animation-speed="10">SITRIA</GradientText>
              <span class="text-slate-300 font-bold"> · </span><span class="text-slate-700">FSTI</span>
            </h1>
            <p class="text-xs text-slate-400 leading-tight mt-0.5">Sistem Informasi Tridarma Akademik</p>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto py-5 px-3 space-y-0.5 custom-scrollbar">
        <template v-for="item in menuItems" :key="item.isHeader ? `h-${item.label}` : item.path">
          <p v-if="item.isHeader" class="px-3 pt-5 pb-1.5 text-xs font-semibold text-slate-400">{{ item.label }}</p>
          <router-link
            v-else
            :to="item.path"
            class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors"
            :class="$route.path === item.path
              ? 'bg-slate-100 font-semibold text-slate-900'
              : 'font-medium text-slate-500 hover:bg-slate-50 hover:text-slate-900'"
          >
            <component
              :is="item.icon"
              class="h-5 w-5"
              :class="$route.path === item.path ? 'text-blue-600' : 'text-slate-400'"
            />
            <span>{{ item.label }}</span>
          </router-link>
        </template>
      </nav>

      <!-- Sumber data + kredit (ringkas) -->
      <div class="px-5 pt-4 pb-5 border-t border-slate-100 space-y-4">
        <div>
          <p class="text-xs font-semibold text-slate-400 mb-2">Sumber data</p>
          <div class="flex flex-wrap gap-x-3 gap-y-1.5">
            <a
              v-for="src in dataSources"
              :key="src.label"
              :href="src.href"
              target="_blank"
              rel="noopener"
              class="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-blue-600 transition-colors"
            >
              <span class="w-1.5 h-1.5 rounded-full" :class="src.dot"></span>{{ src.label }}
            </a>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <img :src="`${baseUrl}images/profil.jpg`" alt="ADL" class="w-8 h-8 rounded-full object-cover border-2 border-white shadow-sm shrink-0" />
          <p class="text-xs text-slate-500 leading-tight">Dibuat oleh <span class="font-black text-slate-700">ADL</span></p>
        </div>
      </div>
    </aside>

    <!-- Overlay for mobile -->
    <div 
      v-if="mobileMenuOpen" 
      class="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-40 md:hidden transition-opacity"
      @click="mobileMenuOpen = false"
    ></div>

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col min-w-0 overflow-hidden bg-slate-50 relative">
      <!-- Top Bar Mobile -->
      <div class="md:hidden h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-4 sticky top-0 z-30">
         <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 bg-white rounded-lg flex items-center justify-center border border-slate-100 p-1">
              <img :src="`${baseUrl}images/logoSITRIA.png`" alt="SITRIA" class="w-full h-full object-contain" />
            </div>
            <div class="flex flex-col leading-tight">
              <span class="font-bold text-slate-800 text-sm">SITRIA <span class="text-slate-400">·</span> FSTI</span>
              <span class="text-[11px] text-slate-400">Tridarma Akademik</span>
            </div>
         </div>
         <button @click="mobileMenuOpen = true" class="p-2 text-slate-500 hover:text-slate-900 rounded-lg hover:bg-slate-100 transition-colors">
           <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
           </svg>
         </button>
      </div>

      <!-- Content -->
      <!-- id dipakai Vue Bits FadeContent (GSAP ScrollTrigger) sebagai scroller -->
      <div id="snap-main-container" class="flex-1 overflow-y-auto custom-scrollbar p-4 md:p-8 md:pt-10 scroll-smooth">
        <ClickSpark spark-color="#3b82f6" :spark-size="9" :spark-radius="22" :spark-count="7" :duration="420" class-name="!h-auto">
        <div class="max-w-7xl mx-auto w-full">
           <router-view v-slot="{ Component }">
            <transition 
              name="page" 
              mode="out-in"
              enter-active-class="transition-all duration-300 ease-out"
              leave-active-class="transition-all duration-200 ease-in"
              enter-from-class="opacity-0 translate-y-4"
              enter-to-class="opacity-100 translate-y-0"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 -translate-y-4"
            >
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
        </ClickSpark>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import GradientText from '../components/vue-bits/GradientText.vue'
import ClickSpark from '../components/vue-bits/ClickSpark.vue'

const mobileMenuOpen = ref(false)
const baseUrl = import.meta.env.BASE_URL
const route = useRoute()

// Tutup menu mobile setiap kali pindah halaman
watch(() => route.path, () => { mobileMenuOpen.value = false })

const dataSources = [
  { label: 'SINTA', href: 'https://sinta.kemdiktisaintek.go.id', dot: 'bg-blue-400' },
  { label: 'Google Scholar', href: 'https://scholar.google.com', dot: 'bg-emerald-400' },
  { label: 'PDDikti', href: 'https://pddikti.kemdiktisaintek.go.id', dot: 'bg-amber-400' },
  { label: 'Repository ITK', href: 'https://repository.itk.ac.id', dot: 'bg-purple-400' },
]

// Modern Minimalist Icons
const DashboardIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>' }
const TeachingIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>' }
const ResearchIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>' }
const ServiceIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>' }
const ExpertiseIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>' }
const FundingIcon = { template: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' }

const menuItems = [
  { path: '/dashboard', label: 'Ringkasan', icon: DashboardIcon },

  { isHeader: true, label: 'Tridarma' },
  { path: '/pengajaran', label: 'Pengajaran', icon: TeachingIcon },
  { path: '/penelitian', label: 'Penelitian', icon: ResearchIcon },
  { path: '/pengabdian', label: 'Pengabdian', icon: ServiceIcon },

  { isHeader: true, label: 'Pendukung' },
  { path: '/sdm-pakar', label: 'SDM & Pakar', icon: ExpertiseIcon },
  { path: '/funding', label: 'Pendanaan', icon: FundingIcon },
]
</script>

<style scoped>
/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: #94a3b8;
}

</style>
