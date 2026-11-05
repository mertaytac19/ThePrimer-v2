import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('primer_training', ROOT / 'train.py')
train = importlib.util.module_from_spec(spec)
spec.loader.exec_module(train)


def test_demo_data_is_not_verified_production():
    df = train.load_data(ROOT / 'data' / 'oturumlar.csv')
    df = df[df['kaynak'].eq('synthetic')].copy()
    assert df['session_id'].nunique() == 5
    with pytest.raises(ValueError, match='15'):
        train.train_and_evaluate(df, demo=False)


def test_demo_model_is_explicitly_unverified():
    df = train.load_data(ROOT / 'data' / 'oturumlar.csv')
    df = df[df['kaynak'].eq('synthetic')].copy()
    pipeline, metrics, status, rows, sessions = train.train_and_evaluate(df, demo=True)
    assert status == 'demo_unverified'
    assert metrics is None
    assert sessions == 0
    assert rows == 5
    assert pipeline.predict_proba(df[train.FEATURES]).shape == (5, 2)


def test_negative_and_invalid_records_rejected(tmp_path):
    raw = (ROOT / 'data' / 'oturumlar.csv').read_text(encoding='utf-8')
    bad = tmp_path / 'bad.csv'
    bad.write_text(raw.replace('12.5,0,1,2,3.2','-12.5,0,1,2,3.2'), encoding='utf-8')
    with pytest.raises(ValueError, match='negatif'):
        train.load_data(bad)
