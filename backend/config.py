# ==========================================
# Configuration File
# ==========================================

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = str(PROJECT_ROOT / "backend"/ "models" / "pharmaguard_random_forest.pkl")
FEATURES_PATH = str(PROJECT_ROOT / "backend" / "models" / "model_features.pkl")
