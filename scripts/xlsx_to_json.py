"""LGS_Takip.xlsx dosyasını dashboard'un okuduğu JSON dosyalarına çevirir.

Kullanım: python3 -I scripts/xlsx_to_json.py <LGS_Takip.xlsx> <çıktı klasörü>
Yalnızca standart kütüphane kullanır (openpyxl gerekmez).
"""
import importlib.util, json, re, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
AYLAR = {'Oca': 1, 'Şub': 2, 'Mar': 3, 'Nis': 4, 'May': 5, 'Haz': 6,
         'Tem': 7, 'Ağu': 8, 'Eyl': 9, 'Eki': 10, 'Kas': 11, 'Ara': 12}
# Tekrar sayfasında ders adları kısaltılmış; diğer sayfalarla aynı adlara çevrilir.
DERS = {'Fen': 'Fen Bilimleri', 'Din': 'Din Kültürü ve Ahlak Bilgisi',
        'İnkılap': 'T.C. İnkılap Tarihi ve Atatürkçülük'}


def read_sheets(path):
    z = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(NS + 'si'):
            shared.append(''.join(t.text or '' for t in si.iter(NS + 't')))
    names = re.findall(r'<sheet name="([^"]+)"', z.read('xl/workbook.xml').decode())
    sheets = {}
    for i, name in enumerate(names, 1):
        rows = []
        for row in ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).iter(NS + 'row'):
            cells = {}
            for c in row.findall(NS + 'c'):
                col = re.match(r'[A-Z]+', c.get('r')).group()
                v = c.find(NS + 'v')
                if c.get('t') == 'inlineStr':
                    val = ''.join(t.text or '' for t in c.iter(NS + 't'))
                elif c.get('t') == 's' and v is not None:
                    val = shared[int(v.text)]
                elif v is not None:
                    val = v.text
                else:
                    val = ''
                cells[col] = val.strip()
            rows.append(cells)
        sheets[name] = rows
    return sheets


def table(rows, keys):
    cols = 'ABCDEFGHIJ'[:len(keys)]
    return [{k: r.get(c, '') for k, c in zip(keys, cols)}
            for r in rows[1:] if any(r.get(c) for c in cols)]


def tr_date(text):
    m = re.search(r'(\d{1,2}) (' + '|'.join(AYLAR) + r') (\d{4})', text)
    if m:
        return f'{m[3]}-{AYLAR[m[2]]:02d}-{int(m[1]):02d}'
    m = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', text)
    return f'{m[3]}-{m[2]}-{m[1]}' if m else None


def durum(text):
    t = text.lower()
    if t.startswith('doğru'):
        return 'doğru'
    if t.startswith('yanliş') or t.startswith('yanlış') or text.startswith('YANLIŞ'):
        return 'yanlış'
    return 'bekliyor'


def main(src, out):
    s = read_sheets(src)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    uniteler = table(s['Üniteler'], ['ders', 'unite', 'son_set', 'setler', 'hatali_soru', 'konu_ozeti', 'siradaki_set'])
    for u in uniteler:
        u['hatali_soru'] = int(u['hatali_soru'] or 0)
        u['konu_ozeti'] = u['konu_ozeti'] == 'Evet'

    setler = table(s['Setler'], ['ders', 'unite', 'set', 'tarih', 'kaynak', 'icerik', 'soru_sayisi', 'soru_kodlari'])
    for i, r in enumerate(setler, 1):
        r['no'] = i
        r['tarih_metin'] = r['tarih']
        r['tarih'] = tr_date(r['tarih'])
        r['soru_sayisi'] = int(r['soru_sayisi'] or 0)

    tekrar = table(s['Tekrar'], ['kod', 'ders', 'konu', 't1', 't1_sonuc', 't2', 't2_sonuc'])
    for r in tekrar:
        r['ders'] = DERS.get(r['ders'], r['ders'])
        r['t1_tarih'], r['t2_tarih'] = tr_date(r['t1']), tr_date(r['t2'])
        r['t1_durum'], r['t2_durum'] = durum(r['t1_sonuc']), durum(r['t2_sonuc'])

    kaynaklar = table(s['Kaynaklar'], ['yukleme', 'tarih', 'islendi', 'setler', 'not'])
    for i, r in enumerate(kaynaklar, 1):
        r['no'] = i
        r['tarih_metin'] = r['tarih']
        r['tarih'] = tr_date(r['tarih'])

    for name, rows in [('uniteler', uniteler), ('setler', setler), ('tekrar', tekrar), ('kaynaklar', kaynaklar)]:
        (out / f'{name}.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1))
        print(name, len(rows))

    # Dashboard'un okuduğu data/veri.js de güncellenir (-I altında betik klasörü sys.path'te olmadığından yol ile yüklenir).
    spec = importlib.util.spec_from_file_location('veri_js', Path(__file__).with_name('veri_js.py'))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    modul.main(out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
