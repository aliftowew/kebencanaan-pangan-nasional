"""
01_match_kecamatan.py
Mencocokkan daftar SPPG (tanpa koordinat) ke centroid kecamatan dari gazetteer BPS 2021.

Input (diunduh otomatis ke data/raw/ bila belum ada):
  - data_sppg.csv   : salinan komunitas daftar "SPPG Operasional" bgn.go.id
                      (repo mekel16/Graph-on-Data-SPPG-Indonesia, commit 26 Agu 2026)
  - districts.json  : 7.071 kecamatan + koordinat (repo yusufsyaifudin/wilayah-indonesia, BPS 2021)
  - regencies.json  : 514 kab/kota + koordinat (repo yang sama)

Output:
  - data/sppg_27387_titik_kecamatan.csv
  - data/sppg_27387_titik_kecamatan.geojson

Untuk memperbarui daftar SPPG: ganti data/raw/data_sppg.csv dengan ekspor terbaru
(kolom: Provinsi SPPG, Kab./Kota SPPG, Kecamatan SPPG, Kelurahan/Desa SPPG, Alamat SPPG, Nama SPPG).
Jika ekspor resmi BGN sudah memuat lat/lon, gunakan itu dan lewati skrip ini.
"""
import json, re, unicodedata, difflib, os, sys, urllib.request
from collections import defaultdict
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw"); os.makedirs(RAW, exist_ok=True)
SRC = {
  "data_sppg.csv": "https://raw.githubusercontent.com/mekel16/Graph-on-Data-SPPG-Indonesia/main/data/data_sppg.csv",
  "districts.json": "https://raw.githubusercontent.com/yusufsyaifudin/wilayah-indonesia/master/data/list_of_area/districts.json",
  "regencies.json": "https://raw.githubusercontent.com/yusufsyaifudin/wilayah-indonesia/master/data/list_of_area/regencies.json",
}
for name, url in SRC.items():
    p = os.path.join(RAW, name)
    if not os.path.exists(p):
        print("unduh", name); urllib.request.urlretrieve(url, p)

df = pd.read_csv(os.path.join(RAW, "data_sppg.csv"))
df = df.rename(columns={"Provinsi SPPG":"prov","Kab./Kota SPPG":"kab","Kecamatan SPPG":"kec",
                        "Kelurahan/Desa SPPG":"desa","Alamat SPPG":"alamat","Nama SPPG":"nama"})
df = df[["prov","kab","kec","desa","alamat","nama"]].copy()
for c in df.columns:
    df[c] = df[c].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
print("baris mentah:", len(df))

reg = json.load(open(os.path.join(RAW, "regencies.json")))
dist = json.load(open(os.path.join(RAW, "districts.json")))
reg_by_id = {r["id"]: r for r in reg}
d_by_reg = defaultdict(list)
for d in dist: d_by_reg[d["regency_id"]].append(d)

NUM = {"SATU":"1","DUA":"2","TIGA":"3","EMPAT":"4","LIMA":"5","ENAM":"6","TUJUH":"7","DELAPAN":"8","SEMBILAN":"9","SEPULUH":"10",
       "I":"1","II":"2","III":"3","IV":"4","V":"5","VI":"6","VII":"7","VIII":"8","IX":"9","X":"10"}
def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode().upper().strip()
    s = re.sub(r"^(KABUPATEN|KAB\.?)\s+", "", s); s = re.sub(r"^KEC\.?\s+", "", s)
    s = s.replace("KEP.", "KEPULAUAN"); s = re.sub(r"[^A-Z0-9 ]", "", s)
    return re.sub(r"\s+", " ", s).strip()
def squash(s): return norm(s).replace(" ", "")
def canon(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode().upper()
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return "".join(NUM.get(t, t) for t in s.split())

# nama kab/kota di BGN yang berbeda dari gazetteer 2021
ALIAS = {"PASANGKAYU":"MAMUJU UTARA","KOTA TANJUNG PINANG":"KOTA TANJUNGPINANG","KOTA SAWAH LUNTO":"KOTA SAWAHLUNTO",
 "KOTA PANGKAL PINANG":"KOTA PANGKALPINANG","KOTA PALANGKARAYA":"KOTA PALANGKA RAYA","FAK FAK":"FAKFAK",
 "KOTA GUNUNG SITOLI":"KOTA GUNUNGSITOLI","KOTA PEMATANG SIANTAR":"KOTA PEMATANGSIANTAR","LABUHANBATU":"LABUHAN BATU",
 "LABUHANBATU UTARA":"LABUHAN BATU UTARA","LABUHANBATU SELATAN":"LABUHAN BATU SELATAN","TOBA":"TOBA SAMOSIR",
 "PAHUWATO":"POHUWATO","KOTA BAUBAU":"KOTA BAU-BAU","MUKO MUKO":"MUKOMUKO","TOJO UNA UNA":"TOJO UNA-UNA",
 "KOTA BANJAR BARU":"KOTA BANJARBARU","KOTA LUBUK LINGGAU":"KOTA LUBUKLINGGAU","KOTA PARE PARE":"KOTA PAREPARE",
 "KEPULAUAN SIAU TAGULANDANG BIARO":"SIAU TAGULANDANG BIARO","SITARO":"SIAU TAGULANDANG BIARO",
 "KEPULAUAN TANIMBAR":"MALUKU TENGGARA BARAT","KOTA ADMINISTRASI JAKARTA PUSAT":"KOTA JAKARTA PUSAT",
 "KOTA ADMINISTRASI JAKARTA UTARA":"KOTA JAKARTA UTARA","KOTA ADMINISTRASI JAKARTA BARAT":"KOTA JAKARTA BARAT",
 "KOTA ADMINISTRASI JAKARTA SELATAN":"KOTA JAKARTA SELATAN","KOTA ADMINISTRASI JAKARTA TIMUR":"KOTA JAKARTA TIMUR",
 "ADMINISTRASI KEPULAUAN SERIBU":"KEPULAUAN SERIBU"}
reg_idx = defaultdict(list)
for r in reg:
    reg_idx[norm(r["name"])].append(r["id"]); reg_idx[squash(r["name"])].append(r["id"])
def find_reg(kab):
    k = norm(kab); k2 = ALIAS.get(k, k)
    for cand in (k2, k, squash(k2), squash(k)):
        if cand in reg_idx: return reg_idx[cand]
    m = difflib.get_close_matches(squash(k2), [n for n in reg_idx if " " not in n], n=1, cutoff=0.86)
    return reg_idx[m[0]] if m else []

cache = {}
def locate(kab, kec):
    key = (norm(kab), norm(kec))
    if key in cache: return cache[key]
    r = None; rids = find_reg(kab)
    if rids:
        kecs = [d for rid in rids for d in d_by_reg[rid]]
        ks, kn = squash(kec), canon(kec)
        hit = [d for d in kecs if squash(d["name"]) == ks] or [d for d in kecs if canon(d["name"]) == kn]
        if not hit:  # fuzzy: ejaan berbeda (LABUHANBATU/LABUHAN BATU), angka romawi vs kata
            m = difflib.get_close_matches(ks, [squash(d["name"]) for d in kecs], n=1, cutoff=0.8)
            if m: hit = [d for d in kecs if squash(d["name"]) == m[0]]
        if not hit:
            m = difflib.get_close_matches(kn, [canon(d["name"]) for d in kecs], n=1, cutoff=0.75)
            if m: hit = [d for d in kecs if canon(d["name"]) == m[0]]
        if hit and hit[0].get("latitude") is not None:
            d = hit[0]; r = (d["latitude"], d["longitude"], "kecamatan", d["regency_id"], d["id"])
        else:
            g = reg_by_id[rids[0]]; r = (g["latitude"], g["longitude"], "kabkota", g["id"], None)
    cache[key] = r; return r

res = [locate(k, c) for k, c in zip(df["kab"], df["kec"])]
df["lat"] = [r[0] if r else None for r in res]; df["lon"] = [r[1] if r else None for r in res]
df["presisi"] = [r[2] if r else "none" for r in res]
df["kode_kab_bps"] = [r[3] if r else None for r in res]; df["kode_kec_bps"] = [r[4] if r else None for r in res]

before = len(df)
df = df.drop_duplicates(subset=["nama","kab","kec","desa"]).reset_index(drop=True)
print(f"duplikat dihapus: {before-len(df)} -> {len(df)} baris")

df["prov"] = df["prov"].str.replace("P A P U A","PAPUA",regex=False).str.replace("DAERAH ISTIMEWA YOGYAKARTA","DI YOGYAKARTA",regex=False)

# --- Validasi koordinat terhadap poligon provinsi ---
# Gazetteer menempatkan sebagian kecamatan bernama umum (TAMAN, KEDIRI, SELONG,
# PULAUPINANG, ...) di provinsi lain, bahkan di luar negeri. Titik yang jatuh di dalam
# provinsi lain, atau > FAR derajat dari provinsi yang diklaim BGN, diganti centroid
# kab/kota (presisi tetap jujur: "kabkota"). Toleransi NEAR dan aturan lepas-pantai
# menerima kecamatan kepulauan yang hilang dari poligon provinsi yang disederhanakan
# (Kep. Seribu, pulau-pulau Sumenep, Natuna, Sitaro, Takabonerate, dll.).
provgeo = json.load(open(os.path.join(ROOT, "scripts", "indonesia_38_prov.min.json")))
def _rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def _inside(lon, lat, ring):
    ok = False; j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]; xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi: ok = not ok
        j = i
    return ok
def _dist(lon, lat, ring): return min(((lon - p[0])**2 + (lat - p[1])**2) ** .5 for p in ring)
def pkey(s):
    s = norm(s)
    return "DI YOGYAKARTA" if s == "DAERAH ISTIMEWA YOGYAKARTA" else s
prov_rings = defaultdict(list)
for f in provgeo["features"]:
    prov_rings[pkey(f["properties"]["PROVINSI"])] += _rings(f["geometry"])
NEAR, FAR = 0.25, 1.2
def coord_ok(prov, lat, lon):
    own = prov_rings.get(pkey(prov))
    if not own: return True  # provinsi tak dikenal: jangan buang
    if any(_inside(lon, lat, r) for r in own): return True
    d = min(_dist(lon, lat, r) for r in own)
    if d <= NEAR: return True
    if d > FAR: return False
    # dekat provinsi sendiri tapi di luar poligon: terima kecuali jelas di provinsi lain
    return not any(_inside(lon, lat, r) for k, rs in prov_rings.items() if k != pkey(prov) for r in rs)

def fix_coord(prov, lat, lon, rid):
    """None = titik sudah benar; selain itu (lat, lon, presisi, cara)."""
    if pd.isna(lat) or coord_ok(prov, lat, lon): return None
    g = reg_by_id.get(rid)
    if g and g.get("latitude") is not None and coord_ok(prov, g["latitude"], g["longitude"]):
        return (g["latitude"], g["longitude"], "kabkota", "centroid kab")
    # centroid kab di gazetteer ikut salah: pakai rata-rata kecamatan valid di kab itu
    pts = [(d["latitude"], d["longitude"]) for d in d_by_reg.get(rid, [])
           if d.get("latitude") is not None and coord_ok(prov, d["latitude"], d["longitude"])]
    if pts:
        la = sum(p[0] for p in pts) / len(pts); lo = sum(p[1] for p in pts) / len(pts)
        if coord_ok(prov, la, lo): return (la, lo, "kabkota", "rata-rata kec valid")
    return (None, None, "none", "dibuang")

vcache = {}; n_fix = defaultdict(int); contoh = []
lat_l, lon_l, pre_l = df["lat"].tolist(), df["lon"].tolist(), df["presisi"].tolist()
for i, (prov, kab, kec, rid) in enumerate(zip(df["prov"], df["kab"], df["kec"], df["kode_kab_bps"])):
    key = (pkey(prov), norm(kab), norm(kec))
    if key not in vcache: vcache[key] = fix_coord(prov, lat_l[i], lon_l[i], rid)
    f = vcache[key]
    if f is not None:
        if len(contoh) < 8 and (prov, kab, kec) not in [c[:3] for c in contoh]:
            contoh.append((prov, kab, kec, lat_l[i], lon_l[i], f[3]))
        lat_l[i], lon_l[i], pre_l[i] = f[0], f[1], f[2]; n_fix[f[3]] += 1
df["lat"], df["lon"], df["presisi"] = lat_l, lon_l, pre_l
print("validasi provinsi:", dict(n_fix) or "semua titik lolos")
for c in contoh: print("  perbaikan:", c)

print("presisi:", df["presisi"].value_counts().to_dict())
if (df["presisi"] == "none").any():
    print("PERHATIAN, baris tanpa koordinat tepercaya:", len(df[df.presisi=="none"]))
df.insert(0, "id_sppg", [f"S{i+1:05d}" for i in range(len(df))])
df["lat"] = df["lat"].round(5); df["lon"] = df["lon"].round(5)
out = df[["id_sppg","nama","prov","kab","kec","desa","alamat","lat","lon","presisi","kode_kab_bps","kode_kec_bps"]]
stem = os.path.join(ROOT, "data", f"sppg_{len(out)}_titik_kecamatan")
out.to_csv(stem + ".csv", index=False)
feats = [{"type":"Feature","geometry":{"type":"Point","coordinates":[float(r.lon), float(r.lat)]},
          "properties":{"id":r.id_sppg,"nama":r.nama,"prov":r.prov,"kab":r.kab,"kec":r.kec,"desa":r.desa,"presisi":r.presisi}}
         for r in out.itertuples() if pd.notna(r.lat)]
json.dump({"type":"FeatureCollection","features":feats}, open(stem + ".geojson","w"), ensure_ascii=False)
print("tersimpan:", stem + ".csv / .geojson")
