# /utils/scoring.py

def calculate_mean_score(responses, keys):
    return sum(responses.get(k, 0) for k in keys) / len(keys)

# ----------------------------
# BIG FIVE
# ----------------------------

extraversion = ["EX01", "EX02", "EX03", "EX04", "EX05", "EX06", "EX07", "EX08", "EX09", "EX10"]
amabilidad = ["AM01", "AM02", "AM03", "AM04", "AM05", "AM06", "AM07", "AM08", "AM09", "AM10"]
responsabilidad = ["CO01", "CO02", "CO03", "CO04", "CO05", "CO06", "CO07", "CO08", "CO09", "CO10"]
neuroticismo = ["NE01", "NE02", "NE03", "NE04", "NE05", "NE06", "NE07", "NE08", "NE09", "NE10"]
apertura = ["AE01", "AE02", "AE03", "AE04", "AE05", "AE06", "AE07", "AE08", "AE09", "AE10"]

# ----------------------------
# PHISHING
# ----------------------------

phish_actitud_riesgo = ["ER01", "ER02", "ER03", "ER04", "ER05", "ER06", "ER07", "ER08", "ER09", "ER10"]
phish_awareness = ["AW01", "AW02", "AW03"]
phish_riesgo_percibido = ["PR01", "PR02", "PR03"]
phish_autoeficacia = ["CP01", "CP02", "CP03"]
phish_susceptibilidad = ["SU01","SU02","SU03", "SU04"]

# ============================
# FATIGA
# ============================

fatiga = ["FE01","FE02","FE03", "FC01","FC02","FC03", "DS01","DS02"]

# ============================
# FUNCIÓN PRINCIPAL
# ============================

def compute_scores(responses: dict) -> dict:
    """
    Calcula todos los scores consolidados y
    adjunta variables demográficas ya codificadas.
    """

    scores = {
        # --- Big Five
        "Big5_Extraversion": calculate_mean_score(responses, extraversion),
        "Big5_Amabilidad": calculate_mean_score(responses, amabilidad),
        "Big5_Responsabilidad": calculate_mean_score(responses, responsabilidad),
        "Big5_Neuroticismo": calculate_mean_score(responses, neuroticismo),
        "Big5_Apertura": calculate_mean_score(responses, apertura),
        # --- Phishing
        "Phish_Actitud_Riesgo": calculate_mean_score(responses, phish_actitud_riesgo),
        "Phish_Awareness": calculate_mean_score(responses, phish_awareness),
        "Phish_Riesgo_Percibido": calculate_mean_score(responses, phish_riesgo_percibido),
        "Phish_Autoeficacia": calculate_mean_score(responses, phish_autoeficacia),
        "Phish_Susceptibilidad": calculate_mean_score(responses, phish_susceptibilidad),

        # --- Fatiga
        "Fatiga_Global_Score": calculate_mean_score(responses, fatiga),
        
        # --- Demográficos (ya vienen codificados)
        "Demo_Pais": responses.get("COUNTRY"),
        "Demo_Tipo_Organizacion": responses.get("ORG_TYPE"),
        "Demo_Industria": responses.get("INDUSTRY"),
        "Demo_Tamano_Org": responses.get("EMPLOYEES"),
        "Demo_Rol_Trabajo": responses.get("ROLE"),
        "Demo_Generacion_Edad": responses.get("GENERATION"),
        "Demo_Genero": responses.get("GENDER"),
        "Demo_Nivel_Educacion": responses.get("EDUCATION"),
        "Demo_Horas": responses.get("HORAS")
    }
    
    

    return scores