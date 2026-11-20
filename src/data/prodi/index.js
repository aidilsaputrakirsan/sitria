// Registry prodi & jurusan FSTI.
//
// File data di src/data/prodi/<slug>/*.json dideteksi otomatis, jadi menambah prodi
// cukup dengan membuat foldernya (lecturers.json dulu, lalu hasil pipeline scraper).
// Tidak perlu lagi menambah baris import manual di sini.

const files = import.meta.glob('./*/*.json', { eager: true, import: 'default' })

// nama file -> kunci di registry (dipakai komponen)
const FILE_KEYS = {
  lecturers: 'config',
  sinta_data: 'sintaData',
  expertise_data: 'expertiseData',
  clusters_data: 'clustersData',
  pddikti_data: 'pddiktiData',
  supervision_data: 'supervisionData',
  roadmap_mapping: 'roadmapMapping',
  roadmap_mapping_itk: 'roadmapMappingItk',
  abdimas_mapping: 'abdimasMapping',
  abdimas_mapping_itk: 'abdimasMappingItk',
}

export const jurusanList = [
  { slug: 'jteib', name: 'Teknik Elektro, Informatika, dan Bisnis', short: 'JTEIB' },
  { slug: 'jsad', name: 'Sains dan Analitika Data', short: 'JSAD' },
]

const PRODI = [
  // Jurusan Teknik Elektro, Informatika, dan Bisnis
  { slug: 'sistem-informasi', name: 'Sistem Informasi', code: 'SI', jurusan: 'jteib' },
  { slug: 'bisnis-digital', name: 'Bisnis Digital', code: 'BD', jurusan: 'jteib' },
  { slug: 'teknik-elektro', name: 'Teknik Elektro', code: 'TE', jurusan: 'jteib' },
  { slug: 'informatika', name: 'Informatika', code: 'IF', jurusan: 'jteib' },
  { slug: 'teknik-biomedis', name: 'Teknik Biomedis', code: 'TB', jurusan: 'jteib' },
  { slug: 'magister-manajemen-teknologi', name: 'Magister Manajemen Teknologi', code: 'MMT', jurusan: 'jteib' },
  // Jurusan Sains dan Analitika Data
  { slug: 'fisika', name: 'Fisika', code: 'FIS', jurusan: 'jsad' },
  { slug: 'matematika', name: 'Matematika', code: 'MAT', jurusan: 'jsad' },
  { slug: 'statistika', name: 'Statistika', code: 'STAT', jurusan: 'jsad' },
  { slug: 'ilmu-aktuaria', name: 'Ilmu Aktuaria', code: 'AKT', jurusan: 'jsad' },
]

export const prodiRegistry = Object.fromEntries(PRODI.map(p => [p.slug, Object.fromEntries(Object.values(FILE_KEYS).map(k => [k, null]))]))
for (const [path, json] of Object.entries(files)) {
  const [, slug, file] = path.match(/^\.\/([^/]+)\/([^/]+)\.json$/) || []
  const key = FILE_KEYS[file]
  if (slug && key) {
    prodiRegistry[slug] ??= {}
    prodiRegistry[slug][key] = json
  }
}

/**
 * status:
 *  - 'ready'  : data SINTA sudah disinkron (tampil di semua dashboard)
 *  - 'roster' : daftar dosen + SINTA ID sudah ada, menunggu sinkron SINTA
 *  - 'empty'  : belum ada data
 */
export const prodiList = PRODI.map(p => {
  const r = prodiRegistry[p.slug]
  const status = r.sintaData ? 'ready' : r.config ? 'roster' : 'empty'
  const jurusan = jurusanList.find(j => j.slug === p.jurusan)
  return {
    ...p,
    jurusanSlug: p.jurusan,
    jurusan: jurusan.name,
    status,
    hasData: status === 'ready',
    lecturerCount: r.config?.lecturers?.length || 0,
  }
})
