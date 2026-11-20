"""
Perekam data PDDikti saat browsing MANUAL
=========================================
API PDDikti mewajibkan reCAPTCHA, jadi pengambilan otomatis tidak dipakai.
Script ini hanya membuka Chrome biasa di layar Anda; ANDA yang mencari dan membuka
halaman dosen di PDDikti (termasuk menyelesaikan captcha bila muncul). Script cukup
menyimpan respons JSON dari API PDDikti yang memang dikirim ke browser Anda.

Yang disimpan  : respons JSON api-pddikti.kemdiktisaintek.go.id (profil, riwayat studi,
                 riwayat mengajar, paten, hasil pencarian).
Yang TIDAK disimpan: cookie, sesi, token, atau halaman lain.
Lokasi         : cache/pddikti/  (folder cache/ sudah di .gitignore)

Persiapan (sekali):
  pip install playwright          # memakai Google Chrome yang sudah terpasang

Pemakaian:
  python scripts/pddikti_capture.py
  -> Chrome terbuka di https://pddikti.kemdiktisaintek.go.id
  -> Cari nama dosen / buka prodi, lalu buka halaman detail tiap dosen
     (scroll sampai riwayat mengajar tampil).
  -> Tutup jendela Chrome bila selesai.
  python scripts/pddikti_import.py   # olah hasil rekaman

Rekaman bersifat kumulatif: boleh dijalankan berkali-kali, hasil lama tidak hilang.
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import unquote, urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURE_DIR = os.path.join(BASE_DIR, 'cache', 'pddikti')
API_HOST = 'api-pddikti.kemdiktisaintek.go.id'
START_URL = 'https://pddikti.kemdiktisaintek.go.id/'

# endpoint dosen yang dibutuhkan -> nama jenis rekaman
DOSEN_ENDPOINTS = [
    (re.compile(r'^/dosen/profile/(.+)$'), 'profile'),
    (re.compile(r'^/dosen/study-history/(.+)$'), 'study-history'),
    (re.compile(r'^/dosen/teaching-history/(.+)$'), 'teaching-history'),
    (re.compile(r'^/dosen/portofolio/paten/(.+)$'), 'paten'),
]


def classify(path):
    for rx, kind in DOSEN_ENDPOINTS:
        m = rx.match(path)
        if m:
            return kind, unquote(m.group(1))
    return 'other', None


def save(url, data):
    path = urlparse(url).path
    kind, dosen_id = classify(path)
    key = dosen_id or (path + '?' + (urlparse(url).query or ''))
    name = hashlib.sha1(key.encode()).hexdigest()[:16] + '.json'
    folder = os.path.join(CAPTURE_DIR, kind)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, name), 'w', encoding='utf-8') as f:
        json.dump({'url': url, 'path': path, 'dosenId': dosen_id,
                   'capturedAt': datetime.now().isoformat(timespec='seconds'),
                   'data': data}, f, ensure_ascii=False, indent=1)
    return kind, data


def describe(kind, data):
    if kind == 'profile' and isinstance(data, dict):
        return f"profil  : {data.get('nama_dosen')} — homebase {data.get('nama_prodi')}"
    if kind == 'teaching-history' and isinstance(data, list):
        return f"mengajar: {len(data)} kelas"
    if kind in ('study-history', 'paten') and isinstance(data, list):
        return f"{kind}: {len(data)} entri"
    return None


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('Playwright belum terpasang. Jalankan: pip install playwright')

    counts = {}

    def on_response(response):
        try:
            if urlparse(response.url).hostname != API_HOST or response.status != 200:
                return
            if 'json' not in (response.headers.get('content-type') or ''):
                return
            data = response.json()
            if isinstance(data, dict) and data.get('status') == 'error':
                return
            kind, data = save(response.url, data)
            counts[kind] = counts.get(kind, 0) + 1
            msg = describe(kind, data)
            if msg:
                print('  ✓ ' + msg)
        except Exception:
            pass  # respons yang tidak bisa dibaca dilewati saja

    print('Membuka Chrome. Silakan browsing PDDikti seperti biasa; tutup jendela bila selesai.')
    print(f'Rekaman disimpan ke {CAPTURE_DIR}\n')
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=False)
        context = browser.new_context()  # profil sementara: tidak memakai/menyimpan cookie Anda
        context.on('response', on_response)
        page = context.new_page()
        page.goto(START_URL)
        try:
            while context.pages:
                context.pages[0].wait_for_event('close', timeout=0)
        except KeyboardInterrupt:
            pass
        finally:
            browser.close()

    print('\nSelesai merekam:', ', '.join(f'{k}={v}' for k, v in sorted(counts.items())) or 'tidak ada data')
    print('Lanjutkan dengan: python scripts/pddikti_import.py')


if __name__ == '__main__':
    main()
