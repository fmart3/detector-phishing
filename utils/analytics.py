import os
import pandas as pd
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

def get_dashboard_stats():
    """
    Conecta a Databricks, descarga datos y calcula estadísticas básicas.
    Devuelve un diccionario puro (JSON-serializable).
    """
    host = os.getenv("DATABRICKS_HOST").replace("https://", "").replace("http://", "").rstrip("/")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")

    query = "SELECT risk_level, probability FROM phishing.surveys.responses"
    
    try:
        with sql.connect(server_hostname=host, http_path=http_path, access_token=token) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                # Convertimos a lista de diccionarios
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
        if not rows:
            return {"error": "No hay datos"}

        df = pd.DataFrame(rows, columns=columns)
        
        # --- CÁLCULOS SIMPLES (Pandas) ---
        total = len(df)
        avg_prob = float(df["probability"].mean())
        
        # Conteo de riesgo
        risk_counts = df["risk_level"].value_counts().to_dict()
        
        return {
            "total_responses": total,
            "average_probability": round(avg_prob, 2),
            "risk_distribution": risk_counts # ej: {'ALTO': 5, 'MEDIO': 2}
        }

    except Exception as e:
        print(f"Error Analytics: {e}")
        return {"error": str(e)}