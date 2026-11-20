<template>
  <div class="space-y-6">
    <!-- Hero pencarian: latar Aurora (Vue Bits, WebGL) -->
    <section class="relative overflow-hidden rounded-3xl bg-slate-950 text-white shadow-xl">
      <div class="absolute inset-0 opacity-80">
        <Aurora :color-stops="['#065f46', '#10b981', '#0ea5e9']" :amplitude="0.9" :blend="0.6" :speed="0.6" :height="0.5" />
      </div>
      <div class="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-slate-950/30 to-transparent"></div>

      <div class="relative z-10 max-w-3xl p-6 md:p-10">
        <h2 class="text-2xl md:text-3xl font-black tracking-tight">Cari Pakar & Pembimbing</h2>
        <p class="mt-2 text-sm md:text-base text-emerald-50/90">
          Tulis ide atau judul penelitian. Sistem mencocokkan kata kuncinya dengan riwayat karya setiap dosen.
        </p>

        <div class="mt-6 flex flex-col gap-2 rounded-2xl bg-white p-2 shadow-2xl md:flex-row">
          <textarea
            v-model="query"
            rows="2"
            placeholder="Contoh: sistem deteksi sampah otomatis berbasis IoT dan machine learning"
            class="flex-1 resize-none border-none bg-transparent p-3 text-slate-800 placeholder:text-slate-400 focus:ring-0"
            @keydown.enter.exact.prevent="findExperts"
            @input="hasSearched = false"
          ></textarea>
          <!-- Vue Bits Magnet: tombol "tertarik" ke arah kursor -->
          <Magnet :padding="60" :magnet-strength="4" wrapper-class-name="md:self-stretch" inner-class-name="h-full">
            <button
              @click="findExperts"
              :disabled="!query.trim()"
              class="flex h-full w-full items-center justify-center gap-2 rounded-xl bg-emerald-500 px-6 py-3 font-bold text-white shadow-lg shadow-emerald-500/30 transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              Cari
            </button>
          </Magnet>
        </div>

        <div class="mt-3 flex flex-wrap items-center gap-2">
          <span class="text-xs text-emerald-100/80">Coba:</span>
          <button
            v-for="ex in examples"
            :key="ex"
            @click="query = ex; findExperts()"
            class="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-medium text-white backdrop-blur transition hover:bg-white/20"
          >{{ ex }}</button>
        </div>
        <p v-if="lastTokens.length" class="mt-3 text-xs text-emerald-100/80">
          Kata kunci terbaca: <span class="font-mono font-bold text-amber-300">{{ lastTokens.join(', ') }}</span>
        </p>
      </div>
    </section>

    <!-- Hasil -->
    <section v-if="results.length" class="animate-fade-in">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="flex items-center gap-2 text-lg font-black text-slate-900">
          Rekomendasi Dosen
          <span class="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-bold text-emerald-700">{{ results.length }}</span>
        </h3>
        <button @click="clearResults" class="text-sm font-semibold text-slate-400 transition-colors hover:text-rose-500">Reset</button>
      </div>

      <div class="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
        <component
          :is="idx === 0 ? BorderGlow : 'div'"
          v-for="(result, idx) in results"
          :key="result.id || result.name"
          v-bind="idx === 0 ? topCardProps : { class: 'rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md' }"
        >
          <div class="p-5">
            <div class="mb-4 flex items-start justify-between gap-3">
              <div class="flex min-w-0 items-center gap-3">
                <div
                  class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold"
                  :class="idx === 0 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'"
                >{{ idx + 1 }}</div>
                <div class="min-w-0">
                  <h4 class="line-clamp-1 font-bold text-slate-800">
                    <!-- Vue Bits DecryptedText: nama "terdekripsi" saat kartu muncul -->
                    <DecryptedText :text="result.name" animate-on="view" sequential :speed="28" reveal-direction="start" encrypted-class-name="text-emerald-400" />
                  </h4>
                  <p v-if="result.sinta_score" class="text-xs text-slate-500">SINTA Score {{ result.sinta_score }}</p>
                </div>
              </div>
              <div class="shrink-0 text-right">
                <div class="text-2xl font-black tabular-nums text-emerald-600">{{ result.relevance }}%</div>
                <div class="text-xs font-bold text-slate-400">Relevansi</div>
              </div>
            </div>

            <div class="mb-4 h-1.5 overflow-hidden rounded-full bg-slate-100">
              <div class="h-full rounded-full bg-emerald-500 transition-all duration-700" :style="{ width: result.relevance + '%' }"></div>
            </div>

            <p class="mb-2 text-[11px] font-bold text-slate-400">Kata kunci yang cocok</p>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="keyword in result.matched_keywords"
                :key="keyword"
                class="rounded-md border border-emerald-100 bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700"
              >{{ keyword }}</span>
            </div>

            <div class="mt-4 border-t border-slate-100 pt-4">
              <p class="mb-1 text-[11px] text-slate-400">Keahlian utama</p>
              <p class="line-clamp-2 text-xs leading-relaxed text-slate-600">{{ Object.keys(result.keywords).slice(0, 5).join(', ') }}</p>
            </div>
          </div>
        </component>
      </div>
      <p class="mt-4 text-xs text-slate-400">
        Relevansi dibandingkan terhadap dosen dengan kecocokan tertinggi (= 100%), bukan skor mutlak.
      </p>
    </section>

    <div v-else-if="hasSearched" class="animate-fade-in py-16 text-center text-slate-400">
      <p class="font-semibold text-slate-500">Belum ada dosen yang cocok.</p>
      <p class="mt-1 text-sm">Coba kata kunci yang lebih spesifik, misalnya nama metode atau bidang.</p>
    </div>
  </div>
</template>

<script>
import { markRaw } from 'vue';
import { prodiRegistry, prodiList } from '../data/prodi/index.js';
import Aurora from './vue-bits/Aurora.vue';
import Magnet from './vue-bits/Magnet.vue';
import DecryptedText from './vue-bits/DecryptedText.vue';
import BorderGlow from './vue-bits/BorderGlow.vue';

// Kata umum yang tidak membedakan keahlian (agar "saya ingin membuat sistem" tidak cocok ke semua dosen)
const STOPWORDS = new Set([
  'saya', 'ingin', 'akan', 'membuat', 'buat', 'yang', 'dan', 'atau', 'untuk', 'dengan', 'pada', 'dari', 'dalam',
  'berbasis', 'menggunakan', 'penggunaan', 'sebuah', 'suatu', 'ini', 'itu', 'adalah', 'oleh', 'sebagai', 'tentang',
  'penelitian', 'riset', 'judul', 'ide', 'studi', 'kasus', 'analisis', 'sistem', 'aplikasi', 'pengembangan',
  'the', 'and', 'for', 'with', 'using', 'based', 'study', 'system',
]);

export default {
  name: 'ExpertiseFinder',
  components: { Aurora, Magnet, DecryptedText },
  data() {
    return {
      query: '',
      results: [],
      hasSearched: false,
      lastTokens: [],
      BorderGlow: markRaw(BorderGlow),
      topCardProps: {
        backgroundColor: '#ffffff',
        borderRadius: 16,
        glowRadius: 28,
        glowColor: '160 84 39',
        colors: ['#10b981', '#34d399', '#0ea5e9'],
        animated: true,
      },
      examples: ['deteksi penyakit dengan deep learning', 'e-government dan tata kelola TI', 'UMKM dan pemasaran digital'],
    };
  },
  computed: {
    profiles() {
      const all = [];
      prodiList.filter(p => p.hasData).forEach(p => {
        const data = prodiRegistry[p.slug];
        if (data?.expertiseData?.profiles) all.push(...data.expertiseData.profiles);
      });
      return all;
    }
  },
  methods: {
    findExperts() {
      if (!this.query.trim()) return;
      this.hasSearched = true;
      const words = this.tokenize(this.query);
      this.lastTokens = words;

      const ranked = this.profiles
        .map(profile => {
          let score = 0;
          const matched = [];
          words.forEach(word => {
            for (const [key, weight] of Object.entries(profile.keywords)) {
              if (key.includes(word) || word.includes(key)) {
                score += weight;
                if (!matched.includes(key)) matched.push(key);
              }
            }
          });
          return { ...profile, score, matched_keywords: matched.slice(0, 6) };
        })
        .filter(p => p.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 6);

      const top = ranked[0]?.score || 1;
      this.results = ranked.map(r => ({ ...r, relevance: Math.max(1, Math.round((r.score / top) * 100)) }));
    },
    tokenize(text) {
      return text.toLowerCase()
        .replace(/[^a-z0-9\s-]/g, ' ')
        .split(/\s+/)
        .filter(w => w.length > 2 && !STOPWORDS.has(w));
    },
    clearResults() {
      this.query = '';
      this.results = [];
      this.hasSearched = false;
      this.lastTokens = [];
    }
  }
};
</script>
