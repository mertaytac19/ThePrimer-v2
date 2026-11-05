import json
import pathlib
import sys
import numpy as np

from pathlib import Path

# Pytest will discover this file automatically.

def load_config_and_model():
    """Load model.onnx, config.json and reference cases.
    Returns:
        model_path (Path): path to ONNX model file
        config (dict): config.json contents
        cases (list): list of dicts with 'input' and 'expected_proba'
    """
    # The project root is the parent directory of the "tests" folder.
    root = Path(__file__).resolve().parents[1]  # .../ThePrimer-v2
    model_path = root / "_out" / "model" / "model.onnx"
    config_path = root / "_out" / "model" / "config.json"
    json_path = root / "tests" / "parite.json"

    if not model_path.exists():
        raise FileNotFoundError(f"model.onnx not found at {model_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"config.json not found at {config_path}")
    if not json_path.exists():
        raise FileNotFoundError(f"parite.json not found at {json_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    with open(json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
    return model_path, config, cases

def test_onnx_vs_sklearn_parite():
    """Differansiyel test: compare ONNX output with sklearn reference.
    Each case from tests/parite.json contains "input" dict and
    "expected_proba" (produced by the sklearn model during generation).
    The test asserts that the ONNX inference probability differs by
    less than 1e-4.
    """
    model_path, config, cases = load_config_and_model()

    # Try to import onnxruntime; if not available, skip the test.
    try:
        import onnxruntime as ort
    except Exception as e:
        import pytest
        pytest.skip(f"onnxruntime not available: {e}")

    sess = ort.InferenceSession(str(model_path))
    # Feature order defined by config["features"]
    feature_order = [f["name"] for f in config["features"]]

    for idx, case in enumerate(cases):
        # Build input tensor according to feature order
        values = [float(case["input"][name]) for name in feature_order]
        x = np.array([values], dtype=np.float32)
        # ONNX output: probabilities tensor shape (1, n_classes)
        onnx_out = sess.run(["probabilities"], {"input": x})[0]
        # Positive class is index 1 (as in sklearn output)
        onnx_proba = float(onnx_out[0][1])
        expected = float(case["expected_proba"])
        diff = abs(onnx_proba - expected)
        assert diff < 1e-4, f"Case {idx} diff {diff:.2e} exceeds tolerance"
