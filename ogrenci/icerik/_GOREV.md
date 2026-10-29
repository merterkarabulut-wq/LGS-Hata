# İçerik çıkarma görevi (her ünite için bir JSON)

Kaynak klasör: `/home/merterk/Belgeler/LGS/<Ders>/<Ünite>/` içindeki PDF'ler:
- `... - Set N - Benzer Sorular.pdf` → çoktan seçmeli benzer sorular; cevap anahtarı kitapçığın SONUNDA.
- `... - Set N - Çözümler ve Hata Analizi.pdf` → Duru'nun yanlış yaptığı asıl soruların çözümü, "hatan şuydu" (turuncu kutu), kısa yol (mavi kutu), "kısa yollar ve tüyolar" tablosu.
- `... - Konu Özeti.pdf`, `... - Konu Alıştırmaları.pdf` (varsa).
- `... - Tekrar Testi (karışık).pdf` + `... Cevap Anahtarı (veli).pdf` + `... Hata Analizi (veli).pdf` (varsa).
- `... - Set N - Sorular.pdf` = Duru'nun yanlış yaptığı asıl sorular (soru metni lazım olursa).

Metni `pdftotext -layout "<dosya>" -` ile oku. Üslü/kesirli/kareköklü ifadeler, tablolar veya şekiller pdftotext'te bozuluyorsa (ör. üsler ayrı satıra kayıyorsa) ilgili sayfayı Read aracıyla PDF olarak (pages parametresi) görsel oku. Asla tahmin etme.

## Çıktı
Her ünite için tek dosya: `/home/merterk/Belgeler/Projelerim/Duru LGS/ogrenci/icerik/<id>.json` (UTF-8, geçerli JSON). Yazdıktan sonra `python3 -I -c "import json,sys;json.load(open(sys.argv[1]))" <dosya>` ile doğrula.

```json
{
  "id": "mat-us",
  "ders": "Matematik",
  "unite": "02 - Üslü İfadeler",
  "baslik": "Üslü İfadeler",
  "anlatim": [ {"baslik": "Negatif üs", "metin": "2–6 cümlelik, 8. sınıf öğrencisine hitap eden (sen dili) kısa anlatım. Örnek içerebilir."} ],
  "tuyolar": [ "Tek cümlelik kısa yol / tuzak uyarısı" ],
  "hatalar": [
    {"kod": "MAT-ÜS-3", "altKonu": "Negatif üs", "soru": "Sorunun 1 cümlelik özeti", "hata": "Duru'nun yaptığı hata (Çözümler PDF'indeki 'hatan' kısmı)", "dogruYol": "Doğru düşünme yolu, 1–3 cümle"}
  ],
  "sorular": [
    {"id": "mat-us-001", "altKonu": "Negatif üs", "kaynakKod": "MAT-ÜS-3", "tur": "benzer",
     "metin": "Soru metni. Satır sonu için \n kullan.",
     "secenekler": ["A şıkkı metni (harf olmadan)", "B", "C", "D"],
     "dogru": "B", "cozum": "1–3 cümlelik çözüm", "emin": true}
  ]
}
```

Kurallar:
- `anlatim`: Konu Özeti varsa ondan; yoksa Çözümler PDF'indeki tüyolar ve çözümlerden sentezle. Ünitenin Duru'nun hata yaptığı alt konularını kapsayan 3–8 bölüm. Kısa, net, Türkçe.
- `hatalar`: Çözümler ve Hata Analizi PDF'lerindeki HER asıl soru için bir kayıt (kod PDF'teki koddur, ör. MAT-ÜS-3, TUR-SA-2).
- `sorular`: Benzer Sorular kitapçıklarındaki TÜM soruları al (tur "benzer"), Konu Alıştırmaları'ndakileri de (tur "alistirma"), Tekrar Testi'ndekileri de (tur "tekrar"). `dogru` mutlaka cevap anahtarından gelsin. Cevap anahtarı yoksa ve kendin %100 emin değilsen `"emin": false` yaz.
- Şekil/grafik olmadan çözülemeyen soruyu: tablo ise metne düz yazıyla dök; şekil ise kısaca betimle; betimlemek mümkün değilse soruyu ATLA. "Asıl soruya göre" sorulan sorularda asıl sorunun gerekli bilgisini metnin başına ekle.
- Üsler için Unicode üst simge (2⁻³, 10⁵), karekök için √, kesir için a/b kullan. HTML etiketi kullanma.
- Şıklar 4 tane (A–D). 5 şıklıysa olduğu gibi 5 yaz. Şık metninde "A)" gibi harf olmasın.
- `id`: `<ünite id>-<3 haneli sıra>`.
- `cozum`: Varsa cevap anahtarı/çözümden; yoksa kendin kısa yaz.

İş bitince: ünite başına soru sayısı, atlanan soru sayısı ve `emin:false` sayısını raporla. Başka bir dosyaya dokunma.
