"""ogrenci/icerik/*.json dosyalarından Duru'nun Çalışma Masası veritabanına yazılacak belgeleri üretir.

Kullanım: python3 -I scripts/icerik_hazirla.py ogrenci/icerik <çıktı_dizini>
Çıktı: <çıktı_dizini>/konu-<id>.json (konular/<id> belgesi) ve banka-<id>.json (bankalar/<id> belgesi).
Karışık tekrar testlerindeki sorular kaynak koduna göre doğru üniteye taşınır, tekrarlar ayıklanır.
Mevcut `durum`/`veliNotu` alanlarını ezmemek için konu belgeleri `update` ile yazılmalıdır (ilk kez: `set`).
"""
import glob, json, os, re, sys

DERS_SIRA = ["Türkçe", "Matematik", "Fen Bilimleri", "T.C. İnkılap Tarihi ve Atatürkçülük",
             "Din Kültürü ve Ahlak Bilgisi", "İngilizce"]
KOD_UNITE = {"MAT-ÇK": "mat-ck", "MAT-ÜS": "mat-us", "MAT-KK": "mat-kk"}


def anahtar(metin):
    return re.sub(r"\W", "", metin.lower())[:120]


def main(kaynak, cikti):
    os.makedirs(cikti, exist_ok=True)
    uniteler = {}
    for f in sorted(glob.glob(os.path.join(kaynak, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        uniteler[d["id"]] = d

    # Karışık tekrar testi sorularını kaynak koduna göre üniteye dağıt.
    tasinacak = []
    for d in uniteler.values():
        kalan = []
        for q in d["sorular"]:
            hedef = KOD_UNITE.get("-".join(q.get("kaynakKod", "").split("-")[:2]))
            if q.get("tur") == "tekrar" and hedef and hedef != d["id"] and hedef in uniteler:
                tasinacak.append((hedef, q))
            else:
                kalan.append(q)
        d["sorular"] = kalan
    for hedef, q in tasinacak:
        uniteler[hedef]["sorular"].append(q)

    for d in uniteler.values():
        gorulen, temiz = set(), []
        for q in d["sorular"]:
            k = anahtar(q["metin"]) + "|" + "|".join(q["secenekler"])
            if k in gorulen:
                continue
            gorulen.add(k)
            temiz.append(q)
        # Kimlikleri yeniden numaralandırma: kimlikler denemelerde saklanır, sabit kalmalı.
        ids = set()
        for q in temiz:
            while q["id"] in ids:
                q["id"] += "b"
            ids.add(q["id"])
        d["sorular"] = temiz

    for d in uniteler.values():
        sira = DERS_SIRA.index(d["ders"]) * 100 + int(re.match(r"\D*(\d+)", d["unite"]).group(1))
        konu = {k: d[k] for k in ("id", "ders", "unite", "baslik", "anlatim", "tuyolar", "hatalar")}
        konu.update(sira=sira, soruSayisi=len(d["sorular"]))
        json.dump(konu, open(os.path.join(cikti, f"konu-{d['id']}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        banka = {"konuId": d["id"], "sorular": d["sorular"]}
        json.dump(banka, open(os.path.join(cikti, f"banka-{d['id']}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        print(f"{d['id']:8} {len(d['sorular']):3} soru  {len(d['hatalar']):3} hata  "
              f"{len(json.dumps(banka, ensure_ascii=False).encode()) // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
