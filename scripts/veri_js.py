"""data/*.json dosyalarını dashboard'un yüklediği tek bir data/veri.js dosyasında toplar.

Tarayıcı, dosyadan (file://) açılan sayfada JSON'u fetch ile okuyamadığı için
veri bir <script> olarak yüklenir.
Kullanım: python3 -I scripts/veri_js.py <veri klasörü>
"""
import json, sys
from datetime import datetime
from pathlib import Path

ADLAR = ['uniteler', 'setler', 'tekrar', 'kaynaklar']


def main(klasor):
    klasor = Path(klasor)
    veri = {ad: json.loads((klasor / f'{ad}.json').read_text()) for ad in ADLAR}
    veri['guncelleme'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    (klasor / 'veri.js').write_text(
        '// Otomatik üretilir: scripts/veri_js.py — elle düzenlemeyin.\n'
        'window.LGS_VERI = ' + json.dumps(veri, ensure_ascii=False) + ';\n')
    print('veri.js', ', '.join(f'{ad} {len(veri[ad])}' for ad in ADLAR))


if __name__ == '__main__':
    main(sys.argv[1])
