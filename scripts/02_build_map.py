"""
02_build_map.py
Menyusun index.html (peta Leaflet mandiri) dari:
  data/sppg_*_titik_kecamatan.csv  -> titik SPPG (dipadatkan)
  data/bulog_kanwil_26.csv          -> 26 Kanwil BULOG
  data/bulog_gudang.csv             -> gudang BULOG (baris dengan lat/lon terisi saja)
  scripts/indonesia_38_prov.min.json-> batas provinsi
  scripts/map_template.html         -> template UI
Jalankan: python scripts/02_build_map.py  (hasil: index.html di root repo)
"""
import json, os, glob
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)

src = sorted(glob.glob(D("data", "sppg_*_titik_kecamatan.csv")))[-1]
df = pd.read_csv(src).dropna(subset=["lat","lon"])
provs = sorted(df.prov.unique()); kabs = sorted(df.kab.unique()); kecs = sorted(df.kec.unique())
pi = {p:i for i,p in enumerate(provs)}; ki = {k:i for i,k in enumerate(kabs)}; ci = {k:i for i,k in enumerate(kecs)}
pts = [[round(float(r.lat),5), round(float(r.lon),5), str(r.nama).replace("SPPG ","",1), ki[r.kab], ci[r.kec], pi[r.prov],
        1 if r.presisi == "kecamatan" else 0] for r in df.itertuples()]
sppg = json.dumps({"provs":provs,"kabs":kabs,"kecs":kecs,"pts":pts}, ensure_ascii=False, separators=(",",":"))

kw = pd.read_csv(D("data","bulog_kanwil_26.csv"))
kanwil = json.dumps([{"n":r.kanwil,"c":r.kota,"a":r.alamat,"lat":float(r.lat),"lon":float(r.lon),"p":r.presisi} for r in kw.itertuples()],
                    ensure_ascii=False, separators=(",",":"))

gd = pd.read_csv(D("data","bulog_gudang.csv")).dropna(subset=["lat","lon"])
gudang = json.dumps([{"n":str(r.nama),"lat":float(r.lat),"lon":float(r.lon),
                      "kap":(None if pd.isna(r.kapasitas_ton) else float(r.kapasitas_ton)),
                      "kanwil":(None if pd.isna(r.kanwil) else str(r.kanwil))} for r in gd.itertuples()],
                    ensure_ascii=False, separators=(",",":"))

prov = open(D("scripts","indonesia_38_prov.min.json"), encoding="utf-8").read()
html = open(D("scripts","map_template.html"), encoding="utf-8").read()
html = html.replace("__SPPG__", sppg).replace("__KANWIL__", kanwil).replace("__GUDANG__", gudang).replace("__PROV__", prov)
open(D("index.html"), "w", encoding="utf-8").write(html)
print(f"index.html: {len(pts)} SPPG, {len(kw)} kanwil, {len(gd)} gudang, {os.path.getsize(D('index.html'))/1e6:.2f} MB")
