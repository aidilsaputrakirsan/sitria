<template>
  <div class="space-y-6">
    <PageHeader
      title="Ringkasan Tridarma FSTI"
      :meta="headerMeta"
      interactive
    >
      <template #description>
        Satu tempat untuk memantau
<!-- Root RotatingText ber-display:flex, jadi dibungkus inline-flex agar tetap satu baris dengan kalimat -->
        <span class="inline-flex align-bottom">
          <RotatingText
            :texts="['penelitian', 'pengabdian', 'pengajaran', 'pendanaan']"
            highlight
            highlight-color="#dbeafe"
            main-class-name="font-bold text-blue-700"
            split-level-class-name="overflow-hidden"
            :stagger-duration="0.02"
            stagger-from="last"
            :rotation-interval="2400"
          />
        </span>
        dosen, langsung dari data resmi.
      </template>
      <template #actions>
        <div class="flex flex-col items-start gap-2 md:items-end">
          <!-- Tingkat 1: jurusan -->
          <div class="inline-flex flex-wrap gap-1 rounded-2xl border border-slate-200 bg-white/90 p-1 shadow-sm backdrop-blur">
            <button
              v-for="opt in jurusanOptions"
              :key="opt.slug"
              @click="selectJurusan(opt.slug)"
              :title="opt.title"
              class="rounded-xl px-3.5 py-2 text-sm font-semibold transition-all"
              :class="selectedJurusan === opt.slug ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'"
            >{{ opt.label }}</button>
          </div>
          <!-- Tingkat 2: prodi di jurusan terpilih (hanya yang datanya sudah lengkap) -->
          <div v-if="prodiOptions.length > 1" class="inline-flex flex-wrap gap-1">
            <button
              v-for="opt in prodiOptions"
              :key="opt.slug"
              @click="selectedProdi = opt.slug"
              class="rounded-lg px-2.5 py-1 text-xs font-semibold transition-colors"
              :class="selectedProdi === opt.slug ? 'bg-slate-900 text-white' : 'bg-white/80 text-slate-500 hover:text-slate-900'"
            >{{ opt.label }}</button>
          </div>
        </div>
      </template>
    </PageHeader>

    <div v-if="!slugs.length" class="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
      <p class="font-semibold text-slate-700">Data SINTA untuk {{ scopeName }} belum disinkron.</p>
      <p class="mt-1 text-sm text-slate-500">Lihat status tiap prodi pada bagian Cakupan Data di bawah.</p>
    </div>

    <!-- KPI utama: setiap angka hanya muncul sekali di halaman ini -->
    <FadeContent v-if="slugs.length" :stagger="0.08" :duration="0.6" class-name="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <KpiCard
        v-for="kpi in kpis"
        :key="kpi.key"
        :label="kpi.label"
        :value="kpi.value"
        :kind="kpi.kind"
        :hint="kpi.hint"
        :icon="kpi.icon"
        :accent="kpi.accent"
      />
    </FadeContent>

    <!-- Per darma: metrik pendalaman yang tidak diulang dari KPI di atas -->
    <section v-if="slugs.length">
      <div class="mb-4 flex items-end justify-between gap-3">
        <h2 class="text-lg font-black text-slate-900">Per Darma</h2>
        <p class="text-xs text-slate-400">Klik kartu untuk membuka detail</p>
      </div>
      <FadeContent :stagger="0.1" :duration="0.6" :delay="0.1" class-name="grid grid-cols-1 gap-4 md:grid-cols-3">
        <router-link v-for="card in tridarmaCards" :key="card.key" :to="card.to" class="group block h-full">
          <SpotlightCard theme="light" :spotlight-color="card.accent" :intensity="0.1" class-name="h-full !p-6 !rounded-2xl">
            <div class="mb-5 flex items-center gap-3">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-xl transition-transform group-hover:scale-105"
                :style="{ backgroundColor: card.accent + '14', color: card.accent }"
              >
                <component :is="card.icon" class="h-5 w-5" />
              </div>
              <div>
                <h3 class="text-base font-bold text-slate-800">{{ card.title }}</h3>
                <p class="text-[11px] text-slate-400">{{ card.source }}</p>
              </div>
            </div>
            <dl v-if="card.metrics.length" class="space-y-2.5">
              <div v-for="m in card.metrics" :key="m.label" class="flex items-center justify-between gap-3">
                <dt class="text-xs text-slate-500">{{ m.label }}</dt>
                <dd class="text-sm font-bold tabular-nums text-slate-800">{{ m.value }}</dd>
              </div>
            </dl>
            <p v-else class="text-xs text-slate-400">Belum ada data untuk prodi ini.</p>
            <div class="mt-5 flex items-center border-t border-slate-100 pt-4 text-xs font-bold text-slate-500 transition-colors group-hover:text-blue-600">
              Lihat detail
              <svg class="ml-1 h-3.5 w-3.5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </SpotlightCard>
        </router-link>
      </FadeContent>
    </section>

    <!-- Cakupan data per jurusan -->
    <section>
      <div class="mb-4 flex items-end justify-between gap-3">
        <h2 class="text-lg font-black text-slate-900">Cakupan Data per Jurusan</h2>
        <p class="text-xs text-slate-400">{{ readyCount }} dari {{ prodiList.length }} prodi FSTI sudah tersinkron</p>
      </div>
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div
          v-for="j in coverage"
          :key="j.slug"
          class="rounded-2xl border bg-white p-5 transition-colors"
          :class="selectedJurusan === j.slug ? 'border-blue-300' : 'border-slate-200'"
        >
          <div class="mb-3 flex items-start justify-between gap-3">
            <div>
              <h3 class="font-bold text-slate-800">{{ j.name }}</h3>
              <p class="text-xs text-slate-500">{{ j.short }} · {{ j.prodi.length }} prodi · {{ j.lecturers }} dosen terdata</p>
            </div>
            <button
              @click="selectJurusan(j.slug)"
              class="shrink-0 rounded-lg px-2.5 py-1 text-xs font-semibold text-blue-600 hover:bg-blue-50"
            >Lihat</button>
          </div>
          <ul class="divide-y divide-slate-100">
            <li v-for="p in j.prodi" :key="p.slug" class="flex items-center justify-between gap-3 py-2">
              <button
                class="min-w-0 truncate text-left text-sm"
                :class="p.hasData ? 'font-medium text-slate-700 hover:text-blue-700' : 'cursor-default text-slate-500'"
                @click="p.hasData && selectProdi(p)"
              >{{ p.name }}</button>
              <span class="flex shrink-0 items-center gap-2 text-xs">
                <span v-if="p.lecturerCount" class="tabular-nums text-slate-400">{{ p.lecturerCount }} dosen</span>
                <span class="rounded-md px-2 py-0.5 font-semibold" :class="STATUS[p.status].cls">{{ STATUS[p.status].label }}</span>
              </span>
            </li>
          </ul>
        </div>
      </div>
      <p class="mt-3 text-xs text-slate-400">
        Daftar dosen mengikuti web FSTI, SINTA ID dicocokkan otomatis. Rincian ada di <code>docs/DATA_DOSEN_JTEIB.md</code>.
      </p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { prodiRegistry, prodiList, jurusanList } from '../data/prodi/index.js'
import { formatNumber, formatCurrencyShort, relativeTime, latestGeneratedAt } from '../utils/format.js'
import PageHeader from '../components/ui/PageHeader.vue'
import KpiCard from '../components/ui/KpiCard.vue'
import SpotlightCard from '../components/vue-bits/SpotlightCard.vue'
import FadeContent from '../components/vue-bits/FadeContent.vue'
import RotatingText from '../components/vue-bits/RotatingText.vue'

// === Cakupan: jurusan -> prodi ===
const selectedJurusan = ref('all')
const selectedProdi = ref('all')

const jurusanOptions = [
  { slug: 'all', label: 'Semua FSTI', title: 'Fakultas Sains dan Teknologi Informasi' },
  ...jurusanList.map(j => ({ slug: j.slug, label: j.short, title: `Jurusan ${j.name}` })),
]
const readyInJurusan = computed(() =>
  prodiList.filter(p => p.hasData && (selectedJurusan.value === 'all' || p.jurusanSlug === selectedJurusan.value)))
const prodiOptions = computed(() => [
  { slug: 'all', label: selectedJurusan.value === 'all' ? 'Semua prodi' : 'Semua prodi jurusan' },
  ...readyInJurusan.value.map(p => ({ slug: p.slug, label: p.code })),
])
const slugs = computed(() => (selectedProdi.value === 'all' ? readyInJurusan.value.map(p => p.slug) : [selectedProdi.value]))

function selectJurusan(slug) {
  selectedJurusan.value = slug
  selectedProdi.value = 'all'
}
function selectProdi(p) {
  selectedJurusan.value = p.jurusanSlug
  selectedProdi.value = p.slug
}

const scopeName = computed(() => {
  if (selectedProdi.value !== 'all') return prodiList.find(p => p.slug === selectedProdi.value)?.name
  if (selectedJurusan.value === 'all') return 'FSTI'
  return `Jurusan ${jurusanList.find(j => j.slug === selectedJurusan.value)?.name}`
})

const STATUS = {
  ready: { label: 'Tersinkron', cls: 'bg-emerald-50 text-emerald-700' },
  roster: { label: 'Menunggu sinkron SINTA', cls: 'bg-amber-50 text-amber-700' },
  empty: { label: 'Belum ada data', cls: 'bg-slate-100 text-slate-500' },
}
const readyCount = prodiList.filter(p => p.hasData).length
const coverage = jurusanList.map(j => {
  const prodi = prodiList.filter(p => p.jurusanSlug === j.slug)
  return { ...j, prodi, lecturers: prodi.reduce((n, p) => n + p.lecturerCount, 0) }
})

// === Agregasi ===
const agg = computed(() => {
  const a = {
    dosen: 0, research: 0, service: 0, researchFunding: 0, serviceFunding: 0,
    articles: 0, citations: 0, scopus: 0, scopusTop: 0, sinta: 0, sintaTop: 0, ipr: 0,
    activeServiceLecturers: 0,
    pddiktiLecturers: 0, classes: 0, supervisionRoles: 0, thesesAsMain: 0, hasTeaching: false,
  }
  const seen = { research: new Map(), service: new Map() }
  slugs.value.forEach(slug => {
    const d = prodiRegistry[slug]
    if (!d?.sintaData) return
    const s = d.sintaData.prodiSummary || {}
    a.dosen += s.lecturerCount || 0
    ;(d.sintaData.lecturers || []).forEach(l => {
      // Judul unik lintas prodi (judul|tahun), sama dengan cara hitung menu Pendanaan,
      // agar judul kolaborasi antarprodi tidak terhitung dua kali.
      ;(l.research || []).forEach(r => { if (r.title) seen.research.set(`${r.title}|${r.year || ''}`, r.fundingAmount || 0) })
      ;(l.services || []).forEach(r => { if (r.title) seen.service.set(`${r.title}|${r.year || ''}`, r.fundingAmount || 0) })
      a.articles += l.stats?.googleArticles || l.stats?.articles || 0
      a.citations += l.stats?.googleCitations || 0
      const sc = l.documents?.scopus || {}
      const si = l.documents?.sinta || {}
      a.scopus += sc.total || 0
      a.scopusTop += (sc.q1 || 0) + (sc.q2 || 0)
      a.sinta += si.total || 0
      a.sintaTop += (si.s1 || 0) + (si.s2 || 0)
      a.ipr += l.ipr?.total || 0
      if ((l.servicesTotal || l.services?.length || 0) > 0) a.activeServiceLecturers++
    })
    if (d.pddiktiData) {
      a.hasTeaching = true
      a.pddiktiLecturers += d.pddiktiData.lecturers?.length || 0
      d.pddiktiData.lecturers.forEach(l => { a.classes += l.stats?.totalClassesTaught || 0 })
    }
    ;(d.supervisionData?.lecturers || []).forEach(l => {
      a.supervisionRoles += l.totalSupervised || 0
      a.thesesAsMain += l.byRole?.['Pembimbing 1'] || 0
    })
  })
  const sum = (m) => [...m.values()].reduce((x, y) => x + y, 0)
  a.research = seen.research.size
  a.service = seen.service.size
  a.researchFunding = sum(seen.research)
  a.serviceFunding = sum(seen.service)
  return a
})

const headerMeta = computed(() => {
  if (!slugs.value.length) return `${scopeName.value} · belum ada prodi tersinkron`
  const scope = selectedProdi.value === 'all' ? `${scopeName.value} (${slugs.value.length} prodi tersinkron)` : scopeName.value
  return `${formatNumber(agg.value.dosen)} dosen · ${scope} · SINTA diperbarui ${relativeTime(latestGeneratedAt('sintaData'))}`
})

// === Ikon ===
const icon = (d) => ({ template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="${d}" /></svg>` })
const PubIcon = icon('M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253')
const ResearchIcon = icon('M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z')
const ServiceIcon = icon('M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z')
const FundIcon = icon('M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z')
const TeachIcon = icon('M12 14l9-5-9-5-9 5 9 5z M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z')

// === KPI ===
const kpis = computed(() => [
  { key: 'pub', label: 'Publikasi', value: agg.value.articles, icon: PubIcon, accent: '#4f46e5', hint: `${formatNumber(agg.value.citations)} sitasi (Google Scholar)` },
  { key: 'res', label: 'Penelitian', value: agg.value.research, icon: ResearchIcon, accent: '#2563eb', hint: 'Judul unik tercatat di SINTA' },
  { key: 'pkm', label: 'Pengabdian', value: agg.value.service, icon: ServiceIcon, accent: '#059669', hint: 'Kegiatan PkM tercatat di SINTA' },
  { key: 'fund', label: 'Total Pendanaan', value: agg.value.researchFunding + agg.value.serviceFunding, kind: 'currency', icon: FundIcon, accent: '#d97706', hint: 'Hibah penelitian + pengabdian' },
])

// === Kartu per darma ===
const pct = (part, total) => (total ? `${Math.round((part / total) * 100)}%` : '0%')
const tridarmaCards = computed(() => {
  const a = agg.value
  return [
    {
      key: 'pengajaran', title: 'Pengajaran', to: '/pengajaran', icon: TeachIcon, accent: '#0891b2', source: 'PDDikti & Repository ITK',
      metrics: a.hasTeaching ? [
        { label: 'Dosen terdata PDDikti', value: formatNumber(a.pddiktiLecturers) },
        { label: 'Kelas diampu (kumulatif)', value: formatNumber(a.classes) },
        { label: 'TA sebagai Pembimbing 1', value: formatNumber(a.thesesAsMain) },
      ] : [],
    },
    {
      key: 'penelitian', title: 'Penelitian', to: '/penelitian', icon: ResearchIcon, accent: '#2563eb', source: 'SINTA',
      metrics: [
        { label: 'Artikel Scopus (Q1–Q2)', value: `${formatNumber(a.scopus)} (${formatNumber(a.scopusTop)})` },
        { label: 'Artikel SINTA (S1–S2)', value: `${formatNumber(a.sinta)} (${formatNumber(a.sintaTop)})` },
        { label: 'HKI terdaftar', value: formatNumber(a.ipr) },
        { label: 'Dana penelitian', value: formatCurrencyShort(a.researchFunding) },
      ],
    },
    {
      key: 'pengabdian', title: 'Pengabdian', to: '/pengabdian', icon: ServiceIcon, accent: '#059669', source: 'SINTA',
      metrics: [
        { label: 'Dosen aktif PkM', value: `${formatNumber(a.activeServiceLecturers)} dari ${formatNumber(a.dosen)} (${pct(a.activeServiceLecturers, a.dosen)})` },
        { label: 'Rata-rata PkM per dosen', value: a.dosen ? (a.service / a.dosen).toLocaleString('id-ID', { maximumFractionDigits: 1 }) : '0' },
        { label: 'Dana pengabdian', value: formatCurrencyShort(a.serviceFunding) },
      ],
    },
  ]
})
</script>
