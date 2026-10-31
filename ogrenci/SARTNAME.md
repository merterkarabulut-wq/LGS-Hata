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
5. `ayarlar/genel`: `{"lgsTarihi":"2027-06-13"}` (sahip değiştirebilir).

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

## Görünüm 2 — Veli paneli (`#veli`, yalnız `sahip === true`)
Sahip için üstte iki sekme: "Duru'nun Paneli" | "Veli Paneli". Sahip değilse veli sekmesi hiç görünmez ve `#veli` → `#duru`'ya düşer.
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
