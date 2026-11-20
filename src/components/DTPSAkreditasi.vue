<template>
  <div class="space-y-6">
    <!-- 2. FILTER PRODI & TAHUN -->
    <div class="card">
      <div class="flex flex-wrap items-center gap-6">
        <!-- Filter Prodi -->
        <div>
          <span class="text-sm font-bold text-slate-700 block mb-2">Program Studi:</span>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="prodi in prodiList"
              :key="prodi"
              @click="selectedProdi = prodi"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-bold transition-all',
                selectedProdi === prodi
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              ]"
            >
              {{ prodi }}
            </button>
          </div>
        </div>

        <!-- Filter Tahun -->
        <div>
          <span class="text-sm font-bold text-slate-700 block mb-2">Periode:</span>
          <div class="flex items-center gap-2">
            <select v-model="startYear" class="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
              <option v-for="year in availableYears" :key="'start-' + year" :value="year">{{ year }}</option>
            </select>
            <span class="text-slate-500">s/d</span>
            <select v-model="endYear" class="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
              <option v-for="year in availableYears" :key="'end-' + year" :value="year">{{ year }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- KPI rasio: digit bergulir setiap kali dosen dicentang / periode diganti -->
    <FadeContent :stagger="0.07" :duration="0.6" class-name="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <KpiCard label="Jumlah DTPS" :value="currentDtpsCount" accent="#4f46e5" :hint="`Homebase + lintas prodi terpilih`" />
      <KpiCard label="Penelitian / DTPS" :value="Number(ratioResearchPerDtps)" kind="decimal" accent="#2563eb" :hint="`${filteredResearchCount} penelitian ÷ ${currentDtpsCount} DTPS`" />
      <KpiCard label="Pengabdian / DTPS" :value="Number(ratioServicePerDtps)" kind="decimal" accent="#059669" :hint="`${filteredServiceCount} pengabdian ÷ ${currentDtpsCount} DTPS`" />
      <KpiCard label="Dana / DTPS" :value="avgFundingPerDtps" kind="currency" accent="#d97706" :hint="`${formatCurrencyShort(totalSelectedFunding)} ÷ ${currentDtpsCount} DTPS`" />
    </FadeContent>

    <!-- 3. TABEL DTPS DENGAN CHECKBOX -->
    <div class="card hover:shadow-lg transition-shadow">
      <div class="mb-4">
        <div class="flex items-center justify-between">
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-bold text-slate-800">Daftar DTPS - {{ selectedProdi }}</h3>
            </div>
            <p class="text-xs text-slate-400 mt-1">Centang dosen dari prodi lain untuk menambahkan ke hitungan DTPS</p>
          </div>
          <div class="flex items-center gap-2 text-sm">
            <span class="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-lg font-bold">{{ currentDtpsCount }} DTPS terpilih</span>
          </div>
        </div>
      </div>

      <p class="mb-4 text-xs leading-relaxed text-slate-500">
        <span class="font-bold text-indigo-700">Homebase</span> otomatis terhitung.
        Centang <span class="font-bold text-purple-700">dosen lintas prodi</span> yang ikut mengajar untuk mensimulasikan rasio.
        Pilihan tidak disimpan dan kembali semula saat halaman dimuat ulang.
      </p>

      <div class="overflow-x-auto max-h-[600px] overflow-y-auto">
        <table class="w-full text-sm">
          <thead class="sticky top-0 bg-white z-10">
            <tr class="border-b border-slate-200 bg-slate-50">
              <th class="text-center py-3 px-2 font-bold text-slate-700 w-12">✓</th>
              <th class="text-left py-3 px-4 font-bold text-slate-700">Nama Dosen</th>
              <th class="text-center py-3 px-4 font-bold text-slate-700">Homebase</th>
              <th class="text-center py-3 px-2 font-bold text-slate-700 bg-blue-50">Penelitian</th>
              <th class="text-center py-3 px-2 font-bold text-slate-700 bg-emerald-50">Pengabdian</th>
              <th class="text-right py-3 px-4 font-bold text-slate-700 bg-amber-50">Total Dana</th>
              <th class="text-center py-3 px-4 font-bold text-slate-700">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="lecturer in allLecturersWithData" 
              :key="lecturer.name" 
              :class="[
                'border-b border-slate-100 hover:bg-slate-50 transition-colors',
                lecturer.isHomebase ? '' : 'bg-purple-50/30'
              ]"
            >
              <td class="py-3 px-2 text-center">
                <input 
                  type="checkbox" 
                  :checked="isSelected(lecturer)"
                  :disabled="lecturer.isHomebase"
                  @change="toggleLecturer(lecturer)"
                  :class="[
                    'w-5 h-5 rounded border-2 transition-all cursor-pointer',
                    lecturer.isHomebase 
                      ? 'text-indigo-600 border-indigo-300 cursor-not-allowed' 
                      : 'text-purple-600 border-purple-300 hover:border-purple-500'
                  ]"
                />
              </td>
              <td class="py-3 px-4">
                <div class="font-medium text-slate-800">{{ lecturer.name }}</div>
              </td>
              <td class="py-3 px-4 text-center">
                <span :class="[
                  'px-2 py-1 rounded-full text-xs font-bold',
                  lecturer.isHomebase 
                    ? 'bg-indigo-100 text-indigo-700' 
                    : 'bg-purple-100 text-purple-700'
                ]">
                  {{ lecturer.homebase }}
                </span>
              </td>
              <td class="py-3 px-2 text-center">
                <span v-if="lecturer.researchCount > 0" class="font-semibold tabular-nums text-slate-800">{{ lecturer.researchCount }}</span>
                <span v-else class="text-slate-300">-</span>
              </td>
              <td class="py-3 px-2 text-center">
                <span v-if="lecturer.serviceCount > 0" class="font-semibold tabular-nums text-slate-800">{{ lecturer.serviceCount }}</span>
                <span v-else class="text-slate-300">-</span>
              </td>
              <td class="py-3 px-4 text-right">
                <span class="text-sm font-semibold tabular-nums text-slate-800">{{ formatCurrencyShort(lecturer.totalFunding) }}</span>
              </td>
              <td class="py-3 px-4 text-center">
                <span :class="[
                  'px-2 py-1 rounded-lg text-xs font-bold',
                  lecturer.isHomebase 
                    ? 'bg-indigo-100 text-indigo-700' 
                    : isSelected(lecturer) 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-slate-100 text-slate-500'
                ]">
                  {{ lecturer.isHomebase ? 'DTPS' : isSelected(lecturer) ? 'Ditambahkan' : 'Lintas Prodi' }}
                </span>
              </td>
            </tr>
          </tbody>
          <tfoot class="sticky bottom-0 bg-slate-100">
            <tr class="font-bold">
              <td class="py-3 px-2"></td>
              <td class="py-3 px-4 text-slate-800">
                TOTAL DTPS ({{ currentDtpsCount }} dosen)
                <span class="block text-xs font-normal text-slate-500">Judul unik; judul yang dikerjakan beberapa dosen dihitung sekali</span>
              </td>
              <td class="py-3 px-4"></td>
              <td class="py-3 px-2 text-center">
                <span class="font-semibold tabular-nums text-slate-800">{{ filteredResearchCount }}</span>
              </td>
              <td class="py-3 px-2 text-center">
                <span class="font-semibold tabular-nums text-slate-800">{{ filteredServiceCount }}</span>
              </td>
              <td class="py-3 px-4 text-right">
                <span class="text-sm font-semibold tabular-nums text-slate-800">{{ formatCurrencyShort(totalSelectedFunding) }}</span>
              </td>
              <td class="py-3 px-4"></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- 4. CARA PERHITUNGAN (ringkas, bisa dibuka) -->
    <details class="card group">
      <summary class="flex cursor-pointer list-none items-center justify-between gap-3">
        <span class="text-sm font-bold text-slate-800">Cara perhitungan indikator (LKPS BAN-PT)</span>
        <svg class="h-4 w-4 text-slate-400 transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
      </summary>
      <dl class="mt-4 grid grid-cols-1 gap-3 text-xs md:grid-cols-2">
        <div class="rounded-lg bg-slate-50 p-3"><dt class="font-bold text-slate-700">Rasio Penelitian</dt><dd class="mt-1 tabular-nums text-slate-700">Jumlah judul penelitian ÷ jumlah DTPS</dd></div>
        <div class="rounded-lg bg-slate-50 p-3"><dt class="font-bold text-slate-700">Rasio Pengabdian</dt><dd class="mt-1 tabular-nums text-slate-700">Jumlah kegiatan PkM ÷ jumlah DTPS</dd></div>
        <div class="rounded-lg bg-slate-50 p-3"><dt class="font-bold text-slate-700">Dana per DTPS</dt><dd class="mt-1 tabular-nums text-slate-700">Total dana penelitian + PkM ÷ jumlah DTPS</dd></div>
        <div class="rounded-lg bg-slate-50 p-3"><dt class="font-bold text-slate-700">Total Aktivitas / DTPS</dt><dd class="mt-1 tabular-nums text-slate-700">(Penelitian + PkM) ÷ DTPS = <strong class="text-slate-800">{{ ratioTotalPerDtps }}</strong></dd></div>
      </dl>
      <p class="mt-3 text-xs text-slate-500">Data SINTA, periode {{ startYear }}–{{ endYear }}.</p>
    </details>
  </div>
</template>

<script>
import { prodiRegistry, prodiList as prodiListData } from '../data/prodi/index.js'
import KpiCard from './ui/KpiCard.vue'
import FadeContent from './vue-bits/FadeContent.vue'

export default {
  name: 'DTPSAkreditasi',
  components: { KpiCard, FadeContent },
  data() {
    return {
      selectedProdi: 'Sistem Informasi',
      startYear: '',
      endYear: '',
      additionalDtps: [] // nama dosen lintas prodi yang ditambahkan
    }
  },
  created() {
    // Set default 3 tahun terakhir
    const currentYear = new Date().getFullYear()
    this.endYear = String(currentYear)
    this.startYear = String(currentYear - 2)
  },
  computed: {
    lecturers() {
      const allLecturers = []
      prodiListData.filter(p => p.hasData).forEach(p => {
        const data = prodiRegistry[p.slug]
        if (data?.sintaData?.lecturers) allLecturers.push(...data.sintaData.lecturers)
      })
      return allLecturers
    },

    prodiList() {
      return prodiListData.filter(p => p.hasData).map(p => p.name).sort()
    },

    availableYears() {
      const years = new Set()
      this.lecturers.forEach(lecturer => {
        if (lecturer.research) {
          lecturer.research.forEach(r => {
            if (r.year && r.year !== 'Unknown') years.add(r.year)
          })
        }
        if (lecturer.services) {
          lecturer.services.forEach(s => {
            if (s.year && s.year !== 'Unknown') years.add(s.year)
          })
        }
      })
      return Array.from(years).sort((a, b) => b.localeCompare(a))
    },

    // Daftar nama dosen per prodi
    lecturersByProdi() {
      const result = {}
      prodiListData.filter(p => p.hasData).forEach(p => {
        const data = prodiRegistry[p.slug]
        if (data?.config) {
          result[p.name] = data.config.lecturers || []
        }
      })
      return result
    },

    // Semua dosen dengan data penelitian/pengabdian
    allLecturersWithData() {
      const result = []
      const homebaseLecturers = this.lecturersByProdi[this.selectedProdi] || []
      const homebaseNames = new Set(homebaseLecturers.map(l => this.normalizeName(l.name)))

      // Ambil semua nama dosen dari semua prodi
      const allProdiLecturers = []
      for (const [prodiName, lecturers] of Object.entries(this.lecturersByProdi)) {
        lecturers.forEach(l => {
          allProdiLecturers.push({
            ...l,
            homebase: prodiName,
            isHomebase: prodiName === this.selectedProdi
          })
        })
      }

      // Hitung data penelitian dan pengabdian per dosen
      allProdiLecturers.forEach(lecturer => {
        // Cocokkan lewat SINTA ID (pasti), baru nama lengkap ternormalisasi sebagai cadangan.
        // Dulu memakai kata pertama nama, sehingga mis. "Dwi Nur Amalia" mendapat data "Dwi Arief".
        const normalizedName = this.normalizeName(lecturer.name)
        const sintaLecturer =
          (lecturer.sintaId && this.lecturers.find(l => String(l.sintaId) === String(lecturer.sintaId))) ||
          this.lecturers.find(l => this.normalizeName(l.name) === normalizedName)

        let researchCount = 0
        let serviceCount = 0
        let totalFunding = 0
        let items = []  // kunci judul unik untuk total DTPS

        if (sintaLecturer) {
          // Filter by year range
          if (sintaLecturer.research) {
            const filteredResearch = sintaLecturer.research.filter(r => 
              this.isInYearRange(r.year)
            )
            researchCount = filteredResearch.length
            totalFunding += filteredResearch.reduce((sum, r) => sum + (r.fundingAmount || 0), 0)
            items.push(...filteredResearch.map(r => ({ key: `r|${r.title}|${r.year || ''}`, type: 'r', funding: r.fundingAmount || 0 })))
          }
          if (sintaLecturer.services) {
            const filteredServices = sintaLecturer.services.filter(s => 
              this.isInYearRange(s.year)
            )
            serviceCount = filteredServices.length
            totalFunding += filteredServices.reduce((sum, s) => sum + (s.fundingAmount || 0), 0)
            items.push(...filteredServices.map(s => ({ key: `s|${s.title}|${s.year || ''}`, type: 's', funding: s.fundingAmount || 0 })))
          }
        }

        result.push({
          name: lecturer.name,
          homebase: lecturer.homebase,
          isHomebase: lecturer.isHomebase,
          researchCount,
          items,
          serviceCount,
          totalFunding
        })
      })

      // Sort: homebase first, then by name
      return result.sort((a, b) => {
        if (a.isHomebase !== b.isHomebase) return a.isHomebase ? -1 : 1
        return a.name.localeCompare(b.name)
      })
    },

    // Dosen yang terpilih sebagai DTPS (homebase + additional)
    selectedDtps() {
      return this.allLecturersWithData.filter(l => 
        l.isHomebase || this.additionalDtps.includes(l.name)
      )
    },

    currentDtpsCount() {
      return this.selectedDtps.length
    },

    // Judul unik yang melibatkan minimal satu DTPS terpilih (judul kolaborasi dihitung sekali)
    selectedUniqueItems() {
      const map = new Map()
      this.selectedDtps.forEach(l => (l.items || []).forEach(it => map.set(it.key, it)))
      return [...map.values()]
    },

    filteredResearchCount() {
      return this.selectedUniqueItems.filter(it => it.type === 'r').length
    },

    filteredServiceCount() {
      return this.selectedUniqueItems.filter(it => it.type === 's').length
    },

    totalSelectedFunding() {
      return this.selectedUniqueItems.reduce((sum, it) => sum + it.funding, 0)
    },

    ratioResearchPerDtps() {
      if (this.currentDtpsCount === 0) return '0.00'
      return (this.filteredResearchCount / this.currentDtpsCount).toFixed(2)
    },

    ratioServicePerDtps() {
      if (this.currentDtpsCount === 0) return '0.00'
      return (this.filteredServiceCount / this.currentDtpsCount).toFixed(2)
    },

    ratioTotalPerDtps() {
      if (this.currentDtpsCount === 0) return '0.00'
      return ((this.filteredResearchCount + this.filteredServiceCount) / this.currentDtpsCount).toFixed(2)
    },

    avgFundingPerDtps() {
      if (this.currentDtpsCount === 0) return 0
      return this.totalSelectedFunding / this.currentDtpsCount
    }
  },
  methods: {
    normalizeName(name) {
      if (!name) return ''
      return name
        .toLowerCase()
        .replace(/,\s*(s\.kom|m\.kom|s\.t|m\.t|s\.si|m\.si|s\.e|m\.m|m\.acc|ak|mba|m\.sc|cpec|chcm|cdms|csca|ir\.|dr\.|prof\.|drs\.|drh\.)\.?/gi, '')
        .replace(/\s+/g, ' ')
        .trim()
    },

    isInYearRange(year) {
      if (!year || year === 'Unknown') return false
      const y = parseInt(year)
      const start = parseInt(this.startYear)
      const end = parseInt(this.endYear)
      return y >= start && y <= end
    },

    isSelected(lecturer) {
      return lecturer.isHomebase || this.additionalDtps.includes(lecturer.name)
    },

    toggleLecturer(lecturer) {
      if (lecturer.isHomebase) return // Can't toggle homebase

      const idx = this.additionalDtps.indexOf(lecturer.name)
      if (idx >= 0) {
        this.additionalDtps.splice(idx, 1)
      } else {
        this.additionalDtps.push(lecturer.name)
      }
    },

    formatCurrency(amount) {
      if (!amount) return 'Rp 0'
      return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(amount)
    },

    formatCurrencyShort(amount) {
      if (!amount) return 'Rp 0'
      if (amount >= 1000000000) {
        return `Rp ${(amount / 1000000000).toFixed(1)}M`
      } else if (amount >= 1000000) {
        return `Rp ${(amount / 1000000).toFixed(1)}jt`
      } else if (amount >= 1000) {
        return `Rp ${(amount / 1000).toFixed(0)}rb`
      }
      return this.formatCurrency(amount)
    }
  },
  watch: {
    selectedProdi() {
      // Reset additional DTPS when prodi changes
      this.additionalDtps = []
    }
  }
}
</script>
