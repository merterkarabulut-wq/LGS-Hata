# "Duru'nun Çalışma Masası" — sayfa şartnamesi

Tek dosya: `/home/merterk/Belgeler/Projelerim/Duru LGS/ogrenci/index.html`. claude.ai Artifact olarak yayımlanacak (tek HTML; kütüphane yok, saf JS). Tüm arayüz metinleri Türkçe.

## Sayfa sözleşmesi (zorunlu)
- `<!doctype>`, `<html>`, `<head>`, `<body>` YAZMA; dosya `<title>Duru'nun Çalışma Masası</title>`, `<meta name="claude:viewport-fit-sides" content="cover">`, Google Fonts `<link>`, `<style>` ile başlar, sonra içerik ve `<script>`.
- Yan boşluk dış sarmalayıcıda: `padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));` dikey için `padding-block`.
- Sadece Google Fonts dışa bağlantı. `alert/confirm/prompt` çalışmaz: onaylar sayfa içi.
- Tema: tüm renkler `:root` token; koyu tema `@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){...;color-scheme:dark}}` ve `:root[data-theme="dark"]{...aynı...}`. `body{background:var(--bg);color:var(--fg)}`.
- 400px telefon genişliğinde çalışmalı; yatay sayfa kaydırması yok. Görünür klavye odağı, `prefers-reduced-motion`.
- Rota hash ile: `#duru` (varsayılan), `#veli`, `#konu-<id>` gibi sade adlar (yalnız harf/rakam/tire). `settings`, `downloads` gibi ayrılmış adları kullanma.
- Veri değerleri güvenilmez metin: `textContent` kullan, `innerHTML` ile veri basma (kendi sabit şablon HTML'in hariç).
- localStorage yalnız devam eden sınav taslağı ve son sekme için; her erişim try/catch.

## Tasarım yönü
Konu: LGS'ye hazırlanan 8. sınıf öğrencisi. Kimlik: "optik form + ders defteri". Serin kâğıt beyazı zemin (hafif mavi), lacivert mürekkep metin, vurgu rengi mürekkep mavisi; konu dışı süs yok. Konuya özgü ayrıntı: şıklar LGS optik formundaki gibi yuvarlak A/B/C/D baloncukları (açık somon/pembe çizgili daire, seçilince dolar). Tüyolar fosforlu kalem sarısı vurgulu. Ders başına bir renk etiketi (Türkçe, Matematik, Fen, İnkılap, Din, İngilizce) — her iki temada okunur.
Fontlar: başlık "Bricolage Grotesque" (600–700), gövde "Atkinson Hyperlegible" (400/700); ikisi de Türkçe karakter destekler; yedek yığın ver. Rakamlarda `font-variant-numeric: tabular-nums`. Krem zemin + terracotta, mor-mavi gradyan, emoji bölüm işaretleri, her şeye aynı gölge/radius KULLANMA. `:root` içinde tasarım planı yorum satırı + 4–6 renk token + font token'ları.
Yükleme anında sayfa boş görünmesin: veri gelene kadar "Konular yükleniyor…" gibi tasarlanmış boş durum; veri yoksa "Henüz konu eklenmedi" açıklaması.

## Yetenekler ve veri (claude.use)
Yayın bildirimi: `capabilities: {db:{rules:[{path:"",read:"view",write:"owner"},{path:"denemeler",read:"view",write:"interact"},{path:"data/users/{self}",write:"interact"}]}, user:{scopes:["profile"]}}`.
```js
const db = await claude.use("db");     // null olabilir → "Bu görünümde veri açılamıyor" mesajı
const user = await claude.use("user"); // null olabilir
const sahip = await user?.isOwner() ?? false;   // VELİ = sahip. canEdit KULLANMA (Duru da düzenleyici olabilir)
const uid = await user?.id();
```
`window.claude` yalnız `use` içerir; başka üyesine dokunma. Her koleksiyona BİR KEZ abone ol (onSnapshot), render içinde abone olma. Aynı belgeye aynı anda tek yazma. Hata kodu `invalid_argument` → kullanıcıya "Kaydedilemedi: bu işlem için yetkin yok" vb.

### Koleksiyonlar
1. `konular/<konuId>` (Claude doldurur; sahip `durum`, `veliNotu` alanlarını günceller):
```json
{"id":"mat-us","ders":"Matematik","unite":"02 - Üslü İfadeler","baslik":"Üslü İfadeler","sira":2,
 "durum":"calisiyor",  // "calisiyor" | "tekrar" | "tamamlandi"
 "veliNotu":"", "durumTarihi":"2026-10-29T...",
 "anlatim":[{"baslik":"...","metin":"..."}], "tuyolar":["..."],
 "hatalar":[{"kod":"MAT-ÜS-3","altKonu":"...","soru":"...","hata":"...","dogruYol":"..."}],
 "soruSayisi": 42}
```
2. `bankalar/<konuId>` (veya çok büyükse `<konuId>-2`): `{"konuId":"mat-us","sorular":[{"id":"mat-us-001","altKonu":"...","kaynakKod":"MAT-ÜS-3","tur":"benzer|alistirma|tekrar","metin":"...","secenekler":["..","..","..",".."],"dogru":"B","cozum":"...","emin":true}]}`. Konu açılınca `db.collection("bankalar").where("konuId","==",id).get()` ile yükle, önbellekte tut, birden çok belgeyi birleştir. Metinlerde `\n` → `white-space: pre-line`. Şık sayısı 4 veya 5 olabilir.
3. `odevler/<otoId>` (yalnız sahip yazar): `{"konuId","baslik","not","soruIds":[...],"olusturma":ISO,"sureDk":number|null,"iptal":false}`.
4. `denemeler/<otoId>` (Duru ve sahip yazar): `{"konuId","odevId":null|id,"tur":"alistirma"|"sinav"|"odev","soruIds":[...],"cevaplar":{"<soruId>":"A"|null},"dogru":n,"yanlis":n,"bos":n,"sureSn":n,"baslangic":ISO,"bitis":ISO,"kullanici":uid,"veliDenemesi":sahip}`. Ödev tamamlandı sayılır = o odevId'li bir deneme varsa. Denemeler koleksiyonu tümüyle (orderBy bitis desc, limit 500) bir kez dinlenir.
5. `ayarlar/genel`: `{"lgsTarihi":"2027-06-13","plan":{...}}` (sahip değiştirebilir; `plan` için "Program, planlayıcı ve koçluk sistemi" bölümüne bak). `program` ve yeni `denemeler` türleri (gunPlan, gorevKayit) aynı bölümde.

## Görünüm 1 — Duru'nun Paneli (`#duru`, herkes)
- Üst şerit: "Merhaba Duru", LGS'ye kalan gün (ayarlar/genel), bu hafta çözdüğü soru sayısı ve doğru oranı.
- "Sana verilen tekrar çalışmaları": iptal edilmemiş ve tamamlanmamış ödevler (konu, başlık, veli notu, soru sayısı, "Başla" düğmesi). Yoksa sakin bir "Bekleyen ödevin yok" satırı.
- Dersler: ders başlıkları altında konu kartları. Kart: konu adı, durum rozeti (Çalışıyor / Tekrar et — veli istedi / Tamamlandı ✓), hata sayısı, son sınav skoru, ilerleme çubuğu (son 3 denemenin doğru oranı). Tamamlananlar ders içinde en sonda ve soluk.
- Konu sayfası (`#konu-<id>`), sekmeler:
  a. **Hatalarım** — `hatalar` listesi: altKonu etiketi, soru özeti, "Ne oldu?" (hata), "Doğru yol" (dogruYol). altKonu'ya göre grupla ve en çok hata olan altKonu'yu üstte göster. Ayrıca kendi denemelerinde yanlış yaptığı sorular (bankadan, en sonuncular) "Sınavlarda kaçırdıkların" altında: soru, onun cevabı, doğru cevap, çözüm.
  b. **Kısa anlatım** — `anlatim` bölümleri + `tuyolar` (fosforlu vurgu kutusu). veliNotu varsa en üstte "Babandan not" kutusu.
  c. **Alıştırma** — altKonu filtresi (çipler, "Hepsi" dahil). Sorular tek tek; şık seçilince anında doğru/yanlış + çözüm gösterilir, "Sonraki". Oturum sonunda (veya "Bitir") deneme `tur:"alistirma"` olarak kaydedilir (en az 1 cevap varsa). Öncelik: daha önce yanlış yapılan ve hiç görülmemiş sorular.
  d. **Sınav** — soru sayısı seçimi (10 / 15 / 20, banka küçükse hepsi), isteğe bağlı süre (soru başına 1.5 dk göstergesi, süre bitince otomatik bitir). Soru seçimi: %50 daha önce yanlış yapılan/boş bırakılan, kalanı hiç görülmemiş, sonra rastgele; karıştır. Optik form gibi gezinti: alt kısımda soru numaraları ızgarası (cevaplanan dolu), önceki/sonraki, "Sınavı bitir" (sayfa içi onay: "3 boş soru var, bitirelim mi?"). Bitince sonuç ekranı: doğru/yanlış/boş, net (doğru − yanlış/3, LGS kuralı), süre, altKonu bazlı tablo, yanlışların listesi (senin cevabın / doğru cevap / çözüm). Deneme `tur:"sinav"` kaydedilir.
  e. Ödev çözme: aynı sınav motoru, sorular `odev.soruIds`, `tur:"odev"`, `odevId`.
- `emin:false` sorular normal gösterilir ama sonuç ekranında "cevap anahtarı kontrol ediliyor" notu düşülür.
- Devam eden sınav localStorage'a (`duruCalisma.taslak`) yazılır; sayfa yeniden açılınca "Yarım kalan sınavın var: devam et / sil".
- `window.claude?.hot?.snapshot(() => durum)` ve `window.claude?.hot?.ready ? window.claude.hot.ready(start) : start(window.claude?.hot?.data ?? {})` ile açık sınav durumunu yeni sürüme taşı.

## Görünüm 2 — Veli paneli (`#veli`, `#veli-program`, `#veli-analiz`; yalnız `sahip === true`)
Sahip için üstte iki sekme: "Duru'nun Paneli" | "Veli Paneli". Sahip değilse veli sekmesi hiç görünmez ve veli rotaları `#duru`'ya düşer. Sayfanın Hazırlık/Program/Rapor sekmeleri aşağıda; bu bölümdeki özet/konu tablosu/ödev verme Rapor sekmesindedir.
- Özet satırı: son 7 günde deneme sayısı, çözülen soru, doğru oranı, bekleyen ödev sayısı, "tekrar" durumundaki konu sayısı.
- "Son etkinlik": son 15 deneme (tarih-saat, konu, tür, D/Y/B, net, süre; veli denemesi ise "(senin denemen)" etiketi; kişi adı `user.profiles([...ids])` ile, `name || "Biri"`).
- Konu tablosu (ders bazlı gruplu): konu, durum, deneme sayısı, son skor, son 5 denemenin mini çubuk grafiği (SVG, `viewBox`, `width="100%"`, token renkleri), en zayıf altKonu, işlemler.
- Konu detay paneli (satıra tıklayınca açılır):
  - altKonu bazlı başarı (yatay çubuklar: doğru/toplam, %), en çok yanlış yapılan sorular (soru metni kısaltılmış, kaç kez yanlış, işaretlediği şıklar, doğru şık).
  - **Tekrar çalışması oluştur**: öneri listesi = yanlış/boş yapılmış sorular + zayıf altKonu'lardan görülmemiş sorular; her biri onay kutulu (varsayılan seçili ilk 10), başlık (varsayılan "<Konu> – Tekrar <tarih>"), not alanı, süre (isteğe bağlı dk). Kaydet → `odevler.add(...)` ve konu `durum:"tekrar"` (`update`). Sayfa içi onay mesajı "Ödev Duru'ya gönderildi".
  - **Konuyu tamamlandı işaretle** → `durum:"tamamlandi"`, `durumTarihi`. **Yeniden aç** → `"calisiyor"`.
  - **Veli notu** (textarea + Kaydet) → `veliNotu`.
  - Bu konunun ödevleri: durum (bekliyor/tamamlandı + sonucu), "İptal et" (iptal:true).
- Ayarlar: LGS tarihi (date input + Kaydet).

## Kalite
- Ağ/izin hatalarında anlaşılır Türkçe mesaj; `quota_exceeded` mesajı.
- Tüm butonlar gerçek `<button>`, form alanlarına sabit `id`.
- Kod okunur: küçük fonksiyonlar, tek `render()` durumu çizer; abonelikler yalnız başlangıçta.
- Bitince `node --check` için script içeriğini ayrı bir geçici dosyaya çıkarıp sözdizimi kontrolü yap (`/home/merterk/.claude/jobs/085381a2/tmp/` altında). Başka dosyaya dokunma.

## Program, planlayıcı ve koçluk sistemi

Veli girdileri hazırlar (sabit program, sınavlar, koç ödevleri, okul ödevleri, kaynak kitaplar, yeni hata yüklemesi); site her gün Duru için bir **görev listesi** kurar ve "şimdi ne yapmalıyım"ı söyler. Yük sınırı aşılmaz, iş teslim tarihine kadar günlere yayılır, yapılmayan iş ertesi güne kayar, yetişmeyecekse veliye uyarı çıkar.

### Rotalar ve sekmeler (`panelSekmeleri(rol, aktif)`)
- Duru: **Programım** `#duru` (varsayılan: selam + LGS'ye kalan gün, "Sıradaki görevin" kartı [üstte "2 / 4" sırası ve "~40 dk" süresi; Başla / Bitti ✓ / Ertele], bugünün listesi [numaralı, saatsiz; üstte soluk "Bugün: Okul 08:00–16:30 · Etüt …" satırı — sabit dersler ve günün olayları listeye girmez], yaklaşanlar, kapalı "Haftayı göster" takvimi, bu haftanın koç ilerlemesi) ve **Derslerim** `#derslerim` (`#ders-<id>`, `#konu-<id>` bu sekmeye aittir). Programım'dan "Başla" ile konu sayfasına gelince "◀ Programıma dön" (`S.programdanGeldi`).
- Veli (yalnız sahip, aksi `#duru`): **Hazırlık** `#veli` | **Program** `#veli-program` | **Rapor** `#veli-analiz` (`#veli-<dersId>`, `#veli-konu-<id>` Rapor'a aittir). Eski `#program` → `#duru`.

### Veri
`program` koleksiyonu (yalnız veli yazar; `tur` belirler):
- `sabit` (haftalık ders), `olay` (sınav/ödev/deneme: `tarih, saat, kategori, ders, baslik, konular, konuIds, uniteler, not`), `hafta` (id `hafta-<Pazartesi>`: `degisiklik`, `ekstra`, `onaylandi`) — değişmedi. Duru'nun eski `denemeler/olay` belgeleri okunur.
- `blok` — velinin elle **sabitlediği görev**: `tarih, bas, bit, is:{tip, konuId?, konuAd?, odevId?, soruAdet?, kocId?}, baslik, ders, not`. Planlayıcı bunlara dokunmaz; günün planına aynen girer ve yüke sayılır. Eski öneri motorunun yazdığı bloklar (`onerildi:true` ya da `is.tip:"bos"`) geçersizdir: `blokEski(b)` ile `S.program.eskiBlok`'a ayrılır, hiçbir yerde gösterilmez/sayılmaz. Boş kutu otomatiği ve "Planı hazırla" önerisi yoktur.
- `koc` — koç ödevi: `{ders, konu, konuId?, soruAdet, baslangic, teslim, not, olusturma}`.
- `kaynak` — kaynak kitap: `{ders, ad, aktif, olusturma}`.
- `yukleme` — id `yukleme-<ts>`: yeni hatalı soru yüklemesi bildirimi `{tarih, not, durum:"bekliyor"|"islendi", olusturma}`.

`denemeler` koleksiyonu (Duru da yazar; `S.denemeler` filtresi bu türleri deneme saymaz; her tür için ayrı `where("tur","==",X)` aboneliği):
- `gunPlan` — id `gunplan-<YYYY-MM-DD>`: günün dondurulmuş planı `{tarih, gorevler:[{gid, bas, bit, tip, baslik, ders, neden, konuId?, kocId?, odevId?, olayId?, kaynakId?, blokId?, soruAdet?}], olusturan, olusturma}`. Bugünün planı yoksa sayfayı açan (Duru ya da veli) kurar; yalnız bugün yazılır, ileri günler canlı hesaplanır.
- `gorevKayit` — id `gorev-<gid>-<uid>`: `{gid, tarih, tip, ders, kocId?, kaynakId?, konuId?, durum:"bitti"|"ertelendi", cozulen?, dogru?, yanlis?, sureDk?, kullanici, veliDenemesi, zaman}`. `veliDenemesi:true` Duru'nun ilerlemesine sayılmaz. Geri alma = belgeyi sil.
- `planIsaret` (eski blok işareti; sabit bloklar için), `olay`, `inceleme` aynen.

`ayarlar/genel`: `{lgsTarihi, plan:{haftaIciDk:180, haftaSonuDk:240, blokDk:40, araDk:10, soruBlok:20}}` (`planAyar()` varsayılanlarla birleştirir; sahip yazar).

### Görev tipleri
`IS_TIP`: koc, kaynak, okulOdevi, sinavCalisma, hatalar, alistirma, yanlislar, sinav, odev (+ sabit blok tipleri). Sitede yapılanlar (hatalar, alistirma, yanlislar, sinav, odev): "Başla" ilgili ekrana götürür; tamamlanma kendiliğinden algılanır (`blokOtomatik`) ya da "Bitti". Diğerlerinde "Başla" süre sayacı başlatır (localStorage `duruCalisma.aktifGorev`), "Bitti" koç/kaynak/soru için "Kaç soru çözdün? / Doğru / Yanlış" formunu açar. `gorevDurum(g, tarih)`: bitti | ertelendi | simdi (sayaç açık) | sirada (bekliyor) | yarina (geçmiş gün, kayıt yok = "yarına kaldı"). "kacti" yoktur; Duru ekranında saat/kırmızı durum gösterilmez (etiketler: Yapıldı ✓ yeşil, Ertelendi turuncu, Şu an çalışıyorsun mavi, Bekliyor gri). Görevlerin `bas`/`bit` alanları yalnız sıralama ve kapasite için tutulur. Sıradaki görev = listede bitti/ertelendi olmayan ilk görev (aktif sayaç ya da `S.seciliGorev` "Öne al" ile öne geçer).

### Planlayıcı kuralları (`planSimule(baslangic, gunSayisi)`, saf fonksiyon; yazanlar `gunPlanKur`, `gunPlanYenile`, `gorevKaydet`)
- Çalışma penceresi: hafta içi 17:30, hafta sonu 10:00 – 23:00; sabit ders/olay/blok `mesgulAraliklar` ile düşülür (dış derslerden sonra 30 dk tampon); bugün için şu andan sonrası. Yuvalar `blokDk`, aralarında `araDk`.
- Kapasite = min(yuva sayısı, günlük süre / blokDk); ertesi gün sınav varsa +1 blok. Sabit bloklar önce yerleşir ve kapasiteden düşer.
- Öncelik: (1) sınav hazırlığı (sınavdan 1–3 gün önce: hatalar, yanlislar, sinav, sinavCalisma), (2) koç ödevleri — kalan = soruAdet − Duru'nun bitti kayıtlarındaki çözülen; kalan günlere eşit yayılır (pay = ceil(kalan/kalanGün), bloklar `soruBlok`), `baslangic`'tan önce planlanmaz; teslim geçtiyse/yetmiyorsa `yetismeyen`, (3) okul ödevleri (7 gün içinde, teslimden önceki uygun gün), (4) velinin verdiği site ödevleri, (5) yeni içerik/eksik bölümler (günde en çok 2), (6) yanlışlar tekrarı (günde en çok 1, son çalışmadan ≥3 gün sonra), (7) kaynak kitap dolgusu (günde en çok 1, aktif kaynaklar arasında dönüşümlü).
- Bugün dondurulmuşsa 0. gün dondurulmuş görevlerdir; ertelenen/kaçan iş kalan hesabından doğal olarak sonraki günlere düşer.
- `gunPlanYenile` (yalnız veli): yalnız bitti/ertelendi kaydı olan görevleri tutar; bekleyenler (saati geçmiş olsa da) yeniden hesaplanır.
- Hatırlatma (`hatirlatKontrol`, Programım açıkken 30 sn'de bir render): görev başına değil, gün başına tek kez — günün ilk görevinin (gizli) başlangıç saati gelmiş ve henüz hiçbir görev bitmemişse "Bugün N görevin var, ilki: …" bildirimi + başlığa "⏰" + kısa bip (`S.hatirlatilan` "gun-<tarih>"). Gün geçince kaydı olmayan görevler "yarına kaldı" sayılır; iş kalandan hesaplandığı için planlayıcı sonraki günlere dağıtır.

### Veli · Hazırlık (`#veli`, `hazirlikSayfasi`)
Tek sütun, ~900 px ortalı (`.hz-tek`). Sıra: **Senden beklenenler** (eski Uyarılar: yetişmeyen işler, geride koç ödevi [beklenen doğrusal − çözülen ≥ soruBlok], son 7 günde ≥3 yarına kalan/ertelenen, 14 gün içinde konusuz sınav ["Konuları seç"], bekleyen yükleme başına "İşlendi ✓", haftalık `kontrolKarti`; yoksa "Her şey yolunda ✓") · **Duru'nun bugünü** (numaralı saatsiz liste, Yapıldı/Ertelendi/Bekliyor, "N / M yapıldı", "Bugünün planını yeniden kur") · **+ Ekle çubuğu** (Koç ödevi · Okul ödevi / sınav · Kaynak kitap · Hata yükledim; bir anda yalnız bir form, çubuğun altında açılır, Vazgeç/kayıtla kapanır — `ekleAcik()`/`ekleAc()`; koç ve olay formu `S.hz.koc`/`S.hz.olay`, diğerleri `S.hz.ekleKaynak`/`ekleYuk`) · kapalı başlayan `<details>` bölümleri, özetlerinde sayılar: "Koç ödevleri · 2 aktif · 1 geride", "Sınavlar ve okul ödevleri · 30 gün içinde 6", "Kaynak kitaplar · 2 aktif", "Önümüzdeki 7 gün" (günlük yük çubuğu, saatsiz görev listesi), "Plan ayarları" (haftaIciDk, haftaSonuDk, soruBlok). İçerikleri eski kartların listeleri (düzenle/sil aynen). Açık/kapalı durum `S.hz.acik` (Set) + `ontoggle` ile render'lar arasında korunur (`hzDetay`).

### Veli · Program (`#veli-program`, `programSayfasi(true)`)
Kontrol kartı, hafta araç çubuğu, renk açıklaması, düzenlenebilir hafta takvimi (planlayıcının tahmini görevleri kesikli kenarlı gösterilir). Takvimden ekleme/düzenleme: sabit ders (yalnız bu hafta / her hafta), sınav/ödev/deneme (ders + ünite kutucukları), çalışma bloğu (sabitlenen görev); "Değiştir", onaylı "Sil" (blok belgesi silinir), "Bu hafta yok", "Sonraki saatleri de kaydır". Taslaklar `S`'te (`takvimDuzen`, `blokDuzen`, `gunEkle`, `hz`); tek seferde bir form açık (`formlariKapat`).
Değişken dersler: `sabit.degisken:true` etiketi; haftalık kontrol: hedef hafta Cuma–Pazar gelecek hafta, aksi bu hafta; `kontrolKarti` "Değişiklik yok, aynen devam ✓" (`hafta-<key>.onaylandi`) ya da "Takvimde değiştir".

### Veli · Rapor (`#veli-analiz`)
Üstte **Koçluk raporu** (Bu hafta / Geçen hafta): planlanan/yapılan/ertelenen/yarına kalan görev, plan uyumu (bekleyenler hariç), çalışma süresi (sureDk toplamı); ders ders çözülen/doğru/yanlış/oran tablosu; haftaya düşen koç ödevi ilerlemesi; sitedeki çalışmalar (görülen hata, alıştırma, sınav, ortalama başarı); kurala dayalı kısa yorumlar. Altında mevcut Analiz (özet kutuları, son etkinlik, dersler, ayarlar).

## Görünüm (temalar, seri, günlük söz, konfeti)

- Üç tema: Lavanta (varsayılan), Şeftali, Deniz. `render()` her çizimde `<html data-tema>` koyar; seçim localStorage `duruCalisma.tema`. Yalnız Duru'nun panelinde geçerli; `#veli…` rotalarında nitelik kaldırılır ve sade açık renkler (turuncu veli vurgusu) kalır. Ders renkleri (`--c-*`) ve ok/bad renkleri temalardan bağımsızdır.
- Karanlık mod yoktur (site her zaman açık tema). Vurgu renkleri WCAG AA için önizlemeye göre biraz koyulaştırıldı (lavanta #6f42bf, şeftali #b73d28, deniz #0b6b7c).
- Selamlama satırında "🎨 Görünüm" düğmesi üç renkli seçeneği açar (`aria-pressed`). Seri rozeti "🔥 N gündür planındasın" (N ≥ 2): planı ve en az bir "bitti" görevi olup bekleyen/yarına kalan görevi olmayan günler; plansız günler atlanır, bugün bitmediyse seri dünden sayılır (en çok 60 gün). Veli "Duru'nun bugünü" başlığında küçük rozet.
- Selamlamanın altında yılın gününe göre sabit günlük söz (30 cümle). "Bugünlük bitti" durumuna geçişte gün başına bir kez konfeti (`duruCalisma.konfeti` = tarih; body'de fixed katman, 3 sn sonra silinir; `prefers-reduced-motion` ise yok).
