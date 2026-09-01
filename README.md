# Peta Logistik Tanggap Bencana: SPPG & BULOG

Peta interaktif 27.387 dapur MBG (Satuan Pelayanan Pemenuhan Gizi) dan jaringan Perum BULOG di Indonesia, untuk merencanakan respons pangan bencana dari daerah: klik titik bencana, lihat berapa SPPG dan gudang BULOG dalam radius 10 sampai 100 km beserta taksiran porsi per hari.

**Ide dasarnya:** saat bencana, bantuan pangan tidak perlu dikirim dari pusat. Dapur SPPG dan gudang BULOG yang sudah ada di sekitar lokasi bisa dimobilisasi lebih cepat. Preseden sudah ada: BGN mengalihkan 341 SPPG menjadi dapur darurat saat banjir dan longsor Sumatra (Des 2025) dan 71 SPPG saat gempa NTT (Agu 2026), dengan payung Surat Edaran BGN No. 7/2025 tentang pelayanan MBG dalam kedaruratan bencana. Yang belum ada: peta pra-bencana yang menjawab pertanyaan itu sebelum kejadian.

## Lihat petanya

Buka `index.html` di browser, atau aktifkan GitHub Pages (Settings, Pages, branch `main`, folder `/root`) supaya peta bisa dibuka dari tautan. File ini mandiri: data sudah tertanam, hanya butuh internet untuk peta dasar (CARTO/OpenStreetMap) dan pustaka Leaflet dari CDN.

Fitur:

- 27.387 titik SPPG dengan pengelompokan otomatis (klaster) dan pencarian kabupaten, kecamatan, atau nama SPPG
- 26 Kanwil BULOG
- Simulasi titik bencana: klik peta, pilih radius, dapatkan jumlah SPPG, taksiran porsi/hari (asumsi 3.000 porsi per SPPG, bisa diubah), rincian per kab/kota, Kanwil dan gudang BULOG terdekat, lalu salin ringkasannya
- Batas 38 provinsi dengan jumlah SPPG

## Isi repo

| Path | Isi |
|---|---|
| `index.html` | Peta siap pakai (hasil `scripts/02_build_map.py`) |
| `data/sppg_27387_titik_kecamatan.csv` / `.geojson` | Daftar SPPG dengan koordinat centroid kecamatan |
| `data/sppg_provinsi_juni2026.csv` | Rekap resmi BGN per provinsi, 8 Juni 2026 (29.991 unit) |
| `data/bulog_kanwil_26.csv` | 26 Kantor Wilayah BULOG, alamat dan koordinat kota |
| `data/bulog_gudang.csv` | Daftar gudang BULOG, baru berisi 1 contoh; isi dari data resmi |
| `data/Peta_Logistik_Bencana_SPPG_BULOG.xlsx` | Workbook: rekap provinsi, Kanwil, detail SPPG, template gudang |
| `scripts/01_match_kecamatan.py` | Unduh sumber mentah, cocokkan SPPG ke kecamatan, buang duplikat, ekspor |
| `scripts/02_build_map.py` | Tanam data ke `scripts/map_template.html` menjadi `index.html` |

## Cara membangun ulang

```bash
pip install -r scripts/requirements.txt
python scripts/01_match_kecamatan.py   # unduh data mentah ke data/raw/, hasilkan CSV + GeoJSON
python scripts/02_build_map.py         # hasilkan index.html
```

## Presisi dan batasan data, penting dibaca

1. **Titik SPPG bukan alamat persis.** Halaman publik BGN tidak memuat koordinat, jadi setiap SPPG diplot pada centroid kecamatannya (27.109 baris, 99%) atau centroid kab/kota bila nama kecamatan tidak cocok dengan gazetteer (278 baris, 1%). Cukup untuk perencanaan radius puluhan km; tidak cukup untuk routing lapangan. Kolom `presisi` menandai setiap baris.
2. **Snapshot daftar SPPG.** Daftar diambil dari salinan komunitas halaman `bgn.go.id/operasional-sppg` (27.640 baris; 253 duplikat akibat pergeseran paginasi dihapus). File di-commit 26 Agustus 2026, tanggal pengambilannya tidak dinyatakan. Rekap resmi BGN per 8 Juni 2026 mencatat 29.991 unit; sejak Juni 2026 ada moratorium SPPG baru dan ribuan unit sempat disuspensi, jadi selisih angka wajar. Minta ekspor resmi BGN (yang memuat koordinat) untuk versi otoritatif.
3. **Jarak dalam simulasi adalah garis lurus (haversine)**, bukan waktu tempuh. Untuk kepulauan dan pegunungan, selisihnya bisa besar.
4. **Gudang BULOG belum terisi.** Tidak ada sumber publik dengan koordinat gudang; struktur nasional BULOG adalah 26 Kanwil, sekitar 101 Kancab, 30 Kancab Pembantu, sekitar 500 kompleks gudang milik (kapasitas 3 juta ton) dan 1.254 gudang filial sewa (2,69 juta ton per April 2026), plus 100 gudang baru yang sedang dibangun di 92 kab/kota. Isi `data/bulog_gudang.csv` dari data resmi BULOG lalu jalankan `02_build_map.py`.
5. Alamat Kanwil BULOG bersumber dari dokumen 2021; koordinatnya tingkat kota (kecuali Bali yang punya titik alamat). Verifikasi sebelum dipakai untuk routing.

## Sumber

- Daftar SPPG: bgn.go.id/operasional-sppg via repo [mekel16/Graph-on-Data-SPPG-Indonesia](https://github.com/mekel16/Graph-on-Data-SPPG-Indonesia)
- Rekap SPPG per provinsi: BGN, dikutip IDN Times 8 Juni 2026
- Koordinat kecamatan dan kab/kota (BPS 2021): [yusufsyaifudin/wilayah-indonesia](https://github.com/yusufsyaifudin/wilayah-indonesia)
- Batas 38 provinsi: [denyherianto/indonesia-geojson-topojson-maps-with-38-provinces](https://github.com/denyherianto/indonesia-geojson-topojson-maps-with-38-provinces)
- Kanwil BULOG: Tabel 1.1 Laporan Kerja Praktik ULBI (data Perum BULOG 2021); struktur 26 Kanwil dikonfirmasi Dirut BULOG, 22 April 2026
- Kebijakan: Perpres 125/2022 (Cadangan Pangan Pemerintah, termasuk untuk bencana); SE BGN No. 7/2025 dan revisinya (Agustus 2026)

## Langkah lanjutan

- Ganti centroid kecamatan dengan koordinat resmi BGN
- Isi gudang BULOG dan kapasitas/stok per gudang
- Tambah lapisan risiko bencana InaRISK/IRBI BNPB dan data pengungsi historis (DIBI)
- Ganti radius garis lurus dengan isochrone waktu tempuh (OSRM/Valhalla)
- Skrip pembaruan daftar SPPG langsung dari bgn.go.id (halaman menolak akses non-browser; perlu user-agent browser dan jeda antar halaman)
