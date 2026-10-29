# CLAUDE.md

Bu dosya, Claude Code'un bu projede çalışırken bilmesi gerekenleri içerir.

## Proje Hakkında

**Duru LGS** — Duru'nun (8. sınıf) LGS (Liselere Geçiş Sistemi) hazırlığını takip etmek ve çalışmasını desteklemek için araçlar. Kullanıcı velidir.

## Dil ve İletişim

- Kullanıcıyla Türkçe iletişim kurulur.
- İçerik (sorular, açıklamalar, arayüz metinleri) Türkçe hazırlanır.

## Model Görev Dağılımı

Bu kural kalıcıdır; kullanıcının her oturumda tekrar belirtmesine gerek yoktur.

- **Opus 5.5 (`claude-opus-5-5`)** — Ana oturum. Tüm tasarım, mimari kararlar, planlama, yönetim/koordinasyon ve kontrol (kod inceleme, sonuç doğrulama) Opus'ta yapılır.
- **Sonnet 5.5 (`claude-sonnet-5-5`)** — Kod yazımı. Gerektiğinde tüm kod yazma/düzenleme işleri Agent aracıyla `model: "sonnet"` verilerek Sonnet'e devredilir. Opus görevi net tarif eder, çıkan kodu kontrol eder.
- **Haiku 5.5 (`claude-haiku-5-5`)** — Doküman işleri. Dokümanların (PDF, müfredat, soru kitapçığı vb.) okunması, analizi, özetlenmesi, düzenlenmesi ve yönetimi Agent aracıyla `model: "haiku"` verilerek Haiku'ya devredilir. Opus sonuçları değerlendirir.
- Küçük, tek adımlık işlerde (ör. tek satırlık düzeltme) devretmek yerine Opus doğrudan yapabilir.

## Teknoloji ve Yapı

Git deposu (origin: github.com/merterkarabulut-wq/LGS-Hata). Bağımlılık yok: saf HTML/JS ve yalnız standart kütüphaneli Python 3.

Dış veri (projenin dışında, kullanıcı yönetir):
- `/home/merterk/Belgeler/LGS/LGS_Takip.xlsx` — ana takip tablosu (Üniteler, Setler, Tekrar, Kaynaklar sayfaları).
- `/home/merterk/Belgeler/LGS/<Ders>/<Ünite>/` — set PDF'leri (Sorular, Benzer Sorular, Çözümler ve Hata Analizi, Konu Özeti, Tekrar Testi…). Yeni hatalı soru fotoğrafları `00 - Kaynaklar/<tarih>/` altına gelir; kullanıcı "yükledim" der.

Proje dosyaları:
- `scripts/xlsx_to_json.py` — Excel'i `data/*.json`'a çevirir (uniteler, setler, tekrar, kaynaklar); sonunda `veri_js.py`'yi çağırır.
- `scripts/veri_js.py` — `data/*.json`'u `data/veri.js` içinde `window.LGS_VERI` olarak toplar (file:// altında fetch çalışmadığı için). `veri.js` elle düzenlenmez.
- `dashboard/index.html` — claude.ai'deki "Duru LGS Takip" Dashboard artifact'ının sayfa kaynağı (veri artifact'ın kendi deposunda, `datasets/<id>`).
- `dashboard.html` — yerel, iki görünümlü panel: `#veli` (Veli Paneli) ve `#duru` (Duru'nun Alanı). `data/veri.js`'i okur; Duru'nun işaretlemeleri tarayıcı localStorage'ında (`duruLGS.v1`).
- `ogrenci/` — "Duru'nun Çalışma Masası": konu anlatımı, hata kartları, alıştırma/sınav motoru ve veli ödev paneli olan claude.ai artifact'ı (yapım aşamasında).
  - `ogrenci/SARTNAME.md` — sayfanın tam şartnamesi (db koleksiyonları: konular, bankalar, odevler, denemeler, ayarlar; veli = artifact sahibi).
  - `ogrenci/icerik/_GOREV.md` — PDF'lerden ünite JSON'u çıkarma görevi ve şeması.
  - `ogrenci/icerik/<id>.json` — ünite başına içerik (`<ders kısaltması>-<ünite kısaltması>`, ör. `fen-mev`, `tur-fii`, `ink-kah`).
  - `ogrenci/index.html` — sayfa (henüz yazılmadı).

## Komutlar

```bash
# Excel güncellenince (proje klasöründen) — data/*.json ve data/veri.js yenilenir
python3 -I scripts/xlsx_to_json.py /home/merterk/Belgeler/LGS/LGS_Takip.xlsx data

# Ünite JSON'u doğrula
python3 -I -c "import json,sys;json.load(open(sys.argv[1]))" ogrenci/icerik/<id>.json

# PDF metni oku (bozuk üs/kesir/şekilde sayfayı Read ile görsel oku, tahmin etme)
pdftotext -layout "<dosya>.pdf" -
```

## Kurallar

- Excel güncellemesinden sonra claude.ai dashboard'u otomatik güncellenmez: değişen JSON'lar artifact'a asset olarak yüklenip `datasets/<id>` belgelerindeki `source.url` ve `updated` güncellenir.
- Soru cevapları mutlaka cevap anahtarından gelir; emin olunmayan sorular `"emin": false` işaretlenir.
- Artifact sayfalarında veri metni `textContent` ile basılır, `innerHTML` ile değil.
- Python scriptleri `-I` ile çalıştırılır.
- **Oturum kapanışı:** Kullanıcı "oturumu kapatıyorum" dediğinde o oturumda değişen/öğrenilen her şeye göre bu `CLAUDE.md` ve memory dosyaları (`MEMORY.md` dizini dahil) güncellenir; ardından ne güncellendiği kısaca söylenip "Güncelledim, kapatabilirsin." denir.
