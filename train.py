"""The Primer v2 — reproducible sklearn → ONNX training with a strict release gate.

Usage:
  python train.py          # production: needs >= 15 real user sessions and F1 >= 0.65
  python train.py --demo   # explicit demonstration model, NEVER production-verified
"""
import argparse
import json
import math
import os
import shutil
import sys
from pathlib import Path

# On Windows, onnxruntime must be imported before scikit-learn / OpenMP
# to prevent DLL initialization conflicts (ERROR_DLL_INIT_FAILED).
try:
    import onnxruntime as ort
except Exception:
    ort = None

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'oturumlar.csv'
MODEL = ROOT / '_out' / 'model'
SEED = 13
F1_MIN = 0.65  # specified in spec.md BEFORE inspecting real test results
DECISION_THRESHOLD = 0.6
FEATURES = ['karar_suresi_sn', 'onceki_hata_sayisi', 'karar_degistirme_sayisi', 'sahne_zorlugu', 'tereddut_suresi_sn']
TARGET = 'yardim_etkisi'
REQUIRED = ['session_id', *FEATURES, TARGET, 'kaynak']


def load_data(path):
    if not path.is_file():
        raise ValueError(f'Veri dosyası bulunamadı: {path}')
    df = pd.read_csv(path, dtype={'session_id': str, 'kaynak': str})
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(f'Eksik sütunlar: {missing}')
    if df.empty:
        raise ValueError('CSV boş.')
    df = df[REQUIRED].copy()
    df['kaynak'] = df['kaynak'].replace({'real': 'gercek', 'sentetik': 'synthetic'})
    if df['session_id'].isna().any() or (df['session_id'].str.strip() == '').any():
        raise ValueError('session_id boş olamaz.')
    if not df['kaynak'].isin(['gercek', 'synthetic']).all():
        raise ValueError('kaynak yalnızca gercek veya synthetic olabilir.')
    for column in [*FEATURES, TARGET]:
        df[column] = pd.to_numeric(df[column], errors='raise')
        if not np.isfinite(df[column].to_numpy(dtype='float64')).all():
            raise ValueError(f'{column}: NaN/inf geçersiz.')
    for column in FEATURES:
        if (df[column] < 0).any():
            raise ValueError(f'{column}: negatif değer var.')
    if not df[TARGET].isin([0, 1]).all():
        raise ValueError('Hedef etiket 0 veya 1 olmalı.')
    if not df['sahne_zorlugu'].between(1, 5).all():
        raise ValueError('Sahne zorluğu 1–5 arasında olmalı.')
    if (df['tereddut_suresi_sn'] > df['karar_suresi_sn'] + 0.05).any():
        raise ValueError('Tereddüt süresi toplam karar süresinden büyük olamaz.')
    return df


def new_pipeline():
    return Pipeline([
        ('scaler', StandardScaler()),
        ('clf', LogisticRegression(max_iter=1000, random_state=SEED)),
    ])


def train_and_evaluate(df, demo=False):
    if demo:
        if df[TARGET].nunique() != 2:
            raise ValueError('Demo için bile her iki etiket sınıfı gerekli.')
        metrics = None
        n_sessions = df['session_id'].nunique()
        if n_sessions >= 10:
            groups = df.session_id
            X = df[FEATURES]
            y = df[TARGET]
            candidates = GroupShuffleSplit(n_splits=100, test_size=0.25, random_state=SEED)
            split = None
            for train_idx, test_idx in candidates.split(X, y, groups):
                if y.iloc[train_idx].nunique() == 2 and y.iloc[test_idx].nunique() == 2:
                    split = train_idx, test_idx
                    break
            if split is not None:
                tr, te = split
                if set(groups.iloc[tr]) & set(groups.iloc[te]):
                    raise RuntimeError('VERİ SIZINTISI: Bir oturum hem eğitim hem test kümesinde.')
                eval_pipeline = new_pipeline().fit(X.iloc[tr], y.iloc[tr])
                pred = eval_pipeline.predict(X.iloc[te])
                from sklearn.metrics import confusion_matrix
                cm = confusion_matrix(y.iloc[te], pred).tolist()
                metrics = {
                    'accuracy': round(float(accuracy_score(y.iloc[te], pred)), 6),
                    'precision': round(float(precision_score(y.iloc[te], pred, zero_division=0)), 6),
                    'recall': round(float(recall_score(y.iloc[te], pred, zero_division=0)), 6),
                    'f1': round(float(f1_score(y.iloc[te], pred, zero_division=0)), 6),
                    'confusion_matrix': cm,
                    'train_rows': len(tr), 'test_rows': len(te),
                    'train_sessions': int(groups.iloc[tr].nunique()),
                    'test_sessions': int(groups.iloc[te].nunique()),
                    'evaluation_type': 'demo_session_split_synthetic_eval'
                }
        pipeline = new_pipeline().fit(df[FEATURES], df[TARGET])
        return pipeline, metrics, 'demo_unverified', len(df), 0

    real = df.loc[df.kaynak == 'gercek'].copy()
    n_sessions = real['session_id'].nunique()
    if n_sessions < 15:
        raise ValueError(f'Üretim modeli için en az 15 GERÇEK oturum gerekiyor; mevcut: {n_sessions}. Demo için --demo kullan.')
    if real[TARGET].nunique() != 2:
        raise ValueError('Gerçek veride hem 0 hem 1 etiketleri olmalı.')
    if real.groupby('session_id')[TARGET].nunique().empty:
        raise ValueError('Geçerli gerçek oturum yok.')
    X = real[FEATURES]
    y = real[TARGET]
    groups = real.session_id
    candidates = GroupShuffleSplit(n_splits=100, test_size=0.25, random_state=SEED)
    split = None
    for train_idx, test_idx in candidates.split(X, y, groups):
        if y.iloc[train_idx].nunique() == 2 and y.iloc[test_idx].nunique() == 2:
            split = train_idx, test_idx
            break
    if split is None:
        raise ValueError('Oturum bazlı train/test ayrımında iki sınıfı da içeren bölünme bulunamadı. Daha fazla dengeli gerçek veri topla.')
    tr, te = split
    if set(groups.iloc[tr]) & set(groups.iloc[te]):
        raise RuntimeError('VERİ SIZINTISI: Bir oturum hem eğitim hem test kümesinde.')
    eval_pipeline = new_pipeline().fit(X.iloc[tr], y.iloc[tr])
    pred = eval_pipeline.predict(X.iloc[te])
    metrics = {
        'accuracy': round(float(accuracy_score(y.iloc[te], pred)), 6),
        'precision': round(float(precision_score(y.iloc[te], pred, zero_division=0)), 6),
        'recall': round(float(recall_score(y.iloc[te], pred, zero_division=0)), 6),
        'f1': round(float(f1_score(y.iloc[te], pred, zero_division=0)), 6),
        'train_rows': len(tr), 'test_rows': len(te),
        'train_sessions': int(groups.iloc[tr].nunique()),
        'test_sessions': int(groups.iloc[te].nunique()),
        'f1_acceptance_threshold': F1_MIN,
    }
    # The threshold check happens BEFORE any output is published or overwritten.
    if metrics['f1'] < F1_MIN:
        raise ValueError(f'Model kabul kapısını geçmedi: F1={metrics["f1"]} < {F1_MIN}. Mevcut model korunuyor.')
    # Evaluate on held-out sessions, then retrain release artifact on all real data.
    release_pipeline = new_pipeline().fit(X, y)
    return release_pipeline, metrics, 'production_verified', len(real), n_sessions


def export_onnx_and_verify(pipeline, output_dir, sample):
    global ort
    if ort is None:
        import onnxruntime as ort
    from skl2onnx import to_onnx
    from skl2onnx.common.data_types import FloatTensorType

    onx = to_onnx(
        pipeline,
        initial_types=[('input', FloatTensorType([None, len(FEATURES)]))],
        options={id(pipeline.named_steps['clf']): {'zipmap': False}},
        target_opset=17,
    )
    path = output_dir / 'model.onnx'
    path.write_bytes(onx.SerializeToString())
    sess = ort.InferenceSession(str(path), providers=['CPUExecutionProvider'])
    in_name = sess.get_inputs()[0].name
    output_names = [item.name for item in sess.get_outputs()]
    prob_name = next((x for x in output_names if 'prob' in x.lower()), output_names[-1])
    as32 = sample[FEATURES].to_numpy(dtype=np.float32)
    actual = np.asarray(sess.run([prob_name], {in_name: as32})[0])
    expected = pipeline.predict_proba(sample[FEATURES])
    if actual.shape != expected.shape:
        raise ValueError(f'ONNX çıktı şekli beklenenden farklı: {actual.shape}, {expected.shape}')
    diff = float(np.max(np.abs(actual - expected)))
    if not np.isfinite(diff) or diff >= 1e-4:
        raise ValueError(f'ONNX parite kontrolü başarısız: max_abs_diff={diff:.9g}')
    return diff, in_name, prob_name


def main():
    parser = argparse.ArgumentParser(description='The Primer v2 model training')
    parser.add_argument('--data', type=Path, default=DATA)
    parser.add_argument('--demo', action='store_true', help='Kabul eşiği karşılanmış üretim modeli DEĞİL, demo modeli üret')
    args = parser.parse_args()
    df = load_data(args.data)
    pipeline, metrics, status, n_rows, n_real_sessions = train_and_evaluate(df, args.demo)
    scratch = ROOT / '_out' / 'model_candidate'
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    try:
        sample = df.loc[df.kaynak == 'gercek'] if not args.demo else df
        parity, input_name, output_name = export_onnx_and_verify(pipeline, scratch, sample.head(min(20, len(sample))))
        config = {
            'title': 'The Primer v2 — Adaptif Yardım Modeli',
            'description': 'Oyuncunun öz bildirimine dayalı yardım ihtiyacı sınıflandırıcısı',
            'target': TARGET,
            'class_labels': {'0': 'yardım gerekmez', '1': 'yardım gerekiyor'},
            'classes': [str(v) for v in pipeline.classes_],
            'features': [{'name': f, 'label': f, 'example': float(sample.iloc[0][f])} for f in FEATURES],
            'decision_threshold': DECISION_THRESHOLD,
            'evaluation_status': status,
            'metrics': metrics,
            'training_rows': int(n_rows),
            'real_session_count': int(n_real_sessions),
            'onnx_parity_max_abs_diff': parity,
            'onnx_input_name': input_name,
            'onnx_probability_output_name': output_name,
            'seed': SEED,
            'sklearn_version': sklearn.__version__,
            'python_version': f'{sys.version_info.major}.{sys.version_info.minor}',
        }
        (scratch / 'config.json').write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')
        joblib.dump(pipeline, scratch / 'model.joblib')
        card = f'''# The Primer v2 — Model Kartı\n\n**Durum:** `{status}`.\n\n## Amaç\nKüçük lojistik regresyon modeli, oyuncunun bildirdiği yardım ihtiyacı etiketini oyun davranışlarından tahmin eder.\n\n## Veri\nEğitim satırı: {n_rows}. Bağımsız gerçek oturum sayısı: {n_real_sessions}. Kaynak: data/oturumlar.csv.\n\n## Ölçüm\nOturum bazlı veri ayrımı; üretim kabul koşulu F1 ≥ {F1_MIN}. Metrikler: `{json.dumps(metrics,ensure_ascii=False)}`. ONNX–sklearn maksimum fark: {parity:.9g}.\n\n## Sınırlamalar\nBu bir sağlık/eğitim başarısı tanısı değildir; öz bildirim yanıltıcı olabilir, az veriyle genelleme güvenilir değildir. Karar verme sırasında alınan ara özellikler ile eğitimdeki final-özellik dağılımı farklılık gösterebilir.\n\n## Kullanılmaması gereken durumlar\nKritik güvenlik, sağlık, disiplin ve öğrenci puanlama kararlarında kullanılmamalıdır.\n'''
        (scratch / 'README.md').write_text(card, encoding='utf-8')
        # Keep the previous working artifact until every validation and write passes.
        backup = ROOT / '_out' / 'model_previous'
        if backup.exists(): shutil.rmtree(backup)
        if MODEL.exists(): MODEL.rename(backup)
        scratch.rename(MODEL)
        print(f'OK: {MODEL} | durum={status} | ONNX farkı={parity:.9g}')
        if args.demo: print('UYARI: Sadece demo modeli. Gerçek 15 oturum ve güvenilir değerlendirme gereklidir.')
        else: print('GERCEK veri oturum sayısı:', n_real_sessions, '| değerlendirme:', metrics)
    except Exception:
        if scratch.exists(): shutil.rmtree(scratch)
        raise

if __name__ == '__main__':
    try: main()
    except Exception as exc:
        print('EĞİTİM DURDU:', exc, file=sys.stderr)
        sys.exit(1)
