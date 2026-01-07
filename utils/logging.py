import pandas as pd
from datetime import datetime
import os

LOG_FILE = "production_predictions.csv"

def log_prediction(features: dict, result: dict):
    row = {
        "timestamp": datetime.utcnow(),
        **features,
        "prediction": result["prediction"],
        "probability": result.get("probability")
    }

    df = pd.DataFrame([row])

    if os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(LOG_FILE, index=False)
