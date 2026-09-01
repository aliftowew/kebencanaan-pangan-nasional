# CLAUDE.md

Konteks proyek untuk Claude Code. Baca ini dulu sebelum mengubah apa pun.

## Apa proyek ini

Peta interaktif (Leaflet, satu file HTML mandiri) yang memplot ~27 ribu dapur MBG (SPPG, di bawah Badan Gizi Nasional) dan jaringan Perum BULOG di Indonesia, untuk perencanaan respons pangan bencana. Pemilik: Alif Towew (Tenaga Ahli Kemenko Pangan RI). Tujuan kebijakan: saat bencana, mobilisasi SPPG dan gudang BULOG di sekitar lokasi, bukan kirim dari pusat.

Bahasa antarmuka dan dokumentasi: Bahasa Indonesia. Kode dan nama variabel boleh Inggris.

## Struktur

- `index.html` adalah file hasil build. Jangan edit langsung; edit `scripts/map_template.html` lalu jalankan `python scripts/02_build_map.py`.
- Template memakai placeholder `__SPPG__`, `__KANWIL__`, `__GUDANG__`, `__PROV__` yang diisi oleh `02_build_map.py`.
- Data SPPG dibangun oleh `scripts/01_match_kecamatan.py` dari sumber mentah di `data/raw/` (di-gitignore, diunduh otomatis).
- Pustaka front-end dari cdnjs: Leaflet 1.9.4 dan Leaflet.markercluster 1.5.3. Tidak ada bundler, tidak ada npm di runtime.

## Prinsip data yang tidak boleh dilanggar

1. Jangan pernah mengarang koordinat. Setiap titik harus punya sumber yang bisa ditelusuri; kolom `presisi` (`kecamatan`, `kabkota`, atau `alamat`) wajib jujur.
2. Titik SPPG saat ini adalah centroid kecamatan, bukan alamat. Jangan menghilangkan peringatan presisi di UI atau README.
3. Data resmi BGN/BULOG mengalahkan data komunitas. Kalau ada ekspor resmi, ganti sumbernya, catat tanggalnya, dan perbarui angka di README.
4. Angka rekap (29.991 SPPG per 8 Jun 2026; 341 SPPG dapur darurat Sumatra; 71 SPPG gempa NTT) punya sumber di README; jangan ubah tanpa sumber baru.
5. Jangan menyimpan atau mengekspor hasil Google Places/Maps ke dataset (melanggar ToS). Gunakan OSM/Nominatim, data resmi, atau input manual.

## Perintah

```bash
pip install -r scripts/requirements.txt
python scripts/01_match_kecamatan.py   # ~1 menit, unduh ~20 MB
python scripts/02_build_map.py         # ~5 detik
python -m http.server 8000             # buka http://localhost:8000/index.html
```

Uji cepat setelah mengubah template: buka index.html, pastikan angka SPPG di header muncul, klik peta di sekitar Bandung dengan radius 25 km, hasil harus ~1.000 SPPG.

## Backlog, urut prioritas

1. **Gudang BULOG.** Saat data resmi masuk (nama, lat, lon, kapasitas_ton, kanwil, kancab): isi `data/bulog_gudang.csv`, jalankan build. Tambahkan kolom stok bila tersedia dan tampilkan di popup serta ringkasan simulasi.
2. **GitHub Pages.** Pastikan `index.html` di root dan Pages aktif dari branch `main`.
3. **Koordinat resmi BGN.** Bila ekspor BGN memuat lat/lon, buat `scripts/00_import_bgn_export.py` yang menghasilkan CSV dengan skema sama (`presisi = alamat`) dan lewati `01_match_kecamatan.py`.
4. **Lapisan risiko.** Tambahkan pilihan lapisan InaRISK/IRBI BNPB (WMS/GeoJSON) dan hitung SPPG per kelas risiko per provinsi.
5. **Isochrone.** Ganti haversine dengan waktu tempuh (OSRM publik atau Valhalla) sebagai opsi; tetap sediakan mode garis lurus untuk offline.
6. **Pembaruan daftar SPPG.** Halaman `https://www.bgn.go.id/operasional-sppg?page=N&search=` adalah tabel HTML 10 baris/halaman (~3.000 halaman), me-redirect ke beranda bila user-agent bukan browser. Buat scraper sopan (jeda 1–2 detik, retry, checkpoint) yang menulis `data/raw/data_sppg.csv` dengan kolom yang sama.
7. **Performa.** Bila titik bertambah jauh, pertimbangkan memindahkan data ke file JSON terpisah yang dimuat via fetch (perlu server, tidak bisa file://), atau ke format biner.
