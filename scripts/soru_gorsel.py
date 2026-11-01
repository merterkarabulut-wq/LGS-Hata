"""Hata kartları için soru görüntüsü + çözüm alanlarını üretir.

Kullanım: python3 -I scripts/soru_gorsel.py <LGS_klasörü> <icerik_klasörü> <sorular_çıktı_klasörü> [dpi=150]
- Sorular PDF'lerinden her kodun soru bölgesini PNG olarak keser (pdftoppm).
- Çözümler ve Hata Analizi PDF'lerinden cevap/senin/cozum/hataAnaliz/tuyo/dikkat çıkarır.
- icerik/*.json içindeki her hataya `gorsel` ve bu alanları ekler (mevcut alanlara dokunmaz).
"""
import glob, json, os, re, subprocess, sys

KOD = r"[A-ZÇĞİÖŞÜ]+-[A-ZÇĞİÖŞÜ]+-\d+"
TR = str.maketrans("ÇĞİÖŞÜ", "CGIOSU")
SOL, SAG = 40, 555          # pt cinsinden yatay kırpma
ALT_BASLIKLAR = ["Doğru cevap:", "Çözüm", "Senin cevabın:", "Doğru yaptıkların", "Hatan neydi?",
                 "Kısa yol / Tüyo", "Dikkat"]


def dosya_adi(kod, parca, toplam):
    a = kod.translate(TR)
    return a + ".png" if toplam == 1 else f"{a}-{parca}.png"


def bbox_sayfalar(pdf):
    """[(genislik, yukseklik, [(x0,y0,x1,y1,metin)...]), ...]"""
    cikti = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    sayfalar = []
    for blok in cikti.split("<page ")[1:]:
        w = float(re.search(r'width="([\d.]+)"', blok).group(1))
        h = float(re.search(r'height="([\d.]+)"', blok).group(1))
        kel = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in re.findall(
            r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', blok)]
        kel = [(a, b, c, d, t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")) for a, b, c, d, t in kel]
        sayfalar.append((w, h, kel))
    return sayfalar


def soru_basliklari(sayfa):
    """Sayfadaki (yMin, kod) başlıkları."""
    _, _, kel = sayfa
    out = []
    for a, b, c, d, t in kel:
        if t != "Soru":
            continue
        for a2, b2, c2, d2, t2 in kel:
            if abs(b2 - b) < 3 and a2 > a + 100 and re.fullmatch(KOD, t2):
                out.append((b, t2))
                break
    return out


def bolgeler(sayfalar):
    """kod -> [(sayfa_no(1..), y0, y1), ...] pt cinsinden."""
    sonuc = {}
    for pi, sayfa in enumerate(sayfalar):
        w, h, kel = sayfa
        for y, kod in soru_basliklari(sayfa):
            parcalar = []
            p, ust = pi, y - 10
            while True:
                _, ph, pk = sayfalar[p]
                bas = [s[0] for s in soru_basliklari(sayfalar[p]) if s[0] > ust + 12]
                coz = [k[1] for k in pk if k[4] == "ÇÖZÜM" and k[1] > ust + 12]
                hat = [k[1] for k in pk if k[4] == "HATAM" and k[1] > ust + 12]
                if coz:
                    parcalar.append((p + 1, ust, min(coz) - 6)); break
                if hat:
                    parcalar.append((p + 1, ust, min(hat) - 6)); break
                if bas:
                    parcalar.append((p + 1, ust, min(bas) - 10)); break
                alt = [k[1] for k in pk if k[4] == "Sayfa" and k[1] > ust]
                parcalar.append((p + 1, ust, (min(alt) - 4) if alt else ph - 30))
                if p + 1 >= len(sayfalar):
                    break
                p += 1
                ust = 30
            sonuc[kod] = parcalar
    return sonuc


def kes(pdf, parcalar, kod, cikti, dpi):
    adlar = []
    for i, (p, y0, y1) in enumerate(parcalar, 1):
        ad = dosya_adi(kod, i, len(parcalar))
        onek = os.path.join(cikti, ad[:-4])
        f = dpi / 72
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-f", str(p), "-l", str(p), "-singlefile",
                        "-x", str(int(SOL * f)), "-y", str(int(max(y0, 0) * f)),
                        "-W", str(int((SAG - SOL) * f)), "-H", str(int(max(y1 - y0, 20) * f)),
                        pdf, onek], check=True)
        adlar.append("sorular/" + ad)
    return adlar


def duzles(satirlar):
    return re.sub(r"\s+", " ", " ".join(s.strip() for s in satirlar)).strip()


def bloklara_ayir(satirlar, layout):
    """Blok başlangıcı: satır sonunda KOD, hemen ardından (<=6 satır) 'Doğru cevap'."""
    bloklar, mevcut = {}, None
    for i, s in enumerate(satirlar):
        mk = re.search(rf"(?:^|\s)({KOD})\s*$", s)
        if mk and any(x.strip().startswith("Doğru cevap") for x in satirlar[i + 1:i + 7]):
            if not layout and mevcut:
                # önceki bloğun sonundaki tek satırlık bölüm/ünite başlığını at (ve Soru/numara artıkları)
                sat = bloklar[mevcut]
                while sat and not sat[-1].strip():
                    sat.pop()
                k = len(sat)
                while k > 0 and sat[k - 1].strip():
                    k -= 1
                if len(sat) - k == 1 and k > 0 and len(sat[-1].strip()) < 70 and not sat[-1].strip().endswith("."):
                    sat.pop()
            mevcut = mk.group(1)
            bloklar[mevcut] = []
        elif mevcut:
            bloklar[mevcut].append(s)
    return bloklar


def baslik_at(liste):
    """Bloğun sonundaki (boş satırla ayrılmış) tek satırlık bölüm başlığını at."""
    while liste and not liste[-1].strip():
        liste.pop()
    if len(liste) >= 2 and not liste[-2].strip() and len(liste[-1].strip()) < 70 \
            and not re.search(r'[.!?)"”:]\s*$', liste[-1].strip()):
        liste.pop()


def bolumle(sat, layout):
    bol, ad = {}, None
    for s in sat:
        t = s.strip()
        # Sonraki sorunun başlığı / bölüm sayfası / altbilgi artıkları: bloğu burada bitir
        if re.fullmatch(r"Soru(\s+\d+.*)?", t) or "kısa yollar ve tüyolar" in t or t.startswith("Bu ünitede") or " Bu ünitede " in t + " " or re.search(rf"\[{KOD}", t):
            if ad and ad != "Çözüm":
                baslik_at(bol[ad])
            break
        if re.fullmatch(r"\d{1,3}", t) or "Çözümler ve Hata Analizi" in t or t.startswith("LGS –"):
            continue
        bas = next((b for b in ALT_BASLIKLAR if t == b or (b.endswith(":") and t.startswith(b))), None)
        if bas and not (layout and s.startswith("    ")):
            if bas in bol:
                break
            ad = bas
            bol.setdefault(ad, [])
            rest = t[len(bas):].strip() if bas.endswith(":") else ""
            if rest:
                bol[ad].append(rest)
            continue
        if ad is None:
            continue
        # Ünite/bölüm başlığı (sütun 0) paragraf bölümlerinin sonuna karışmasın.
        if layout and ad in ("Doğru yaptıkların", "Hatan neydi?", "Kısa yol / Tüyo", "Dikkat") and t and not s.startswith(" "):
            continue
        bol[ad].append(s)
    return bol


def alanlar(bol):
    r = {}
    if "Doğru cevap:" in bol and duzles(bol["Doğru cevap:"]):
        r["cevap"] = duzles(bol["Doğru cevap:"])
    if "Senin cevabın:" in bol and duzles(bol["Senin cevabın:"]):
        r["senin"] = duzles(bol["Senin cevabın:"])
    if "Çözüm" in bol:
        adimlar, cur = [], None
        for s in bol["Çözüm"]:
            t = s.strip()
            if not t:
                continue
            if re.match(r"^\d+\.\s", t) and not s.startswith("    "):
                cur = [re.sub(r"^\d+\.\s*", "", t)]
                adimlar.append(cur)
            elif cur is not None:
                cur.append(t)
        adimlar = [duzles(a) for a in adimlar if duzles(a)]
        if adimlar:
            r["cozum"] = adimlar
    for anahtar, ad in (("hataAnaliz", "Hatan neydi?"), ("tuyo", "Kısa yol / Tüyo"), ("dikkat", "Dikkat")):
        if ad in bol and duzles(bol[ad]):
            r[anahtar] = duzles(bol[ad])
    return r


def temiz_cevap(r):
    return bool(re.match(r"^[A-Da-d](\) .{1,100})?$", r.get("cevap", "")))


def skor(r):
    metin = " ".join(str(v) for v in r.values())
    return (not temiz_cevap(r), len(re.findall(r"\b(\w{3,}) \1\b", metin)) + metin.count("ünitede") + metin.count("Soru ")
            + sum(1 for k in ("hataAnaliz", "tuyo", "dikkat") if k in r and not re.search(r'[.!?)"”:✓✗»…\']\s*$', r[k])))


def cozum_ayristir(pdf):
    adaylar = {}
    for layout in (False, True):
        args = ["pdftotext"] + (["-layout"] if layout else []) + [pdf, "-"]
        metin = subprocess.run(args, capture_output=True, text=True, check=True).stdout
        satirlar = []
        ham = metin.replace("\f", "\n").split("\n")
        for n, s in enumerate(ham):
            if re.match(r"^\s*LGS\s*[–-].*Çözümler ve Hata Analizi\s*(\d+)?\s*$", s):
                continue
            if not layout and re.fullmatch(r"\d{1,3}", s.strip()) and n >= 2 and re.match(r"^\s*LGS\s*[–-]", ham[n - 2] + ham[n - 1]):
                continue
            satirlar.append(s.rstrip())
        for kod, sat in bloklara_ayir(satirlar, layout).items():
            adaylar.setdefault(kod, []).append(alanlar(bolumle(sat, layout)))
    return {kod: min(l, key=skor) for kod, l in adaylar.items()}


DETAY_ALANLARI = ("gorsel", "cevap", "senin", "cozum", "hataAnaliz", "tuyo", "dikkat")


# Kullanıcının istediği elle düzeltmeler (yeniden kesimde kaybolmasın diye burada).
# TUR-SÖZ-2: kitapçıktaki "ç." maddesi A-B-C-D düzenine uysun diye "d." gösterilir.
# Görselde "b" harfi aynalanıp "ç"nin yerine konur (150 dpi kesime göre piksel konumları).
FEN20_METIN = [  # (alan, eski, yeni) — madde harfleri a..ğ,h → a..j
    ("cevap", "İklim: a, c, g, ğ. Hava olayı: b, ç, d, e, f, h.", "İklim: a, c, h, i. Hava olayı: b, d, e, f, g, j."),
    ("senin", "ç maddesini", "d maddesini"),
    ("hataAnaliz", "ç'yi", "d'yi"),
    ("soru", "ç maddesi", "d maddesi"),
    ("hata", "ç maddesini", "d maddesini"),
]
FEN20_COZUM = [
    ("g (kış ayları", "h (kış ayları"), ("ğ (35–40", "i (35–40"),
    ("d (yarın)", "e (yarın)"), ("e (sabah", "f (sabah"), ("f (günlük", "g (günlük"), ("h (akşam", "j (akşam"),
    ("ç: \"Atmosferde", "d: \"Atmosferde"),
]
FEN20_MAGICK = [
    "-fill", "white",
    "-draw", "rectangle 70,286 94,322", "-draw", "rectangle 70,330 94,366", "-draw", "rectangle 70,378 94,404",
    "-draw", "rectangle 70,446 94,474", "-draw", "rectangle 70,516 94,552", "-draw", "rectangle 70,560 94,596",
    "-draw", "rectangle 70,604 94,634",
    "-font", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", "-pointsize", "20", "-fill", "#1F2A44",
    "-annotate", "+72+311", "d.", "-annotate", "+72+355", "e.", "-annotate", "+72+399", "f.",
    "-annotate", "+72+468", "g.", "-annotate", "+72+540", "h.", "-annotate", "+72+584", "i.", "-annotate", "+72+627", "j.",
    "(", "+clone", "-crop", "555x30+95+446", "+repage", ")", "-geometry", "+100+446", "-composite",
    "-fill", "white", "-draw", "rectangle 95,446 99,475",
    "(", "+clone", "-crop", "555x34+95+289", "+repage", ")", "-geometry", "+98+289", "-composite",
    "-fill", "white", "-draw", "rectangle 95,289 97,322",
]


def elle_duzelt(kod, x, cikti, dpi):
    if kod == "FEN-MI-20":
        for alan, eski, yeni in FEN20_METIN:
            if isinstance(x.get(alan), str):
                x[alan] = x[alan].replace(eski, yeni)
        if isinstance(x.get("cozum"), list):
            yeni_c = []
            for a in x["cozum"]:
                for eski, yeni in FEN20_COZUM:
                    a = a.replace(eski, yeni)
                yeni_c.append(a)
            x["cozum"] = yeni_c
        png = os.path.join(cikti, "FEN-MI-20.png")
        if dpi == 150 and os.path.exists(png):
            subprocess.run(["magick", png, *FEN20_MAGICK, png], check=False)
        return
    if kod != "TUR-SÖZ-2":
        return
    for k in ("cozum",):
        if isinstance(x.get(k), list):
            x[k] = [a.replace(" ç: ", " d: ") for a in x[k]]
    if dpi != 150:
        return
    png = os.path.join(cikti, "TUR-SOZ-2.png")
    if os.path.exists(png):
        subprocess.run(["magick", png, "(", "+clone", "-crop", "15x19+72+234", "+repage", "-flop", ")",
                        "(", "-clone", "0", "-fill", "white", "-draw", "rectangle 70,300 84,323", ")",
                        "-delete", "0", "-swap", "0,1", "-geometry", "+70+301", "-composite", png], check=False)


def main(lgs, icerik, cikti, dpi=150):
    os.makedirs(cikti, exist_ok=True)
    soru_pdf, coz_pdf = {}, {}
    for pdf in sorted(glob.glob(os.path.join(lgs, "*", "*", "*.pdf"))):
        ad = os.path.basename(pdf)
        if "Benzer" in ad:
            continue
        if re.search(r"Set \d+ - Sorular\.pdf$", ad):
            for kod, parca in bolgeler(bbox_sayfalar(pdf)).items():
                soru_pdf.setdefault(kod, []).append((pdf, parca))
        elif re.search(r"Set \d+ - Çözümler ve Hata Analizi\.pdf$", ad):
            for kod, r in cozum_ayristir(pdf).items():
                coz_pdf.setdefault(kod, []).append(r)
    rapor, bulunamayan, uyari, supheli = [], [], [], []
    for f in sorted(glob.glob(os.path.join(icerik, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        n = g = c = t = 0
        for x in d["hatalar"]:
            kod = x.get("kod", "")
            n += 1
            if kod in soru_pdf:
                if len(soru_pdf[kod]) > 1:
                    uyari.append(f"{kod}: Sorular PDF'inde {len(soru_pdf[kod])} yerde")
                pdf, parca = soru_pdf[kod][0]
                x["gorsel"] = kes(pdf, parca, kod, cikti, dpi)
                g += 1
            else:
                bulunamayan.append(f"{kod} (görsel)")
            if kod in coz_pdf:
                if len(coz_pdf[kod]) > 1:
                    uyari.append(f"{kod}: Çözümler PDF'inde {len(coz_pdf[kod])} yerde")
                r = coz_pdf[kod][0]
                for k, v in r.items():
                    x[k] = v
                if "cevap" in r:
                    c += 1
                    cv = r["cevap"]
                    if "?" in cv or not re.match(r"^[A-Da-d]\b", cv):
                        supheli.append(f"{kod}: {cv!r}")
                else:
                    bulunamayan.append(f"{kod} (cevap)")
                if "tuyo" in r:
                    t += 1
            else:
                bulunamayan.append(f"{kod} (çözümler)")
            elle_duzelt(kod, x, cikti, dpi)
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
        rapor.append(f"{d['id']:8} hata={n:3} gorsel={g:3} cevap={c:3} tuyo={t:3}")
    # Sayfa ayrıntıları db yerine artifact dosyasından okur: kod → {gorsel, cevap, senin, cozum, hataAnaliz, tuyo, dikkat}
    detay = {}
    for f in sorted(glob.glob(os.path.join(icerik, "*.json"))):
        for x in json.load(open(f, encoding="utf-8")).get("hatalar", []):
            ek = {k: x[k] for k in DETAY_ALANLARI if k in x}
            if ek:
                detay[x["kod"]] = ek
    with open(os.path.join(cikti, "detay.json"), "w", encoding="utf-8") as fh:
        json.dump(detay, fh, ensure_ascii=False, separators=(",", ":"))
    rapor.append(f"detay.json: {len(detay)} kod")
    print("\n".join(rapor))
    print("Bulunamayan:", bulunamayan or "yok")
    print("Uyarı:", uyari or "yok")
    print("Şüpheli cevap:", supheli or "yok")
    top = sum(os.path.getsize(p) for p in glob.glob(os.path.join(cikti, "*.png")))
    print(f"PNG sayısı={len(glob.glob(os.path.join(cikti, '*.png')))} toplam={top/1e6:.1f} MB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 150)
