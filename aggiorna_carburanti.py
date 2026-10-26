#!/usr/bin/env python3
"""Estrae dall'open data MIMIT i distributori di Terrasini e dintorni con i prezzi.

Fonte: Ministero delle Imprese e del Made in Italy, "Carburanti, prezzi praticati e
anagrafica degli impianti" (licenza IODL 2.0, aggiornamento quotidiano, dati delle ore 8
del giorno prima). Pagina: https://www.mimit.gov.it/it/open-data/elenco-dataset/carburanti-prezzi-praticati-e-anagrafica-degli-impianti

Uso:
    python aggiorna_carburanti.py                 # scarica e scrive carburanti.json
    python aggiorna_carburanti.py --raggio 15     # raggio in km dal centro (default 10)
    python aggiorna_carburanti.py --anagrafica a.csv --prezzi p.csv   # file già scaricati

Solo libreria standard. Non serve nessun account. Dal 10/02/2026 il separatore dei CSV è "|".
"""
import argparse, csv, io, json, math, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL_ANAGRAFICA = "https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"
URL_PREZZI = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
UA = "terrasini-mappa/1.0 (+https://trupianovisual.com; trupystudios.ia@gmail.com)"
CENTRO = (38.1522, 13.0832)  # piazza del paese, lat/lon
COMUNE = "TERRASINI"

def scarica(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace"), r.headers.get("Last-Modified")

def leggi_csv(testo):
    righe = testo.splitlines()
    estrazione = righe[0].replace("Estrazione del", "").strip() if righe and righe[0].startswith("Estrazione") else None
    corpo = "\n".join(righe[1:]) if estrazione else testo
    return estrazione, list(csv.DictReader(io.StringIO(corpo), delimiter="|"))

def km(a, b):
    r = 6371.0088
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))

def num(s):
    try:
        return float(str(s).replace(",", "."))
    except ValueError:
        return None

def iso(dt):
    try:
        return datetime.strptime(dt.strip(), "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d")
    except ValueError:
        return None

def prezzo(imp, carburante, self_):
    v = [p["prezzo"] for p in imp["prezzi"] if p["carburante"] == carburante and p["self"] == self_]
    return min(v) if v else None

def geojson(out):
    """Punti con campi piatti per MapLibre. Un campo vuoto vuol dire 'prezzo non comunicato'."""
    feats = []
    for i in out["impianti"]:
        altri = sorted({p["carburante"] for p in i["prezzi"]} - {"Benzina", "Gasolio", "GPL", "Metano"})
        props = {
            "id": "mimit/" + i["id"], "nome": i["nome"], "bandiera": i["bandiera"], "indirizzo": i["indirizzo"],
            "comune": i["comune"], "in_comune": i["in_comune"], "distanza_km": i["distanza_km"],
            "benzina_self": prezzo(i, "Benzina", True), "benzina_servito": prezzo(i, "Benzina", False),
            "gasolio_self": prezzo(i, "Gasolio", True), "gasolio_servito": prezzo(i, "Gasolio", False),
            "gpl": prezzo(i, "GPL", False) or prezzo(i, "GPL", True), "metano": prezzo(i, "Metano", False) or prezzo(i, "Metano", True),
            "altri_carburanti": "; ".join(altri),
            "prezzo_comunicato": i["ultima_comunicazione"],
            "estrazione": out["estrazione_mimit"],
            "fonte": "MIMIT, Osservatorio prezzi carburanti", "licenza": "IODL 2.0",
            "link_fonte": out["link_fonte"],
        }
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [i["lon"], i["lat"]]}, "properties": props})
    return {"type": "FeatureCollection", "name": "carburanti_terrasini", "licenza_file": out["licenza"],
            "attribuzione": out["attribuzione"], "estrazione": out["estrazione_mimit"], "features": feats}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raggio", type=float, default=10.0)
    ap.add_argument("--anagrafica")
    ap.add_argument("--prezzi")
    ap.add_argument("--out", default=str(Path(__file__).with_name("carburanti.json")))
    a = ap.parse_args()

    if a.anagrafica and a.prezzi:
        t_an, t_pr = Path(a.anagrafica).read_text(encoding="utf-8"), Path(a.prezzi).read_text(encoding="utf-8")
        lm_an = lm_pr = None
    else:
        t_an, lm_an = scarica(URL_ANAGRAFICA)
        t_pr, lm_pr = scarica(URL_PREZZI)
    est_an, impianti = leggi_csv(t_an)
    est_pr, prezzi = leggi_csv(t_pr)

    scelti = {}
    for r in impianti:
        lat, lon = num(r.get("Latitudine")), num(r.get("Longitudine"))
        if lat is None or lon is None or not (35 < lat < 39 and 11 < lon < 16):
            continue
        d = km(CENTRO, (lat, lon))
        stesso = (r.get("Comune") or "").strip().upper() == COMUNE
        if stesso or d <= a.raggio:
            scelti[r["idImpianto"]] = {
                "id": r["idImpianto"],
                "nome": (r.get("Nome Impianto") or "").strip(),
                "bandiera": (r.get("Bandiera") or "").strip(),
                "gestore": (r.get("Gestore") or "").strip(),
                "tipo": (r.get("Tipo Impianto") or "").strip(),
                "indirizzo": " ".join((r.get("Indirizzo") or "").split()),
                "comune": (r.get("Comune") or "").strip().title(),
                "provincia": (r.get("Provincia") or "").strip(),
                "lat": round(lat, 6), "lon": round(lon, 6),
                "distanza_km": round(d, 1),
                "in_comune": stesso,
                "prezzi": [],
            }
    for r in prezzi:
        imp = scelti.get(r["idImpianto"])
        p = num(r.get("prezzo"))
        if imp is None or p is None or p <= 0:
            continue
        imp["prezzi"].append({
            "carburante": r["descCarburante"].strip(),
            "prezzo": round(p, 3),
            "self": r.get("isSelf") == "1",
            "comunicato": iso(r.get("dtComu", "")),
        })
    elenco = sorted(scelti.values(), key=lambda x: (not x["in_comune"], x["distanza_km"]))
    for imp in elenco:
        imp["prezzi"].sort(key=lambda x: (x["carburante"], not x["self"]))
        imp["ultima_comunicazione"] = max((p["comunicato"] for p in imp["prezzi"] if p["comunicato"]), default=None)

    out = {
        "titolo": "Distributori di Terrasini e dintorni con i prezzi",
        "fonte": "Ministero delle Imprese e del Made in Italy, Osservatorio prezzi carburanti (open data)",
        "licenza": "IODL 2.0 (https://www.dati.gov.it/iodl/2.0/)",
        "attribuzione": "Fonte: MIMIT, Osservatorio prezzi carburanti, licenza IODL 2.0",
        "link_fonte": "https://www.mimit.gov.it/it/open-data/elenco-dataset/carburanti-prezzi-praticati-e-anagrafica-degli-impianti",
        "link_ufficiale_prezzi": "https://carburanti.mise.gov.it/ospzSearch/home",
        "estrazione_mimit": est_pr or est_an,
        "pubblicato_mimit": lm_pr,
        "generato": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "centro": {"lat": CENTRO[0], "lon": CENTRO[1]},
        "raggio_km": a.raggio,
        "nota": "I prezzi sono quelli comunicati dai gestori e in vigore alle ore 8 del giorno prima dell'estrazione. Possono essere cambiati. Il prezzo alla pompa è quello che vale.",
        "impianti": elenco,
    }
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    Path(a.out).with_suffix(".geojson").write_text(json.dumps(geojson(out), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(elenco)} impianti ({sum(1 for i in elenco if i['in_comune'])} a Terrasini) scritti in {a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
