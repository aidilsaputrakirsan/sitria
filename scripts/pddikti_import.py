"""
Olah rekaman PDDikti (dari pddikti_capture.py) menjadi data SITRIA
===================================================================

Usage:
  python scripts/pddikti_import.py                    # tulis pddikti_data.json + laporan homebase
  python scripts/pddikti_import.py --apply-homebase   # + pindahkan keanggotaan dosen di lecturers.json
                                                      #   sesuai homebase PDDikti

Output:
  src/data/prodi/<slug>/pddikti_data.json   (dipakai menu Pengajaran; skema sama seperti sebelumnya)
  docs/HOMEBASE_PDDIKTI.md                  (perbandingan homebase PDDikti vs daftar SITRIA)

Aturan:
  - Hanya dosen dengan nama_pt "Institut Teknologi Kalimantan" yang diproses.
  - Prodi ditentukan dari homebase PDDikti (profile.nama_prodi). Homebase di luar FSTI
    dilaporkan saja, tidak dimasukkan ke prodi mana pun.
  - pddikti_data.json digabung per dosen: dosen yang belum direkam ulang tetap memakai data lama.
  - --apply-homebase hanya memindahkan dosen yang profilnya terekam; dosen lain tidak disentuh.
    Setelah itu jalankan sinta_scraper.py untuk prodi yang anggotanya berubah.
"""

import glob
import importlib.util
import json
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE_DIR, 'scripts')
PRODI_DIR = os.path.join(BASE_DIR, 'src', 'data', 'prodi')
CAPTURE_DIR = os.path.join(BASE_DIR, 'cache', 'pddikti')
SINTA_CACHE = os.path.join(BASE_DIR, 'cache', 'sinta_itk_authors.json')
DOC_PATH = os.path.join(BASE_DIR, 'docs', 'HOMEBASE_PDDIKTI.md')


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, f'{name}.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


shape_dosen = _load('pddikti_scraper').shape_dosen
norm_name = _load('build_lecturers_from_fsti').norm_name

JTEIB = 'Teknik Elektro, Informatika, dan Bisnis'
JSAD = 'Sains dan Analitika Data'
# nama prodi di PDDikti -> (slug SITRIA, nama, kode, jurusan)
PRODI_MAP = {
    'sistem informasi': ('sistem-informasi', 'Sistem Informasi', 'SI', JTEIB),
    'bisnis digital': ('bisnis-digital', 'Bisnis Digital', 'BD', JTEIB),
    'teknik elektro': ('teknik-elektro', 'Teknik Elektro', 'TE', JTEIB),
    'informatika': ('informatika', 'Informatika', 'IF', JTEIB),
    'teknik biomedis': ('teknik-biomedis', 'Teknik Biomedis', 'TB', JTEIB),
    'manajemen teknologi': ('magister-manajemen-teknologi', 'Magister Manajemen Teknologi', 'MMT', JTEIB),
    'magister manajemen teknologi': ('magister-manajemen-teknologi', 'Magister Manajemen Teknologi', 'MMT', JTEIB),
    'fisika': ('fisika', 'Fisika', 'FIS', JSAD),
    'matematika': ('matematika', 'Matematika', 'MAT', JSAD),
    'statistika': ('statistika', 'Statistika', 'STAT', JSAD),
    'ilmu aktuaria': ('ilmu-aktuaria', 'Ilmu Aktuaria', 'AKT', JSAD),
}


def prodi_of(nama_prodi):
    return PRODI_MAP.get((nama_prodi or '').strip().lower())


# --------------------------------------------------------------------------- baca rekaman
def read_captures():
    """Kelompokkan rekaman per dosenId (diambil dari URL, karena id_sdm di isi respons berubah-ubah)."""
    dosen = {}
    for kind in ('profile', 'study-history', 'teaching-history', 'paten'):
        for path in glob.glob(os.path.join(CAPTURE_DIR, kind, '*.json')):
            with open(path, encoding='utf-8') as f:
                rec = json.load(f)
            d = dosen.setdefault(rec['dosenId'], {'id': rec['dosenId']})
            prev = d.get(kind)
            if not prev or rec['capturedAt'] >= prev['capturedAt']:
                d[kind] = rec
    return dosen


def load_lecturers():
    """Semua lecturers.json: slug -> data."""
    out = {}
    for path in glob.glob(os.path.join(PRODI_DIR, '*', 'lecturers.json')):
        with open(path, encoding='utf-8') as f:
            out[os.path.basename(os.path.dirname(path))] = json.load(f)
    return out


def sinta_lookup():
    if not os.path.exists(SINTA_CACHE):
        return {}
    with open(SINTA_CACHE, encoding='utf-8') as f:
        return {norm_name(a['name']): a for a in json.load(f)['authors']}


# --------------------------------------------------------------------------- proses
def build(apply_homebase=False):
    caps = read_captures()
    lecturers = load_lecturers()
    sinta = sinta_lookup()

    # indeks dosen SITRIA saat ini: nama ternormalisasi -> (slug, entri)
    current = {}
    for slug, data in lecturers.items():
        for l in data['lecturers']:
            current[norm_name(l['name'])] = (slug, l)

    rows, per_prodi, outside = [], {}, []
    for d in caps.values():
        prof = (d.get('profile') or {}).get('data') or {}
        if not prof or 'Kalimantan' not in (prof.get('nama_pt') or ''):
            continue
        name = prof.get('nama_dosen', '').strip()
        key = norm_name(name)
        target = prodi_of(prof.get('nama_prodi'))
        cur_slug, cur_entry = current.get(key, (None, None))
        shaped = shape_dosen(prof,
                             (d.get('study-history') or {}).get('data'),
                             (d.get('teaching-history') or {}).get('data'),
                             (d.get('paten') or {}).get('data'))
        row = {'name': (cur_entry or {}).get('name') or name.title(), 'pddiktiName': name,
               'pddiktiId': d['id'], 'homebase': prof.get('nama_prodi'), 'target': target,
               'currentSlug': cur_slug, 'entry': cur_entry, 'shaped': shaped,
               'hasTeaching': bool(d.get('teaching-history')), 'profile': prof}
        rows.append(row)
        if target:
            per_prodi.setdefault(target[0], []).append(row)
        else:
            outside.append(row)

    if not rows:
        sys.exit(f'Belum ada rekaman profil dosen ITK di {CAPTURE_DIR}. Jalankan pddikti_capture.py dulu.')

    write_pddikti_data(per_prodi)
    if apply_homebase:
        apply(per_prodi, lecturers, sinta)
    write_doc(rows, per_prodi, outside, lecturers, applied=apply_homebase)


def write_pddikti_data(per_prodi):
    for slug, rows in per_prodi.items():
        path = os.path.join(PRODI_DIR, slug, 'pddikti_data.json')
        old = {}
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                old = {norm_name(l['name']): l for l in json.load(f).get('lecturers', [])}
        for r in rows:
            prev = old.get(norm_name(r['name']), {})
            # rekaman tanpa riwayat mengajar tidak menimpa riwayat mengajar lama
            merged = {**prev, **{k: v for k, v in r['shaped'].items()
                                 if r['hasTeaching'] or k not in ('teachingHistory', 'teachingBySemester', 'stats')}}
            old[norm_name(r['name'])] = {'name': r['name'], 'pddiktiId': r['pddiktiId'],
                                        'fetchedAt': datetime.now().isoformat(timespec='seconds'), **merged}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        out = {'metadata': {'generatedAt': datetime.now().isoformat(timespec='seconds'),
                            'source': 'PDDikti (direkam saat browsing manual, pddikti_capture.py)',
                            'prodi': PRODI_MAP[rows[0]['homebase'].strip().lower()][1],
                            'description': 'Data publik PDDikti: profil, riwayat pendidikan, riwayat mengajar, HKI/Paten'},
               'lecturers': sorted(old.values(), key=lambda l: l['name'])}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f'  pddikti_data.json {slug}: {len(out["lecturers"])} dosen')


def apply(per_prodi, lecturers, sinta):
    """Pindahkan dosen ke lecturers.json prodi homebase PDDikti-nya."""
    moved = {r['pddiktiId'] for rows in per_prodi.values() for r in rows}
    names = {norm_name(r['name']) for rows in per_prodi.values() for r in rows}
    # 1) keluarkan dosen terekam dari prodi lama
    for slug, data in lecturers.items():
        data['lecturers'] = [l for l in data['lecturers'] if norm_name(l['name']) not in names]
    # 2) masukkan ke prodi homebase
    for slug, rows in per_prodi.items():
        _, pname, code, jur = PRODI_MAP[rows[0]['homebase'].strip().lower()]
        data = lecturers.setdefault(slug, {'name': pname, 'code': code, 'jurusan': jur, 'lecturers': []})
        for r in rows:
            e = dict(r['entry'] or {})
            if not e.get('sintaId'):
                a = sinta.get(norm_name(r['pddiktiName']))
                if a:
                    e.update({'sintaId': a['sintaId'],
                              'sintaUrl': f"https://sinta.kemdiktisaintek.go.id/authors/profile/{a['sintaId']}",
                              'scholarId': e.get('scholarId') or a.get('scholarId') or ''})
                else:
                    e['needsReview'] = True
            e.update({'name': r['name'], 'pddiktiId': r['pddiktiId'], 'homebaseSource': 'PDDikti'})
            data['lecturers'].append(e)
        data['lecturers'].sort(key=lambda l: l['name'])
    for slug, data in lecturers.items():
        path = os.path.join(PRODI_DIR, slug, 'lecturers.json')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    print(f'  homebase diterapkan untuk {len(moved)} dosen.')


def write_doc(rows, per_prodi, outside, lecturers, applied):
    L = ['# Homebase Dosen menurut PDDikti', '',
         f'_Dibuat oleh `scripts/pddikti_import.py` pada {datetime.now():%d %B %Y %H:%M}, '
         f'dari rekaman `pddikti_capture.py`._', '',
         'Homebase PDDikti adalah prodi tempat NIDN dosen tercatat dan menjadi dasar data LKPS. '
         'Kolom **Di SITRIA** menunjukkan prodi dosen di daftar SITRIA sebelum skrip ini dijalankan'
         + (' (homebase PDDikti sudah diterapkan ke `lecturers.json`).' if applied
            else '. Jalankan dengan `--apply-homebase` untuk menerapkannya.'), '']
    for slug, rs in sorted(per_prodi.items()):
        pname = PRODI_MAP[rs[0]['homebase'].strip().lower()][1]
        L += [f'## {pname}', '', '| Nama | Jabatan | Pendidikan | Status | Kelas diampu | Di SITRIA | Keterangan |',
              '|---|---|---|---|---|---|---|']
        for r in sorted(rs, key=lambda x: x['name']):
            p = r['profile']
            cur = r['currentSlug'] or '—'
            note = 'sama' if r['currentSlug'] == slug else ('**pindah homebase**' if r['currentSlug'] else '**baru di SITRIA**')
            kelas = r['shaped']['stats']['totalClassesTaught'] if r['hasTeaching'] else 'belum direkam'
            L.append(f"| {r['name']} | {p.get('jabatan_akademik') or '—'} | {p.get('pendidikan_tertinggi') or '—'} | "
                     f"{p.get('status_aktivitas') or '—'} | {kelas} | {cur} | {note} |")
        L.append('')
    if outside:
        L += ['## Homebase di luar FSTI', '']
        for r in outside:
            L.append(f"- {r['name']} — homebase PDDikti: {r['homebase']} (di SITRIA: {r['currentSlug'] or '—'})")
        L.append('')
    recorded = {norm_name(r['name']) for r in rows}
    missing = [(slug, l['name']) for slug, d in lecturers.items() for l in d['lecturers']
               if norm_name(l['name']) not in recorded]
    if missing:
        L += ['## Dosen SITRIA yang belum direkam profil PDDikti-nya', '']
        L += [f'- {n} ({s})' for s, n in sorted(missing)]
        L.append('')
    os.makedirs(os.path.dirname(DOC_PATH), exist_ok=True)
    with open(DOC_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    print(f'  laporan: {DOC_PATH}')


if __name__ == '__main__':
    build(apply_homebase='--apply-homebase' in sys.argv)
