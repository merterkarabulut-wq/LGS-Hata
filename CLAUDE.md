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

Git deposu; uzak depo GitHub: `origin` → https://github.com/merterkarabulut-wq/LGS-Hata (dal: `main`; `.claude/worktrees/` git dışı). Bağımlılık yok: saf HTML/JS ve yalnız standart kütüphaneli Python 3.

Dış veri (projenin dışında, kullanıcı yönetir):
- `/home/merterk/Belgeler/LGS/LGS_Takip.xlsx` — ana takip tablosu (Üniteler, Setler, Tekrar, Kaynaklar sayfaları).
- `/home/merterk/Belgeler/LGS/<Ders>/<Ünite>/` — set PDF'leri (Sorular, Benzer Sorular, Çözümler ve Hata Analizi, Konu Özeti, Tekrar Testi…). Yeni hatalı soru fotoğrafları `00 - Kaynaklar/<tarih>/` altına gelir; kullanıcı "yükledim" der.

Proje dosyaları:
- `scripts/xlsx_to_json.py` — Excel'i `data/*.json`'a çevirir (uniteler, setler, tekrar, kaynaklar); sonunda `veri_js.py`'yi çağırır.
- `scripts/veri_js.py` — `data/*.json`'u `data/veri.js` içinde `window.LGS_VERI` olarak toplar (file:// altında fetch çalışmadığı için). `veri.js` elle düzenlenmez.
- `dashboard/index.html` — claude.ai'deki "Duru LGS Takip" Dashboard artifact'ının sayfa kaynağı (veri artifact'ın kendi deposunda, `datasets/<id>`).
- `dashboard.html` — yerel, iki görünümlü panel: `#veli` (Veli Paneli) ve `#duru` (Duru'nun Alanı). `data/veri.js`'i okur; Duru'nun işaretlemeleri tarayıcı localStorage'ında (`duruLGS.v1`).
- `ogrenci/` — "Duru'nun Çalışma Masası": konu anlatımı, hata kartları, alıştırma/sınav motoru ve veli ödev paneli olan claude.ai artifact'ı (yayında: https://claude.ai/artifact/EEZAAeYsUN212z1rogUtj8).
  - `ogrenci/SARTNAME.md` — sayfanın tam şartnamesi (db koleksiyonları: konular, bankalar, odevler, denemeler, ayarlar; veli = artifact sahibi).
  - `ogrenci/icerik/_GOREV.md` — PDF'lerden ünite JSON'u çıkarma görevi ve şeması.
  - `ogrenci/icerik/<id>.json` — ünite başına içerik (`<ders kısaltması>-<ünite kısaltması>`). 15 ünite hazır: din-kad, fen-dna, fen-mev, ing-fri, ink-kah, ink-mil, mat-ck, mat-kk, mat-us, tur-cum, tur-fii, tur-man, tur-par, tur-soz, tur-yaz.
  - `ogrenci/index.html` — sayfa kaynağı. Site bir **planlayıcı/koçluk sistemi**: veli girdileri hazırlar, site her gün Duru'ya görev listesi kurar (ayrıntı `ogrenci/SARTNAME.md`).
    - Duru rotaları: `#duru` Programım ("Sıradaki görevin · 2/4" kartı + numaralı, **saatsiz** bugünün listesi; Başla/Bitti ✓/Ertele; seri rozeti, günlük söz, konfeti; "Haftayı göster" kapalı), `#derslerim` (3+3 ders kartı), `#ders-<id>`, `#konu-<id>` (Hatalarım/Alıştırma/Sınav). Plandan "Başla": Hatalarım'da ilk görülmemiş hata kartı açılır, Alıştırma hemen başlar.
    - Veli rotaları (yalnız sahip): `#veli` Hazırlık (Senden beklenenler → Duru'nun bugünü → "+ Ekle" [koç ödevi / okul ödevi·sınav / kaynak kitap / hata yükledim] → kapalı bölümler), `#veli-program` (düzenlenebilir haftalık sabit program takvimi), `#veli-analiz` Rapor (koçluk raporu + eski analiz), `#veli-<dersId>`, `#veli-konu-<id>`.
    - Planlayıcı (`planSimule`): boş zamanı sabit programdan hesaplar; yük sınırı hafta içi 180 / hafta sonu 240 dk (`ayarlar/genel.plan`), 40 dk görev + 10 dk mola; öncelik sınav hazırlığı → koç ödevi (teslime kadar günlere bölünür) → okul/veli ödevi → yeni/eksik hatalar → yanlış tekrarı → kaynak kitap. Bugünün planı `denemeler/gunplan-<tarih>` olarak dondurulur; koç/kaynak değişince kendiliğinden yeniden kurulur. Duru'nun kayıtları `denemeler/gorev-<gid>-<uid>` (`tur:"gorevKayit"`: bitti/ertelendi, cozulen/dogru/yanlis).
    - db `program`: `sabit` (haftalık okul/dershane/etüt/özel/Cambly; `gizli` yemek), `olay` (okul sınavları/ödevler/denemeler, `konuIds`), `hafta-<Pzt>` (haftalık değişiklik/onay), `blok` (velinin sabitlediği görev), `koc`, `kaynak`, `yukleme`. Eski öneri motorunun blokları silindi; `onerildi`/`bos` bloklar yok sayılır.
    - Görünüm: Duru panelinde 3 açık tema (Lavanta varsayılan, Şeftali, Deniz; localStorage `duruCalisma.tema`), karanlık mod yok; veli paneli temasız. Ders renkleri her yerde sabit ve dolu etiket: Türkçe kırmızı, Mat mavi, Fen yeşil, İnkılap amber, Din mor, İng pembe. Sayfa içi ekranlar `history.pushState` ile tarayıcı geri tuşuna bağlı.
  - Hatalarım: alt konu satırları → tek kart (solda soru görseli, sağda doğru cevap/Duru'nun cevabı/hata analizi/doğru yol/tüyo/çözüm), Geri/İleri; alt konunun kısa anlatımı kart altında. Ayrı "Kısa anlatım" sekmesi yok. Alıştırma da satır satır + Geri/İleri. Sınav sonunda karne + "Benzer sorularla yeniden dene".
  - Tamamlanma: görülen hatalar `denemeler/inceleme-<konuId>-<uid>` belgesinde (`tur:"inceleme"`, `gorulen:{anahtar:ISO}`) — bu belgeler `S.denemeler`'den ayrılır, istatistiklere girmez; velinin kayıtları Duru'nun ilerlemesine sayılmaz. Alıştırma: her soru alıştırmada en az bir kez çözülmüş. Sınav: hatalar+alıştırma bittikten sonra bitirilen sınav. Yeni hata/soru gelince ilgili bölüm yeniden "tamamlanmadı" olur.
  - `ogrenci/sorular/` — hata sorularının PDF'ten kesilmiş PNG'leri (`<ASCII kod>.png`) + `detay.json` (kod → gorsel, cevap, senin, cozum, hataAnaliz, tuyo, dikkat). Sayfa bunu `fetch` ile okur (db'ye yazılmaz). Üretici: `scripts/soru_gorsel.py` (içerik JSON'larına da bu alanları ekler).
  - `ogrenci/sira.json` — ünite başına anlatım bölümü / soru altKonu / tüyo → hata alt konusu eşlemesi (Hatalarım sırası tek kaynak). Yeni ünitede elle/Haiku ile eklenir; `icerik/` içine koyma (icerik_hazirla.py oradaki her JSON'u ünite sanar).
  - Artifact slug: `6b2b4a28-e1d5-4d6d-bdb2-7f1dd875075f`. Yayın `publish_files` ile (index.html, sira.json, sorular/*); patch modunda listelenmeyen dosyalar korunur.
- `scripts/icerik_hazirla.py` — ünite JSON'larını artifact db'ye yazılacak `konular`/`bankalar` belgelerine hazırlar.

## Komutlar

```bash
# Excel güncellenince (proje klasöründen) — data/*.json ve data/veri.js yenilenir
python3 -I scripts/xlsx_to_json.py /home/merterk/Belgeler/LGS/LGS_Takip.xlsx data

# Ünite JSON'u doğrula
python3 -I -c "import json,sys;json.load(open(sys.argv[1]))" ogrenci/icerik/<id>.json

# Ünite JSON'larını Çalışma Masası db'sine hazırla (sonra db batch yazımı)
python3 -I scripts/icerik_hazirla.py ogrenci/icerik <çıktı klasörü>

# Hata sorularının görsellerini ve çözüm alanlarını üret (yeni ünite/set sonrası), sonra ogrenci/sorular/* yayımlanır
python3 -I scripts/soru_gorsel.py /home/merterk/Belgeler/LGS ogrenci/icerik ogrenci/sorular

# PDF metni oku (bozuk üs/kesir/şekilde sayfayı Read ile görsel oku, tahmin etme)
pdftotext -layout "<dosya>.pdf" -
```

## Kurallar

- Excel güncellemesinden sonra claude.ai dashboard'u otomatik güncellenmez: değişen JSON'lar artifact'a asset olarak yüklenip `datasets/<id>` belgelerindeki `source.url` ve `updated` güncellenir.
- Soru cevapları mutlaka cevap anahtarından gelir; emin olunmayan sorular `"emin": false` işaretlenir.
- Artifact sayfalarında veri metni `textContent` ile basılır, `innerHTML` ile değil.
- Python scriptleri `-I` ile çalıştırılır.
- Çalışma Masası konu belgeleri yeniden yazılırken `durum`/`veliNotu` ezilmez (update kullan); soru id'leri sabit kalır (denemelerde saklanıyor).
- **Oturum kapanışı:** Kullanıcı "oturumu kapatıyorum" dediğinde o oturumda değişen/öğrenilen her şeye göre bu `CLAUDE.md` ve memory dosyaları (`MEMORY.md` dizini dahil) güncellenir; ardından kullanıcıya **"Projeyi GitHub'a da göndereyim mi?"** diye sorulur; "evet" derse değişiklikler commit'lenip `origin`'e push edilir (sormadan push edilmez). En son ne güncellendiği (ve push yapıldıysa) kısaca söylenip "Güncelledim, kapatabilirsin." denir. Arka plan oturumunda bu değişiklikler `worktree-*` dalına commit'lenir; bu dallar sonraki ana oturumda `main`'e birleştirilir ve kullanıcı onayıyla silinir.
