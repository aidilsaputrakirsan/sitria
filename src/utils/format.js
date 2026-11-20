// Helper format & metadata yang dipakai bersama oleh banyak halaman.
import { prodiRegistry, prodiList } from '../data/prodi/index.js'

export const formatNumber = (n) => new Intl.NumberFormat('id-ID').format(Math.round(n || 0))

export const formatCurrencyShort = (n) => {
  const v = n || 0
  if (v >= 1e9) return `Rp ${(v / 1e9).toLocaleString('id-ID', { maximumFractionDigits: 2 })} M`
  if (v >= 1e6) return `Rp ${(v / 1e6).toLocaleString('id-ID', { maximumFractionDigits: 1 })} Jt`
  return `Rp ${formatNumber(v)}`
}

export function relativeTime(iso) {
  if (!iso) return 'beberapa waktu lalu'
  const days = Math.floor((Date.now() - new Date(iso).getTime()) / 86400000)
  if (days < 1) return 'hari ini'
  if (days < 30) return `${days} hari lalu`
  const months = Math.floor(days / 30)
  if (months < 12) return `${months} bulan lalu`
  return `${Math.floor(months / 12)} tahun lalu`
}

/** Tanggal sinkron terbaru dari satu jenis data (`sintaData`, `pddiktiData`, ...) lintas prodi. */
export function latestGeneratedAt(key = 'sintaData') {
  let latest = null
  prodiList.forEach(p => {
    const iso = prodiRegistry[p.slug]?.[key]?.metadata?.generatedAt
    if (iso && (!latest || iso > latest)) latest = iso
  })
  return latest
}

/** Teks meta standar untuk PageHeader, contoh: "SINTA · diperbarui 3 bulan lalu". */
export function syncLabel(source = 'SINTA', key = 'sintaData') {
  return `${source} · diperbarui ${relativeTime(latestGeneratedAt(key))}`
}
