# ==========================================
# ML Model Loader
# ==========================================

import joblib
from config import MODEL_PATH, FEATURES_PATH


class PharmaGuardModel:
    def __init__(self):
        print("🔄 Loading RandomForest model...")
        self.model = joblib.load(MODEL_PATH)
        self.feature_columns = joblib.load(FEATURES_PATH)
        print("✅ Model loaded successfully.")

    def get_model(self):
        return self.model

    def get_feature_columns(self):
        return self.feature_columns


# Singleton instance (loads once)
model_instance = PharmaGuardModel()
