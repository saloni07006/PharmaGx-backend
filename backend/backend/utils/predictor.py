# utils/predictor.py

import pandas as pd
from ml_model import model_instance

def predict_risk(drug: str, phenotype: str):

    model = model_instance.get_model()
    feature_columns = model_instance.get_feature_columns()

    input_df = pd.DataFrame([{
        "drug": drug,
        "phenotype": phenotype
    }])

    input_encoded = pd.get_dummies(input_df)

    input_encoded = input_encoded.reindex(
        columns=feature_columns,
        fill_value=0
    )

    prediction = model.predict(input_encoded)[0]
    probabilities = model.predict_proba(input_encoded)[0]

    confidence_score = float(max(probabilities))

    return prediction, round(confidence_score, 4)
