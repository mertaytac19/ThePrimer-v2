"""Pytest's default test_*.py discovery also runs the required tests/parite.py."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('required_parity_test', HERE / 'parite.py')
required = importlib.util.module_from_spec(spec)
spec.loader.exec_module(required)


def test_required_onnx_sklearn_parity():
    required.test_onnx_vs_sklearn_parite()
