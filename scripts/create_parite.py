import json
import joblib
import numpy as np
import pathlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # project root
MODEL_DIR = ROOT / "_out" / "model"
DATA_CSV = ROOT / "data" / "oturumlar.csv"
OUTPUT_JSON = ROOT / "tests" / "parite.json"

# Load sklearn model
model_path = MODEL_DIR / "model.joblib"
if not model_path.exists():
    sys.exit(f"✗ model.joblib not found at {model_path}")
model = joblib.load(model_path)

# Load data CSV
if not DATA_CSV.exists():
    sys.exit(f"✗ data csv not found at {DATA_CSV}")
import pandas as pd
df = pd.read_csv(DATA_CSV)

# Choose first 5 rows (or all if less)
ref_rows = df.head(5)
ref = []
for _, row in ref_rows.iterrows():
    x = row[["karar_suresi_sn", "onceki_hata_sayisi", "karar_degistirme_sayisi", "sahne_zorlugu", "tereddut_suresi_sn"]]
    # Create a one‑row DataFrame with proper column names for sklearn prediction
    x_df = pd.DataFrame([x])
    prob = float(model.predict_proba(x_df)[0][1])
    ref.append({"input": x.to_dict(), "expected_proba": prob})

OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_JSON.write_text(json.dumps(ref, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"parite.json created at {OUTPUT_JSON} with {len(ref)} entries")
