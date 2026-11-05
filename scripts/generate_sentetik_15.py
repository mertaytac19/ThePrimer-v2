"""The Primer v2: 15 reproducible, clearly SYNTHETIC sample sessions.

Creates 15 distinct game sessions x 8 scene decisions (120 decision rows).
The labels are simulated, NOT reports from human participants.
No private data is generated or collected.
"""
import csv
import math
import random
import uuid
from pathlib import Path

SEED = 20261105
NUM_SESSIONS = 15
DIFFICULTIES = [1, 2, 3, 3, 4, 3, 5, 5]
FIELDS = [
    'session_id', 'karar_suresi_sn', 'onceki_hata_sayisi',
    'karar_degistirme_sayisi', 'sahne_zorlugu', 'tereddut_suresi_sn',
    'yardim_etkisi', 'kaynak',
]

# Persona names are internal generator parameters, not personal identifiers.
PERSONAS = [
    ('fast_confident', 0.72, -0.9, -0.20),
    ('careful_skilled', 1.12, -0.6, -0.10),
    ('quick_uncertain', 0.79, 0.65, 0.50),
    ('slow_beginner', 1.54, 1.05, 0.90),
    ('balanced', 1.00, 0.0, 0.0),
]


def make_rows():
    rng = random.Random(SEED)
    rows = []
    for session_idx in range(NUM_SESSIONS):
        profile_name, time_mult, skill_bias, hesitation_bias = PERSONAS[session_idx % len(PERSONAS)]
        # Stable anonymous synthetic identifier: never label as a real session.
        sid = str(uuid.uuid5(uuid.NAMESPACE_URL, f'theprimer-demo-synthetic-v1-{SEED}-{session_idx + 1}'))
        previous_errors = 0
        session_variation = rng.uniform(-0.18, 0.18)
        for scene_idx, difficulty in enumerate(DIFFICULTIES):
            time_mean = (5.2 + difficulty * 3.3 + previous_errors * 0.85) * time_mult
            decision_time = max(2.0, min(85.0, rng.lognormvariate(math.log(time_mean), 0.36)))
            # Some choices happen quickly, other decisions are reconsidered.
            changes_lambda = max(0.04, 0.28 + difficulty * 0.15 + skill_bias * 0.18)
            changes = min(4, sum(rng.random() < changes_lambda / 3.2 for _ in range(4)))
            hesitation_ratio = max(0.025, min(0.87, rng.betavariate(1.5, 3.0) + 0.12 * changes + 0.1 * hesitation_bias))
            hesitation = round(min(decision_time, decision_time * hesitation_ratio), 2)
            decision_time = round(decision_time, 2)

            # This self-report label is SYNTHESIZED, not collected from a player.
            z = (-2.05 + 0.52 * difficulty + 0.032 * decision_time
                 + 0.23 * previous_errors + 0.32 * changes
                 + 0.55 * hesitation_ratio + 0.58 * skill_bias + session_variation)
            p_help = 1 / (1 + math.exp(-z))
            needs_help = int(rng.random() < p_help)
            rows.append({
                'session_id': sid,
                'karar_suresi_sn': f'{decision_time:.2f}',
                'onceki_hata_sayisi': str(previous_errors),
                'karar_degistirme_sayisi': str(changes),
                'sahne_zorlugu': str(difficulty),
                'tereddut_suresi_sn': f'{hesitation:.2f}',
                'yardim_etkisi': str(needs_help),
                'kaynak': 'synthetic',
            })
            # Simulated correctness is not the same as the need-for-help label.
            p_wrong = max(0.035, min(0.83, 0.11 + 0.09 * difficulty + 0.12 * skill_bias + 0.028 * previous_errors))
            if rng.random() < p_wrong:
                previous_errors += 1
    return rows


def main():
    output = Path(__file__).resolve().parents[1] / 'data' / 'oturumlar_sentetik_15.csv'
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = make_rows()
    with output.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Olusturuldu: {output} | satir={len(rows)} | sentetik_oturum=15 | kaynak=synthetic')


if __name__ == '__main__':
    main()
