"""Test deduplication without assuming that participants.csv is still empty.

The merge() function returns the TOTAL number of unique real sessions after
merging, NOT the number of newly added rows. A student's dataset may already
contain real sessions collected since the example project was packaged.
"""
import csv
import importlib.util
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('primer_merge', ROOT / 'scripts' / 'merge_sessions.py')
merge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge)


def test_merge_deduplicates_and_counts_real_sessions(tmp_path):
    existing = tmp_path / 'oturumlar.csv'
    existing.write_text((ROOT / 'data' / 'oturumlar.csv').read_text(encoding='utf-8'), encoding='utf-8')

    with existing.open(newline='', encoding='utf-8-sig') as f:
        rows_before = list(csv.DictReader(f))
    real_before = {r['session_id'] for r in rows_before if r['kaynak'] == 'gercek'}

    new_session_id = 'test-' + uuid.uuid4().hex
    volunteer = tmp_path / 'participant.csv'
    with volunteer.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=merge.COLUMNS)
        writer.writeheader()
        writer.writerow({
            'session_id': new_session_id,
            'karar_suresi_sn': '10',
            'onceki_hata_sayisi': '0',
            'karar_degistirme_sayisi': '0',
            'sahne_zorlugu': '2',
            'tereddut_suresi_sn': '2',
            'yardim_etkisi': '1',
            'kaynak': 'gercek',
        })

    # Sending the same file twice must add the single new decision just once.
    total_sessions = merge.merge([volunteer, volunteer], existing)
    assert total_sessions == len(real_before) + 1

    with existing.open(newline='', encoding='utf-8-sig') as f:
        rows_after = list(csv.DictReader(f))
    assert len(rows_after) == len(rows_before) + 1
    assert sum(r['session_id'] == new_session_id for r in rows_after) == 1

    # Importing the same file again must not duplicate the decision or session.
    assert merge.merge([volunteer], existing) == total_sessions
    with existing.open(newline='', encoding='utf-8-sig') as f:
        rows_final = list(csv.DictReader(f))
    assert rows_final == rows_after
