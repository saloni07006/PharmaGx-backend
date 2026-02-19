from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "pharmaguard_random_forest.pkl"
FEATURES_PATH = BASE_DIR / "models" / "model_features.pkl"
