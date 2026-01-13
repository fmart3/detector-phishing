from datetime import datetime
import pandas as pd
import os

LOG_FILE = "production_predictions.csv"

def log_prediction(features: dict, result: dict):

    row = {
        "timestamp": datetime.utcnow(),
        **features,
        "probability": result.get("probability"),
        "risk_level": result.get("risk_level")
    }

    df = pd.DataFrame([row])

    if os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(LOG_FILE, index=False)
