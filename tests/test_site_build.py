from pathlib import Path


def test_static_frontend_contract():
    root=Path(__file__).resolve().parents[1]
    text=(root/'web'/'index.html').read_text(encoding='utf-8')
    js=(root/'web'/'app.js').read_text(encoding='utf-8')
    assert 'primer-model-base' in text
    assert 'data-cy="self-report"' in text
    assert 'window.primerRunInference=runInference' in js
    assert 'onceki_hata_sayisi:session.errors' in js
