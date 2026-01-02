## envio a modelo

# ----------------------------
# BIG FIVE
# ----------------------------

def score_big5_extraversion(responses):
    keys = ["EX01", "EX02", "EX03", "EX04", "EX05", "EX06", "EX07", "EX08", "EX09", "EX10"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_big5_amabilidad(responses):
    keys = ["AM01", "AM02", "AM03", "AM04", "AM05", "AM06", "AM07", "AM08", "AM09", "AM10"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_big5_responsabilidad(responses):
    keys = ["CO01", "CO02", "CO03", "CO04", "CO05", "CO06", "CO07", "CO08", "CO09", "CO10"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_big5_neuroticismo(responses):
    keys = ["NE01", "NE02", "NE03", "NE04", "NE05", "NE06", "NE07", "NE08", "NE09", "NE10"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_big5_apertura(responses):
    keys = ["AE01", "AE02", "AE03", "AE04", "AE05", "AE06", "AE07", "AE08", "AE09", "AE10"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

# ----------------------------
# PHISHING
# ----------------------------

def score_phish_actitud_riesgo(responses):
    keys = ["ER01", "ER02", "ER03", "ER04", "ER05", "ER06", "ER07", "ER08", "ER09", "ER10"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_phish_awareness(responses):
    keys = ["AW01", "AW02", "AW03"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_phish_riesgo_percibido(responses):
    keys = ["PR01", "PR02", "PR03"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_phish_autoeficacia(responses):
    keys = ["CP01", "CP02", "CP03"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_phish_susceptibilidad(responses):
    keys = ["SU01","SU02","SU03", "SU04"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

# ============================
# FATIGA
# ============================

def score_fatiga_emocional(responses):
    keys = ["FE01","FE02","FE03"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_fatiga_cinismo(responses):
    keys = ["FC01","FC02","FC03"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_fatiga_abandono(responses):
    keys = ["DS01","DS02"]
    return sum(responses.get(k, 0) for k in keys) / len(keys)

def score_fatiga_global(responses):
    return (
        score_fatiga_emocional(responses) +
        score_fatiga_cinismo(responses) +
        score_fatiga_abandono(responses)
    ) / 3

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
        "Big5_Extraversion": score_big5_extraversion(responses),
        "Big5_Amabilidad": score_big5_amabilidad(responses),
        "Big5_Responsabilidad": score_big5_responsabilidad(responses),
        "Big5_Neuroticismo": score_big5_neuroticismo(responses),
        "Big5_Apertura": score_big5_apertura(responses),

        # --- Phishing
        "Phish_Actitud_Riesgo": score_phish_actitud_riesgo(responses),
        "Phish_Awareness": score_phish_awareness(responses),
        "Phish_Riesgo_Percibido": score_phish_riesgo_percibido(responses),
        "Phish_Autoeficacia": score_phish_autoeficacia(responses),
        "Phish_Susceptibilidad": score_phish_susceptibilidad(responses),

        # --- Fatiga
        "Fatiga_Emocional": score_fatiga_emocional(responses),
        "Fatiga_Cinismo": score_fatiga_cinismo(responses),
        "Fatiga_Abandono": score_fatiga_abandono(responses),
        "Fatiga_Global_Score": score_fatiga_global(responses),

        # --- Demográficos (ya vienen codificados)
        "Demo_Pais": responses.get("COUNTRY"),
        "Demo_Tipo_Organizacion": responses.get("ORG_TYPE"),
        "Demo_Industria": responses.get("INDUSTRY"),
        "Demo_Tamano_Org": responses.get("EMPLOYEES"),
        "Demo_Rol_Trabajo": responses.get("ROLE"),
        "Demo_Generacion_Edad": responses.get("GENERATION"),
        "Demo_Genero": responses.get("GENDER"),
        "Demo_Nivel_Educacion": responses.get("EDUCATION"),
    }

    return scores