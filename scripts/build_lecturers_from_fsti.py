"""
Bangun lecturers.json per prodi dari daftar dosen resmi FSTI + SINTA ID dari SINTA.
==================================================================================

Sumber:
  1. Daftar dosen per prodi : https://fsti.itk.ac.id/profil/dosen
     (data Inertia yang tertanam di HTML; diambil: nama, link Google Scholar, keahlian.
      NIP sengaja TIDAK disimpan karena repo & situs SITRIA publik.)
  2. SINTA ID               : daftar author afiliasi ITK di SINTA
     https://sinta.kemdiktisaintek.go.id/affiliations/authors/536
     (publik, tanpa login; tiap entri memuat nama, SINTA ID, departemen, Scholar ID)

Pencocokan (urutan prioritas):
  a. Google Scholar ID sama                      -> confidence "scholar"
  b. Nama sama persis (setelah buang gelar)      -> confidence "exact"
  c. Kemiripan nama tinggi, departemen sama      -> confidence "fuzzy"   (perlu review)
  Tidak ketemu                                   -> sintaId kosong        (perlu review)

Usage:
  python scripts/build_lecturers_from_fsti.py              # jurusan JTEIB (default)
  python scripts/build_lecturers_from_fsti.py --refresh    # paksa ambil ulang data SINTA
  python scripts/build_lecturers_from_fsti.py --write      # tulis lecturers.json prodi yang BELUM punya
  python scripts/build_lecturers_from_fsti.py --write --force  # timpa yang sudah ada (hati-hati: homebase PDDikti hilang)

Tanpa --write script hanya membuat laporan docs/DATA_DOSEN_JTEIB.md + cache,
sehingga hasil bisa direview dulu. lecturers.json Sistem Informasi & Bisnis Digital
yang sudah ada TIDAK pernah ditimpa; script hanya melaporkan bila ada beda.
"""

import html
import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODI_DIR = os.path.join(BASE_DIR, 'src', 'data', 'prodi')
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
DOC_PATH = os.path.join(BASE_DIR, 'docs', 'DATA_DOSEN_JTEIB.md')

FSTI_URL = 'https://fsti.itk.ac.id/profil/dosen'
SINTA = 'https://sinta.kemdiktisaintek.go.id'
ITK_AFFIL = '536'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8',
    'Referer': f'{SINTA}/authors',
}

# Jurusan Teknik Elektro, Informatika, dan Bisnis (JTEIB)
JURUSAN = 'Teknik Elektro, Informatika, dan Bisnis'
TARGETS = [
    # slug, nama di web FSTI, nama departemen di SINTA, kode
    ('sistem-informasi', 'Sistem Informasi', 'Sistem Informasi', 'SI'),
    ('bisnis-digital', 'Bisnis Digital', 'Bisnis Digital', 'BD'),
    ('teknik-elektro', 'Teknik Elektro', 'Teknik Elektro', 'TE'),
    ('informatika', 'Informatika', 'Informatika', 'IF'),
    ('teknik-biomedis', 'Teknik Biomedis', 'Teknik Biomedis', 'TB'),
    ('magister-manajemen-teknologi', 'Magister Manajemen Teknologi', 'Manajemen Teknologi', 'MMT'),
]
EXISTING = {'sistem-informasi', 'bisnis-digital'}  # sudah punya data, jangan ditimpa
# Belum diaktifkan (lihat dokumen): TB belum punya daftar dosen di web FSTI;
# satu-satunya dosen MMT di web juga tercantum di TE sehingga akan terhitung ganda.
SKIP_WRITE = {
    'teknik-biomedis': 'belum ada daftar dosen di web FSTI',
    'magister-manajemen-teknologi': 'dosennya juga tercantum di prodi lain (hindari hitung ganda)',
}

ROSTER_INDEX = {}  # prodi -> set nama ternormalisasi (untuk deteksi dosen di >1 prodi)

session = requests.Session()
session.headers.update(HEADERS)


# --------------------------------------------------------------------------- utils
def norm_name(name):
    """Nama tanpa gelar, huruf kecil, tanpa aksen/tanda baca."""
    n = name.split(',')[0]
    n = re.sub(r'\b(prof|dr|ir|drs|dra|h|hj)\b\.?', ' ', n, flags=re.I)
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode()
    n = re.sub(r'[^a-zA-Z ]', ' ', n).lower()
    return ' '.join(n.split())


def scholar_id(url):
    m = re.search(r'[?&]user=([\w-]{12})', url or '')
    return m.group(1) if m else None


def similarity(a, b):
    A, B = norm_name(a), norm_name(b)
    ratio = SequenceMatcher(None, A, B).ratio()
    ta, tb = set(A.split()), set(B.split())
    token = len(ta & tb) / max(1, min(len(ta), len(tb)))
    return max(ratio, token * 0.95)


def initials_match(full, short):
    """'Riska Kurniyanto Abdullah' cocok dengan 'RISKA K ABDULLAH' / 'PRASIS DAMAI NH'."""
    F, S = norm_name(full).split(), norm_name(short).split()
    if not F or not S or F[0] != S[0]:
        return False
    rest = ''.join(w[0] for w in F[1:])
    tail = ''.join(w if len(w) <= 3 else w[0] for w in S[1:])
    # setiap token ringkas harus berupa kata utuh yang ada, atau inisial berurutan
    return all(w in F or (len(w) <= 3 and w in rest) for w in S[1:]) or tail == rest


def get(url, tries=3):
    for i in range(tries):
        r = session.get(url, timeout=30)
        if r.status_code == 200:
            return r.text
        time.sleep(2 * (i + 1))
    raise RuntimeError(f'Gagal GET {url} ({r.status_code})')


# --------------------------------------------------------------------------- sumber 1: FSTI
def fetch_fsti_roster():
    page = get(FSTI_URL)
    m = re.search(r'data-page="([^"]+)"', page)
    if not m:
        raise RuntimeError('Data Inertia tidak ditemukan di halaman FSTI (struktur web berubah?)')
    props = json.loads(html.unescape(m.group(1)))['props']
    roster = {}
    for prodi, items in props['groupedLecturers'].items():
        roster[prodi] = []
        for it in items:
            if not it.get('is_active', True):
                continue
            links = it.get('academic_profiles') or []
            scholar = next((u for u in links if 'scholar.google' in u), None)
            sinta = next((u for u in links if 'sinta' in u), None)
            sid = re.search(r'profile/(\d+)', sinta or '')
            roster[prodi].append({
                'name': it['name'].strip(),
                'scholarUrl': scholar,
                'scholarId': scholar_id(scholar),
                'sintaIdFromFsti': sid.group(1) if sid else None,
                'functional_position': it.get('functional_position'),
                'expertise': it.get('expertise'),
            })
    return roster


# --------------------------------------------------------------------------- sumber 2: SINTA
def parse_author_page(text):
    """Pecah halaman daftar author SINTA per entri (dibatasi oleh foto avatar)."""
    out = []
    for blk in re.split(r'<div class="col-lg-2">', text)[1:]:
        m = re.search(r'authors/profile/(\d+)">([^<]+)</a>', blk)
        if not m:
            continue
        gs = re.search(r'citations\?view_op=view_photo&(?:amp;)?user=([\w-]{12})', blk)
        dept = re.search(r'profile-dept">\s*<a[^>]*>(?:\s*<i[^>]*></i>)?\s*([^<]+)</a>', blk)
        out.append((gs.group(1) if gs else '', m.group(1), m.group(2), dept.group(1) if dept else ''))
    return out


def fetch_sinta_itk_authors(refresh=False):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache = os.path.join(CACHE_DIR, 'sinta_itk_authors.json')
    if not refresh and os.path.exists(cache):
        with open(cache, encoding='utf-8') as f:
            data = json.load(f)
        print(f'  pakai cache SINTA ({len(data["authors"])} author, {data["fetchedAt"]})')
        return data['authors']

    authors, page = {}, 1
    while True:
        text = get(f'{SINTA}/affiliations/authors/{ITK_AFFIL}?page={page}')
        found = parse_author_page(text)
        before = len(authors)
        for gs, sid, name, dept in found:
            dept = re.sub(r'\s*\((S1|S2|S3|D3|D4)\)\s*$', '', ' '.join(dept.split()))
            authors[sid] = {'sintaId': sid, 'name': ' '.join(name.split()), 'dept': dept,
                            'scholarId': gs.strip() or None}
        print(f'  SINTA halaman {page}: total {len(authors)} author')
        if not found or len(authors) == before:  # halaman kosong / mengulang -> selesai
            break
        page += 1
        time.sleep(1.2)  # sopan ke server SINTA
    with open(cache, 'w', encoding='utf-8') as f:
        json.dump({'fetchedAt': datetime.now().isoformat(timespec='seconds'),
                   'authors': list(authors.values())}, f, ensure_ascii=False, indent=1)
    return list(authors.values())


# --------------------------------------------------------------------------- pencocokan
def match(person, sinta_authors, dept):
    by_gs = {a['scholarId']: a for a in sinta_authors if a.get('scholarId')}
    if person.get('sintaIdFromFsti'):
        a = next((x for x in sinta_authors if x['sintaId'] == person['sintaIdFromFsti']), None)
        if a:
            return a, 'fsti-link', 1.0
    if person.get('scholarId') and person['scholarId'] in by_gs:
        return by_gs[person['scholarId']], 'scholar', 1.0

    best, best_s = None, 0
    for a in sinta_authors:
        s = similarity(person['name'], a['name'])
        if a['dept'] == dept:
            s += 0.05  # utamakan departemen yang sama
        if s > best_s:
            best, best_s = a, s
    if best and norm_name(best['name']) == norm_name(person['name']):
        return best, 'exact', 1.0
    if best and best_s >= 0.85:
        return best, 'fuzzy', round(min(best_s, 1.0), 2)
    # nama disingkat di SINTA, hanya dalam departemen yang sama
    same = [a for a in sinta_authors if a['dept'] == dept and initials_match(person['name'], a['name'])]
    if len(same) == 1:
        return same[0], 'initials', 0.9
    return None, 'none', round(best_s, 2)


def build(refresh=False, write=False):
    print('1) Ambil daftar dosen dari web FSTI...')
    roster = fetch_fsti_roster()
    ROSTER_INDEX.update({p: {norm_name(x['name']) for x in xs} for p, xs in roster.items()})
    print('2) Ambil daftar author ITK dari SINTA...')
    sinta = fetch_sinta_itk_authors(refresh)

    results = []
    for slug, fsti_name, dept, code in TARGETS:
        people = roster.get(fsti_name, [])
        rows, used = [], set()
        for p in people:
            a, how, score = match(p, sinta, dept)
            if a:
                used.add(a['sintaId'])
            rows.append({**p, 'sinta': a, 'how': how, 'score': score,
                         'deptMismatch': bool(a and a['dept'] != dept)})
        # Author SINTA di departemen ini yang tidak ada di web FSTI
        extra = [a for a in sinta if a['dept'] == dept and a['sintaId'] not in used]
        results.append({'slug': slug, 'prodi': fsti_name, 'dept': dept, 'code': code,
                        'rows': rows, 'extra': extra})

    write_doc(results)
    if write:
        write_lecturers(results)
    return results


# --------------------------------------------------------------------------- output
def lecturer_entry(r):
    a = r['sinta']
    sid = a['sintaId'] if a else ''
    gs = r['scholarId'] or (a or {}).get('scholarId') or ''
    return {
        'name': r['name'],
        'scholarId': gs,
        'scholarUrl': r['scholarUrl'] or (f'https://scholar.google.com/citations?user={gs}' if gs else ''),
        'sintaId': sid,
        'sintaUrl': f'{SINTA}/authors/profile/{sid}' if sid else '',
        **({'needsReview': True} if r['how'] in REVIEW else {}),
    }


def write_lecturers(results):
    for res in results:
        path = os.path.join(PRODI_DIR, res['slug'], 'lecturers.json')
        if res['slug'] in EXISTING or (os.path.exists(path) and not FORCE):
            # jangan timpa daftar yang sudah ada (bisa sudah disesuaikan homebase PDDikti)
            print(f'  lewati {res["slug"]} (lecturers.json sudah ada; pakai --force untuk menimpa)')
            continue
        if res['slug'] in SKIP_WRITE:
            print(f'  lewati {res["slug"]} ({SKIP_WRITE[res["slug"]]})')
            continue
        path = os.path.join(PRODI_DIR, res['slug'], 'lecturers.json')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {'name': res['prodi'], 'code': res['code'], 'jurusan': JURUSAN,
                'source': 'fsti.itk.ac.id/profil/dosen + SINTA (afiliasi ITK)',
                'generatedAt': datetime.now().isoformat(timespec='seconds'),
                'lecturers': [lecturer_entry(r) for r in res['rows']]}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'  tulis {path} ({len(data["lecturers"])} dosen)')


def existing_ids(slug):
    path = os.path.join(PRODI_DIR, slug, 'lecturers.json')
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        return {norm_name(l['name']): l.get('sintaId') for l in json.load(f)['lecturers']}


HOW_LABEL = {'fsti-link': 'link SINTA di web FSTI', 'scholar': 'Scholar ID sama',
             'exact': 'nama sama', 'initials': 'nama disingkat di SINTA', 'fuzzy': 'nama mirip',
             'none': 'tidak ditemukan'}
REVIEW = ('initials', 'fuzzy', 'none')  # perlu dicek manual


def write_doc(results):
    today = datetime.now().strftime('%d %B %Y')
    L = [
        '# Data Dosen Jurusan Teknik Elektro, Informatika, dan Bisnis (JTEIB)',
        '',
        f'_Dibuat otomatis oleh `scripts/build_lecturers_from_fsti.py` pada {today}._',
        '',
        '## Sumber dan cara pencocokan',
        '',
        f'- **Daftar dosen per prodi:** [{FSTI_URL}]({FSTI_URL}) (web resmi FSTI).',
        f'- **SINTA ID:** daftar author afiliasi ITK di SINTA ({SINTA}/affiliations/authors/{ITK_AFFIL}).',
        '- Pencocokan, dari yang paling kuat: link SINTA di web FSTI → Google Scholar ID sama → nama sama persis → nama mirip (wajib dicek).',
        '- Kolom **Status**: ✅ SINTA ID terverifikasi otomatis · ⚠️ perlu dicek manual.',
        '- Kolom **Catatan** “homebase SINTA” berarti departemen dosen di SINTA berbeda dengan prodinya di web FSTI. SINTA ID tetap benar; yang berbeda hanya pencatatan homebase.',
        '- NIP tidak dicatat karena repo dan situs SITRIA bersifat publik.',
        '',
        '## Ringkasan',
        '',
        '| Prodi | Dosen (web FSTI) | SINTA ID ditemukan | Perlu dicek | Author SINTA di luar daftar FSTI |',
        '|---|---|---|---|---|',
    ]
    for res in results:
        ok = sum(1 for r in res['rows'] if r['sinta'])
        old = existing_ids(res['slug']) if res['slug'] in EXISTING else {}
        rev = sum(1 for r in res['rows'] if r['how'] in REVIEW
                  and not (r['sinta'] and old.get(norm_name(r['name'])) == r['sinta']['sintaId']))
        L.append(f"| {res['prodi']} | {len(res['rows'])} | {ok} | {rev} | {len(res['extra'])} |")

    for res in results:
        L += ['', f"## {res['prodi']} ({res['code']})", '']
        old = existing_ids(res['slug']) if res['slug'] in EXISTING else {}
        if res['slug'] in SKIP_WRITE:
            L.append(f"> **Belum diaktifkan di SITRIA:** {SKIP_WRITE[res['slug']]}. "
                     'Perlu keputusan koorprodi/jurusan dosen mana yang dihitung sebagai homebase prodi ini.')
            L.append('')
        if not res['rows']:
            L.append('_Belum ada dosen yang tercantum di web FSTI untuk prodi ini._')
        else:
            L += ['| No | Nama | SINTA ID | Departemen di SINTA | Google Scholar | Dasar pencocokan | Status | Catatan |',
                  '|---|---|---|---|---|---|---|---|']
            for i, r in enumerate(res['rows'], 1):
                a = r['sinta']
                sid = f"[{a['sintaId']}]({SINTA}/authors/profile/{a['sintaId']})" if a else '—'
                gs = r['scholarId'] or (a or {}).get('scholarId')
                gs_md = f'[{gs}](https://scholar.google.com/citations?user={gs})' if gs else '—'
                how = HOW_LABEL[r['how']] + (f" ({r['score']})" if r['how'] in ('fuzzy', 'none') else '')
                if a and r['how'] in ('fuzzy', 'initials'):
                    how += f" → SINTA: “{a['name']}”"
                flag = '⚠️' if r['how'] in REVIEW else '✅'
                notes = []
                if r['deptMismatch']:
                    notes.append(f"homebase SINTA: {a['dept']}")
                others = [p for p, names in ROSTER_INDEX.items() if p != res['prodi'] and norm_name(r['name']) in names]
                if others:
                    notes.append('juga tercantum di ' + ', '.join(others) + ' (web FSTI)')
                if old:
                    prev = old.get(norm_name(r['name']))
                    if prev and a and prev != a['sintaId']:
                        flag = '⚠️'
                        notes.append(f'beda dengan data SITRIA lama ({prev})')
                    elif prev and a and r['how'] in REVIEW:
                        flag = '✅'
                        notes.append('dikonfirmasi data SITRIA lama')
                L.append(f"| {i} | {r['name']} | {sid} | {(a or {}).get('dept', '—')} | {gs_md} | {how} | {flag} | {'; '.join(notes)} |")
        if res['extra']:
            L += ['', f"**Terdaftar di departemen {res['dept']} pada SINTA tetapi tidak ada di web FSTI** "
                      '(bisa dosen baru, sudah pindah, atau salah departemen di SINTA):', '']
            for a in res['extra']:
                L.append(f"- {a['name']} — [{a['sintaId']}]({SINTA}/authors/profile/{a['sintaId']})")

    L += ['', '## Cara memperbarui', '', '```bash',
          'python scripts/build_lecturers_from_fsti.py --refresh   # ambil ulang & perbarui dokumen ini',
          'python scripts/build_lecturers_from_fsti.py --write     # tulis lecturers.json prodi baru',
          'python scripts/sinta_scraper.py teknik-elektro          # lalu pipeline biasa per prodi',
          '```', '']
    os.makedirs(os.path.dirname(DOC_PATH), exist_ok=True)
    with open(DOC_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    print(f'3) Laporan ditulis ke {DOC_PATH}')


FORCE = '--force' in sys.argv

if __name__ == '__main__':
    build(refresh='--refresh' in sys.argv, write='--write' in sys.argv)
