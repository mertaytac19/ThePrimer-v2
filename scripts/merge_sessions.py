"""Combine downloaded, consented participant CSVs without inventing real sessions.

Usage (PowerShell): python scripts/merge_sessions.py "data/collected/*.csv"
"""
import argparse
import csv
import glob
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'oturumlar.csv'
COLUMNS = ['session_id', 'karar_suresi_sn', 'onceki_hata_sayisi', 'karar_degistirme_sayisi',
           'sahne_zorlugu', 'tereddut_suresi_sn', 'yardim_etkisi', 'kaynak']


def rows_from(path):
    with open(path, newline='', encoding='utf-8-sig') as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or set(reader.fieldnames) != set(COLUMNS):
            raise ValueError(f'{path}: beklenen CSV sütunları yok/fazla.')
        return [validate(row, path) for row in reader]


def validate(r, origin):
    if not r['session_id'].strip():
        raise ValueError(f'{origin}: oturum ID boş.')
    if r['kaynak'] not in ('synthetic', 'gercek'):
        raise ValueError(f'{origin}: geçersiz kaynak {r["kaynak"]}')
    numbers = COLUMNS[1:-1]
    try: values = {k: float(r[k]) for k in numbers}
    except (ValueError, TypeError) as e: raise ValueError(f'{origin}: sayı hatası {e}') from e
    if not all(math.isfinite(n) and n >= 0 for n in values.values()):
        raise ValueError(f'{origin}: negatif/NaN/inf değer var.')
    if values['yardim_etkisi'] not in (0, 1) or not (1 <= values['sahne_zorlugu'] <= 5):
        raise ValueError(f'{origin}: etiket veya zorluk geçersiz.')
    if values['tereddut_suresi_sn'] > values['karar_suresi_sn'] + .05:
        raise ValueError(f'{origin}: tereddüt karar süresini aşıyor.')
    return {k: str(r[k]) for k in COLUMNS}


def merge(files, output=OUT):
    if not files:
        raise ValueError('Hiç CSV dosyası seçilmedi.')
    records = rows_from(output) if output.exists() else []
    seen = {(r['session_id'], r['karar_suresi_sn'], r['yardim_etkisi'], r['sahne_zorlugu']) for r in records}
    added = 0
    for source in files:
        for record in rows_from(source):
            if record['kaynak'] != 'gercek':
                raise ValueError(f'{source}: İçe alınan kullanıcı oturumları gercek olmalı; sentetik veri gerçek gibi gösterilemez.')
            key=(record['session_id'], record['karar_suresi_sn'], record['yardim_etkisi'], record['sahne_zorlugu'])
            if key not in seen:
                records.append(record);seen.add(key);added+=1
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():
        backup=output.with_suffix('.csv.bak')
        backup.write_bytes(output.read_bytes())
    with open(output, 'w', newline='', encoding='utf-8') as fh:
        writer=csv.DictWriter(fh,fieldnames=COLUMNS)
        writer.writeheader();writer.writerows(records)
    real_sessions={r['session_id'] for r in records if r['kaynak']=='gercek'}
    print(f'Eklendi: {added} karar. Toplam gerçek oturum: {len(real_sessions)}/15.')
    print(f'Güncellendi: {output}')
    if len(real_sessions)<15:
        print('UYARI: Hoca için 15 gerçek oturum koşulu henüz tamamlanmadı.')
    return len(real_sessions)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('patterns',nargs='+',help='CSV yolları veya tırnak içinde wildcard: data/collected/*.csv')
    p.add_argument('--out',type=Path,default=OUT)
    args=p.parse_args()
    paths=sorted({Path(f) for pat in args.patterns for f in glob.glob(pat)})
    merge(paths,args.out)

if __name__=='__main__':main()
