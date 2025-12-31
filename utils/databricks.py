import mlflow
import mlflow.pyfunc
import pandas as pd
import streamlit as st

def setup_mlflow():
    """
    Configura la conexión a Databricks usando secrets de Streamlit
    """
    mlflow.set_tracking_uri("databricks")

    # Estas variables deben existir en .streamlit/secrets.toml
    import os
    os.environ["DATABRICKS_HOST"] = st.secrets["DATABRICKS_HOST"]
    os.environ["DATABRICKS_TOKEN"] = st.secrets["DATABRICKS_TOKEN"]

@st.cache_resource
def load_model():
    """
    Carga el modelo registrado en Databricks MLflow
    """
    setup_mlflow()

    model_uri = "models:/Phishing_Model/Production"
    model = mlflow.pyfunc.load_model(model_uri)

    return model

def predict(features: dict):
    """
    Recibe un diccionario de features ya procesadas
    Retorna predicción y probabilidad
    """
    model = load_model()

    df = pd.DataFrame([features])

    pred = model.predict(df)

    # Compatibilidad con modelos sklearn
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(df)[0][1]
    else:
        proba = None

    return {
        "prediction": int(pred[0]),
        "probability": proba
    }