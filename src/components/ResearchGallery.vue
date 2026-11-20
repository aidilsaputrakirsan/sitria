<template>
  <div class="space-y-6">
    <!-- Toolbar filter (judul halaman sudah ada di PageHeader + tab) -->
    <div class="sticky top-0 z-20 -mx-1 px-1 py-1">
      <div class="flex flex-wrap items-center gap-3 rounded-2xl border border-slate-200 bg-white/90 p-3 shadow-sm backdrop-blur">
        <div class="relative flex-1 min-w-[220px]">
          <input
            v-model="searchQuery"
            type="search"
            placeholder="Cari judul atau nama dosen..."
            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 pl-10 text-sm text-slate-800 placeholder-slate-400 focus:border-blue-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
          <svg class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
        <select v-if="availableProdi.length > 1" v-model="selectedProdi" class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 focus:border-blue-400 focus:outline-none">
          <option value="all">Semua Prodi</option>
          <option v-for="p in availableProdi" :key="p.slug" :value="p.name">{{ p.name }}</option>
        </select>
        <select v-model="selectedYear" class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 focus:border-blue-400 focus:outline-none">
          <option value="all">Semua Tahun</option>
          <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
        </select>
      </div>
    </div>

    <!-- Trend Chart: Penelitian & Pengabdian per Tahun -->
    <div class="card hover:shadow-lg transition-shadow">
      <div class="mb-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <h3 class="text-lg font-bold text-slate-800">Tren Penelitian & Pengabdian</h3>
          </div>
          <div class="flex gap-2 text-xs">
            <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded flex items-center gap-1">
              <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
              Penelitian
            </span>
            <span class="px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded flex items-center gap-1">
              <span class="w-2 h-2 bg-emerald-500 rounded-full"></span>
              Pengabdian
            </span>
          </div>
        </div>
        <p class="text-xs text-slate-400 mt-1">
          Data {{ selectedProdi === 'all' ? 'semua prodi' : selectedProdi }} dari tahun {{ chartYears[0] || '-' }} hingga {{ chartYears[chartYears.length - 1] || '-' }}
        </p>
      </div>
      <div class="h-64">
        <Line :data="trendChartData" :options="trendChartOptions" />
      </div>
      <p v-if="peakYear.year" class="mt-3 text-xs text-slate-500">
        Puncak aktivitas: <strong class="text-slate-700">{{ peakYear.year }}</strong> dengan {{ peakYear.total }} kegiatan.
      </p>
    </div>

    <!-- Category Tabs -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'px-3.5 py-2 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center gap-2 border',
          activeTab === tab.key
            ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
            : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300 hover:text-slate-900'
        ]"
      >
        <span>{{ tab.label }}</span>
        <span :class="[
          'px-1.5 py-0.5 rounded-md text-[11px] font-bold tabular-nums',
          activeTab === tab.key ? 'bg-white/15 text-white' : 'bg-slate-100 text-slate-500'
        ]">{{ getTabCount(tab.key) }}</span>
      </button>
    </div>

    <!-- Content Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <GlareHover
        v-for="(item, index) in visibleItems"
        :key="`${item.type}-${index}`"
        background="#ffffff"
        border-radius="0.75rem"
        border-color="#f1f5f9"
        glare-color="#ffffff"
        :glare-opacity="0.55"
        :glare-size="45"
        class-name="card group !flex !flex-col !place-items-stretch !text-left w-full !p-5 hover:shadow-md transition-shadow duration-300 cursor-pointer"
        role="button"
        tabindex="0"
        @click="openModal(item)"
        @keydown.enter="openModal(item)"
      >
        <!-- Category Badge -->
        <div class="flex items-center justify-between mb-2">
          <span :class="getBadgeClass(item)">{{ getBadgeText(item) }}</span>
          <span v-if="item.year" class="text-xs text-slate-400 font-medium">{{ item.year }}</span>
        </div>

        <!-- Title -->
        <h3 class="font-semibold text-slate-800 text-sm leading-relaxed mb-4 group-hover:text-blue-700 transition-colors line-clamp-3 min-h-[3.9rem]" :title="item.title">
          {{ item.title }}
        </h3>

        <!-- Author -->
        <div class="flex items-center gap-2 text-xs text-slate-500 mt-auto pt-3 border-t border-slate-100">
          <div class="w-6 h-6 rounded-full overflow-hidden bg-slate-200 flex-shrink-0">
            <img v-if="item.authorPhoto" :src="item.authorPhoto" :alt="item.author" class="w-full h-full object-cover">
            <svg v-else class="w-full h-full p-1 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
          </div>
          <div class="flex flex-col min-w-0">
             <span class="font-medium truncate">{{ item.author }}</span>
             <span class="text-slate-400 text-[10px] truncate">{{ item.prodi }}</span>
          </div>
        </div>
      </GlareHover>
    </div>

    <div v-if="visibleItems.length < filteredItems.length" class="flex justify-center">
      <button
        @click="visibleCount += PAGE_SIZE"
        class="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-300 hover:text-blue-700"
      >
        Tampilkan {{ Math.min(PAGE_SIZE, filteredItems.length - visibleItems.length) }} karya lagi
      </button>
    </div>

    <!-- Modal Detail -->
    <teleport to="body">
      <transition name="modal-fade">
        <div
          v-if="selectedItem"
          class="fixed inset-0 z-50 flex items-center justify-center p-4"
          @click.self="closeModal"
        >
          <!-- Backdrop -->
          <div class="absolute inset-0 bg-slate-900/70 backdrop-blur-sm"></div>

          <!-- Modal Card -->
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <!-- Header modal -->
            <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4">
              <div class="flex items-center gap-2">
                <span :class="getBadgeClass(selectedItem)" class="text-xs">{{ getBadgeText(selectedItem) }}</span>
                <span v-if="selectedItem.year" class="text-xs text-slate-400">{{ selectedItem.year }}</span>
              </div>
              <button
                @click="closeModal"
                aria-label="Tutup"
                class="flex h-8 w-8 items-center justify-center rounded-full text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>

            <!-- Konten Modal -->
            <div class="p-6">
              <!-- Judul -->
              <h2 class="text-lg font-black text-slate-800 leading-snug mb-5">
                {{ selectedItem.title }}
              </h2>

              <!-- Profil Dosen -->
              <div class="flex items-center gap-4 p-4 bg-slate-50 rounded-xl mb-5">
                <div class="w-14 h-14 rounded-full overflow-hidden bg-slate-200 flex-shrink-0 ring-2 ring-white shadow-md">
                  <img
                    v-if="selectedItem.authorPhoto"
                    :src="selectedItem.authorPhoto"
                    :alt="selectedItem.author"
                    class="w-full h-full object-cover"
                    @error="$event.target.style.display='none'"
                  >
                  <svg v-else class="w-full h-full p-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                </div>
                <div>
                  <div class="font-bold text-slate-800 text-sm">{{ selectedItem.author }}</div>
                  <div class="text-xs text-slate-500 mt-0.5">{{ selectedItem.prodi }}</div>
                </div>
              </div>

              <!-- Detail berdasarkan tipe -->
              <!-- Penelitian / Pengabdian -->
              <div v-if="selectedItem.type === 'research' || selectedItem.type === 'services'" class="space-y-3">
                <div class="grid grid-cols-2 gap-3">
                  <div class="bg-slate-50 rounded-xl p-3">
                    <div class="text-xs text-slate-400 font-bold mb-1">Tahun</div>
                    <div class="text-sm font-bold text-slate-700">{{ selectedItem.year || '-' }}</div>
                  </div>
                  <div class="bg-slate-50 rounded-xl p-3">
                    <div class="text-xs text-slate-400 font-bold mb-1">Status</div>
                    <div class="text-sm font-bold" :class="selectedItem.raw?.status === 'Approved' ? 'text-emerald-600' : 'text-slate-600'">
                      {{ selectedItem.raw?.status || '-' }}
                    </div>
                  </div>
                  <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.fundingFormatted">
                    <div class="text-xs text-slate-400 font-bold mb-1">Dana</div>
                    <div class="text-sm font-bold text-rose-600">{{ selectedItem.raw.fundingFormatted }}</div>
                  </div>
                  <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.grantCategory">
                    <div class="text-xs text-slate-400 font-bold mb-1">Kategori Hibah</div>
                    <div class="text-sm font-bold text-slate-700">{{ selectedItem.raw.grantCategory }}</div>
                  </div>
                </div>
                <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.grantType">
                  <div class="text-xs text-slate-400 font-bold mb-1">Jenis Hibah</div>
                  <div class="text-sm text-slate-700">{{ selectedItem.raw.grantType }}</div>
                </div>
                <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.source">
                  <div class="text-xs text-slate-400 font-bold mb-1">Sumber Dana</div>
                  <div class="text-sm text-slate-700">{{ selectedItem.raw.source }}</div>
                </div>
                <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.leader && selectedItem.raw.leader !== selectedItem.raw.grantType">
                  <div class="text-xs text-slate-400 font-bold mb-1">Ketua</div>
                  <div class="text-sm font-medium text-slate-700">{{ selectedItem.raw.leader }}</div>
                </div>
                <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.members?.length">
                  <div class="text-xs text-slate-400 font-bold mb-2">Anggota</div>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="m in selectedItem.raw.members"
                      :key="m"
                      class="px-2.5 py-1 bg-white border border-slate-200 text-slate-600 text-xs rounded-full font-medium"
                    >{{ m }}</span>
                  </div>
                </div>
              </div>

              <!-- Scopus / SINTA / Google Scholar / RAMA -->
              <div v-else-if="['scopus','sinta','google','rama'].includes(selectedItem.type)" class="space-y-3">
                <div class="grid grid-cols-2 gap-3">
                  <div class="bg-slate-50 rounded-xl p-3">
                    <div class="text-xs text-slate-400 font-bold mb-1">Tahun</div>
                    <div class="text-sm font-bold text-slate-700">{{ selectedItem.year || '-' }}</div>
                  </div>
                  <div class="bg-slate-50 rounded-xl p-3">
                    <div class="text-xs text-slate-400 font-bold mb-1">Indeks</div>
                    <div class="text-sm font-bold text-indigo-600">{{ selectedItem.q || '-' }}</div>
                  </div>
                </div>
                <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.journal">
                  <div class="text-xs text-slate-400 font-bold mb-1">Jurnal</div>
                  <div class="text-sm text-slate-700">{{ selectedItem.raw.journal }}</div>
                </div>
                <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.doi">
                  <div class="text-xs text-slate-400 font-bold mb-1">DOI</div>
                  <a :href="'https://doi.org/' + selectedItem.raw.doi" target="_blank" class="text-sm text-blue-600 hover:underline break-all">{{ selectedItem.raw.doi }}</a>
                </div>
              </div>

              <!-- Buku -->
              <div v-else-if="selectedItem.type === 'books'" class="space-y-3">
                <div class="grid grid-cols-2 gap-3">
                  <div class="bg-slate-50 rounded-xl p-3">
                    <div class="text-xs text-slate-400 font-bold mb-1">Tahun</div>
                    <div class="text-sm font-bold text-slate-700">{{ selectedItem.year || '-' }}</div>
                  </div>
                  <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.isbn">
                    <div class="text-xs text-slate-400 font-bold mb-1">ISBN</div>
                    <div class="text-sm font-bold text-slate-700">{{ selectedItem.raw.isbn }}</div>
                  </div>
                </div>
                <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.publisher">
                  <div class="text-xs text-slate-400 font-bold mb-1">Penerbit</div>
                  <div class="text-sm text-slate-700">{{ selectedItem.raw.publisher }}</div>
                </div>
              </div>

              <!-- HKI -->
              <div v-else-if="selectedItem.type === 'ipr'" class="space-y-3">
                <div class="grid grid-cols-2 gap-3">
                  <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.registrationNumber">
                    <div class="text-xs text-slate-400 font-bold mb-1">No. Registrasi</div>
                    <div class="text-sm font-bold text-slate-700">{{ selectedItem.raw.registrationNumber }}</div>
                  </div>
                  <div class="bg-slate-50 rounded-xl p-3" v-if="selectedItem.raw?.year">
                    <div class="text-xs text-slate-400 font-bold mb-1">Tahun</div>
                    <div class="text-sm font-bold text-slate-700">{{ selectedItem.raw.year }}</div>
                  </div>
                </div>
              </div>

            </div><!-- end konten modal -->
          </div>
        </div>
      </transition>
    </teleport>

    <!-- Empty State -->
    <div v-if="filteredItems.length === 0" class="card text-center py-12">
      <svg class="w-16 h-16 mx-auto text-slate-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <h3 class="text-lg font-bold text-slate-600 mb-1">Tidak ada data ditemukan</h3>
      <p class="text-sm text-slate-400">Coba ubah filter atau kata kunci pencarian</p>
    </div>

    <!-- Stats Footer -->
    <div class="text-center text-sm text-slate-500 pt-4">
      <span>Menampilkan <strong class="text-slate-700">{{ visibleItems.length }}</strong> dari <strong class="text-slate-700">{{ filteredItems.length }}</strong> karya yang cocok</span>
    </div>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { prodiRegistry, prodiList } from '../data/prodi/index.js';
import GlareHover from './vue-bits/GlareHover.vue';

const PAGE_SIZE = 24;

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default {
  name: 'ResearchGallery',
  components: {
    Line,
    GlareHover
  },
  props: {
    initialTab: {
      type: String,
      default: 'research'
    }
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeydown);
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeydown);
  },
  data() {
    return {
      activeTab: this.initialTab,
      selectedProdi: 'all',
      selectedYear: 'all',
      searchQuery: '',
      selectedItem: null,
      PAGE_SIZE,
      visibleCount: PAGE_SIZE,
      tabs: [
        { key: 'research', label: 'Penelitian' },
        { key: 'services', label: 'Pengabdian' },
        { key: 'scopus', label: 'Scopus' },
        { key: 'sinta', label: 'SINTA' },
        { key: 'google', label: 'G.Scholar' },
        { key: 'rama', label: 'RAMA' },
        { key: 'books', label: 'Buku' },
        { key: 'ipr', label: 'HKI' }
      ],
      trendChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleColor: '#fff',
            bodyColor: '#cbd5e1',
            borderColor: 'rgba(148, 163, 184, 0.2)',
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
              title: (items) => `Tahun ${items[0].label}`,
              label: (item) => ` ${item.dataset.label}: ${item.raw} karya`
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: '#64748b',
              font: {
                weight: 'bold',
                size: 11
              }
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(148, 163, 184, 0.1)'
            },
            ticks: {
              color: '#64748b',
              font: {
                weight: 'bold'
              },
              stepSize: 5
            }
          }
        },
        elements: {
          line: {
            tension: 0.4
          },
          point: {
            radius: 4,
            hoverRadius: 6
          }
        }
      }
    };
  },
  computed: {
    availableProdi() {
      return prodiList.filter(p => p.hasData);
    },
    lecturers() {
      const allLecturers = [];
      prodiList.filter(p => p.hasData).forEach(p => {
        const data = prodiRegistry[p.slug];
        if (data?.sintaData?.lecturers) allLecturers.push(...data.sintaData.lecturers);
      });
      return allLecturers;
    },

    // Filtered lecturers based on prodi selection
    filteredLecturers() {
      if (this.selectedProdi === 'all') {
        return this.lecturers;
      }
      return this.lecturers.filter(lec => lec.prodi === this.selectedProdi);
    },

    // Get all years for the chart (sorted ascending)
    chartYears() {
      const years = new Set();
      this.filteredLecturers.forEach(lec => {
        (lec.research || []).forEach(r => {
          if (r.year) years.add(String(r.year));
        });
        (lec.services || []).forEach(s => {
          if (s.year) years.add(String(s.year));
        });
      });
      return [...years].sort((a, b) => Number(a) - Number(b));
    },

    // Research data by year (filtered by prodi)
    researchByYear() {
      const data = {};
      this.chartYears.forEach(y => data[y] = 0);
      this.filteredLecturers.forEach(lec => {
        (lec.research || []).forEach(r => {
          const y = String(r.year);
          if (data[y] !== undefined) data[y]++;
        });
      });
      return data;
    },

    // Services data by year (filtered by prodi)
    servicesByYear() {
      const data = {};
      this.chartYears.forEach(y => data[y] = 0);
      this.filteredLecturers.forEach(lec => {
        (lec.services || []).forEach(s => {
          const y = String(s.year);
          if (data[y] !== undefined) data[y]++;
        });
      });
      return data;
    },

    // Total research filtered
    totalResearchFiltered() {
      return Object.values(this.researchByYear).reduce((a, b) => a + b, 0);
    },

    // Total services filtered
    totalServicesFiltered() {
      return Object.values(this.servicesByYear).reduce((a, b) => a + b, 0);
    },

    // Peak year (most combined research + services)
    peakYear() {
      let maxYear = null;
      let maxTotal = 0;
      this.chartYears.forEach(y => {
        const total = (this.researchByYear[y] || 0) + (this.servicesByYear[y] || 0);
        if (total > maxTotal) {
          maxTotal = total;
          maxYear = y;
        }
      });
      return { year: maxYear, total: maxTotal };
    },

    // Chart data for Line chart
    trendChartData() {
      return {
        labels: this.chartYears,
        datasets: [
          {
            label: 'Penelitian',
            data: this.chartYears.map(y => this.researchByYear[y] || 0),
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.15)',
            fill: true,
            borderWidth: 3,
            pointBackgroundColor: '#3b82f6',
            pointBorderColor: '#fff',
            pointBorderWidth: 2
          },
          {
            label: 'Pengabdian',
            data: this.chartYears.map(y => this.servicesByYear[y] || 0),
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            fill: true,
            borderWidth: 3,
            pointBackgroundColor: '#10b981',
            pointBorderColor: '#fff',
            pointBorderWidth: 2
          }
        ]
      };
    },

    allItems() {
      const items = [];
      
      this.lecturers.forEach(lec => {
        const authorPhoto = lec.photo || null;

        // Research
        (lec.research || []).forEach(r => {
          items.push({
            type: 'research',
            title: r.title,
            year: r.year,
            author: lec.name,
            authorPhoto,
            prodi: lec.prodi,
            raw: r
          });
        });

        // Services
        (lec.services || []).forEach(s => {
          items.push({
            type: 'services',
            title: s.title,
            year: s.year,
            author: lec.name,
            authorPhoto,
            prodi: lec.prodi,
            raw: s
          });
        });

        // Documents (Scopus, SINTA, Google Scholar, RAMA)
        (lec.documents?.list || []).forEach(d => {
          let type = 'sinta';
          let categoryUpper = (d.category || '').toUpperCase();

          if (categoryUpper.includes('SCOPUS')) type = 'scopus';
          else if (categoryUpper.includes('SINTA')) type = 'sinta';
          else if (categoryUpper.includes('GOOGLE')) type = 'google';
          else if (categoryUpper.includes('RAMA')) type = 'rama';

          items.push({
            type: type,
            title: d.title,
            q: d.category,
            year: d.year,
            author: lec.name,
            authorPhoto,
            prodi: lec.prodi,
            raw: d
          });
        });

        // Books
        (lec.books || []).forEach(b => {
          items.push({
            type: 'books',
            title: b.title,
            year: b.year,
            author: lec.name,
            authorPhoto,
            prodi: lec.prodi,
            raw: b
          });
        });

        // IPR
        (lec.ipr?.list || []).forEach(i => {
          items.push({
            type: 'ipr',
            title: i.title,
            category: i.category,
            author: lec.name,
            authorPhoto,
            prodi: lec.prodi,
            raw: i
          });
        });
      });

      return items;
    },

    totalItems() {
      return this.allItems.length;
    },

    availableYears() {
      const years = new Set();
      this.allItems.forEach(item => {
        if (item.year) years.add(item.year);
      });
      return [...years].sort((a, b) => b - a);
    },

    filteredItems() {
      return this.allItems.filter(item => {
        // Filter by tab/type
        if (item.type !== this.activeTab) return false;

        // Filter by prodi
        if (this.selectedProdi !== 'all' && item.prodi !== this.selectedProdi) return false;

        // Filter by year
        if (this.selectedYear !== 'all' && item.year !== this.selectedYear) return false;

        // Filter by search
        if (this.searchQuery) {
          const query = this.searchQuery.toLowerCase();
          const matchTitle = item.title?.toLowerCase().includes(query);
          const matchAuthor = item.author?.toLowerCase().includes(query);
          if (!matchTitle && !matchAuthor) return false;
        }

        return true;
      });
    },
    // Render bertahap agar ratusan kartu tidak dimuat sekaligus
    visibleItems() {
      return this.filteredItems.slice(0, this.visibleCount);
    }
  },

  watch: {
    // Filter berubah -> mulai lagi dari halaman pertama
    activeTab() { this.visibleCount = PAGE_SIZE; },
    selectedProdi() { this.visibleCount = PAGE_SIZE; },
    selectedYear() { this.visibleCount = PAGE_SIZE; },
    searchQuery() { this.visibleCount = PAGE_SIZE; }
  },

  methods: {
    getTabCount(tabKey) {
      let items = this.allItems.filter(i => i.type === tabKey);
      
      if (this.selectedProdi !== 'all') {
        items = items.filter(i => i.prodi === this.selectedProdi);
      }
      
      return items.length;
    },

    getBadgeClass(item) {
      const base = 'px-2 py-1 rounded-lg text-xs font-bold';
      
      if (item.type === 'research') return `${base} bg-blue-100 text-blue-700`;
      if (item.type === 'services') return `${base} bg-emerald-100 text-emerald-700`;
      
      if (item.type === 'scopus') {
        const cat = (item.q || '').toUpperCase();
        if (cat.includes('Q1')) return `${base} bg-indigo-200 text-indigo-800`;
        if (cat.includes('Q2')) return `${base} bg-indigo-100 text-indigo-700`;
        if (cat.includes('Q3')) return `${base} bg-indigo-50 text-indigo-600`;
        if (cat.includes('Q4')) return `${base} bg-slate-100 text-indigo-500`;
        return `${base} bg-slate-100 text-slate-500`;
      }
      
      if (item.type === 'sinta') {
        const cat = (item.q || '').toUpperCase();
        if (cat.includes('S1')) return `${base} bg-sky-200 text-sky-800`;
        if (cat.includes('S2')) return `${base} bg-sky-100 text-sky-700`;
        if (cat.includes('S3')) return `${base} bg-sky-50 text-sky-600`;
        return `${base} bg-slate-100 text-sky-500`;
      }

      if (item.type === 'google') return `${base} bg-orange-100 text-orange-700`;
      if (item.type === 'rama') return `${base} bg-pink-100 text-pink-700`;
      
      if (item.type === 'books') return `${base} bg-teal-100 text-teal-700`;
      
      if (item.type === 'ipr') {
        if (item.category === 'hakCipta') return `${base} bg-amber-100 text-amber-700`;
        if (item.category === 'paten') return `${base} bg-purple-100 text-purple-700`;
        return `${base} bg-slate-100 text-slate-600`;
      }
      
      return `${base} bg-slate-100 text-slate-600`;
    },

    getBadgeText(item) {
      if (item.type === 'research') return 'Penelitian';
      if (item.type === 'services') return 'Pengabdian';
      if (item.type === 'scopus') return item.q || 'Scopus';
      if (item.type === 'sinta') return item.q || 'SINTA';
      if (item.type === 'google') return 'Google Scholar';
      if (item.type === 'rama') return 'RAMA';
      if (item.type === 'books') return 'Buku';
      if (item.type === 'ipr') {
        if (item.category === 'hakCipta') return 'Hak Cipta';
        if (item.category === 'paten') return 'Paten';
        return 'HKI';
      }
      return item.type;
    },


    openModal(item) {
      this.selectedItem = item;
      document.body.style.overflow = 'hidden';
    },

    closeModal() {
      this.selectedItem = null;
      document.body.style.overflow = '';
    },

    handleKeydown(e) {
      if (e.key === 'Escape') this.closeModal();
    }
  }
};
</script>

<style scoped>
.card {
  @apply bg-white p-5 rounded-2xl border border-slate-200 shadow-sm;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Modal transition */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-active .relative,
.modal-fade-leave-active .relative {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from .relative {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}
</style>
