"""
compare_parite.py
Python ONNX Oracle: tests/parite.json referans girdilerini ONNX modeli
ile calistirip beklenen olasiliklarla karsilastirir.

Kullanim:
    python scripts/compare_parite.py
"""
import json
import sys
from pathlib import Path

import numpy as np

def main():
    root = Path(__file__).resolve().parent.parent
    model_path = root / "_out" / "model" / "model.onnx"
    config_path = root / "_out" / "model" / "config.json"
    parite_path = root / "tests" / "parite.json"

    for p in [model_path, config_path, parite_path]:
        if not p.exists():
            print("HATA: Dosya bulunamadi:", p)
            sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    feature_names = [feat["name"] for feat in cfg["features"]]

    with open(parite_path, "r", encoding="utf-8") as f:
        refs = json.load(f)

    try:
        import onnxruntime as ort
    except ImportError:
        print("HATA: onnxruntime yuklu degil.")
        sys.exit(1)

    sess = ort.InferenceSession(str(model_path))
    input_name = sess.get_inputs()[0].name

    print("Python ONNX Oracle - Parite Testi")
    print("=" * 60)
    print("Model:", model_path.name)
    print("Config features:", feature_names)
    print("Input tensor name:", input_name)
    print("Referans sayisi:", len(refs))
    print("=" * 60)

    all_pass = True
    for i, entry in enumerate(refs):
        inp = entry["input"]
        vec = [float(inp[name]) for name in feature_names]
        tensor = np.array([vec], dtype=np.float32)

        out = sess.run(["probabilities"], {input_name: tensor})[0]
        # Binary: index 1 = positive class ("yardim gerekiyor")
        onnx_prob = float(out[0][1])
        expected = float(entry["expected_proba"])
        diff = abs(onnx_prob - expected)
        status = "PASS" if diff < 1e-4 else "FAIL"
        if diff >= 1e-4:
            all_pass = False

        print("Entry %d: expected=%.10f  onnx=%.10f  diff=%.2e  [%s]" % (
            i + 1, expected, onnx_prob, diff, status))

    print("=" * 60)
    if all_pass:
        print("Sonuc: TUMU GECTI (5/5)")
    else:
        print("Sonuc: BAZI TESTLER BASARISIZ")
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
