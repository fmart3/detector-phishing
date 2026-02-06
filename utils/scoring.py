import json
import os

REVERSE_QUESTIONS = set()
CATEGORIES = {}

def load_config():
    """Lee questions.json y mapea configuración."""
    global REVERSE_QUESTIONS, CATEGORIES
    
    file_path = "questions.json"
    
    if not os.path.exists(file_path):
        print(f"❌ Error Crítico: No se encontró {file_path}")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        survey_sections = data.get("survey", [])

        REVERSE_QUESTIONS = set()
        CATEGORIES = {}

        for section in survey_sections:
            section_id = section.get("id")
            questions = section.get("questions", [])
            
            if questions:
                # Guardamos los códigos (ej: ["EX01", "EX02"...])
                CATEGORIES[section_id] = [q["code"] for q in questions]

            for q in questions:
                if q.get("reverse") is True:
                    REVERSE_QUESTIONS.add(q["code"])
        
    except Exception as e:
        print(f"❌ Error leyendo questions.json: {e}")

# Cargar configuración al iniciar
load_config()

# ==========================================
# LÓGICA DE CÁLCULO
# ==========================================

def calculate_mean_score(responses: dict, question_codes: list, category_name: str = "") -> float:
    if not question_codes:
        return 0.0
    
    total = 0
    count = 0
    
    for code in question_codes:
        val = responses.get(code)
        if val is not None:
            val = int(val)
            # Invertir si es necesario
            if code in REVERSE_QUESTIONS:
                val = 6 - val
            
            total += val
            count += 1
            
    if count == 0:
        return 0.0
        
    return round(total / count, 2)

def compute_scores(responses: dict) -> dict:
    # Aseguramos que la config esté cargada
    if not CATEGORIES:
        load_config()

    scores = {
        # --- Big Five ---
        "Big5_Extraversion": calculate_mean_score(responses, CATEGORIES.get('big5_extraversion', [])),
        "Big5_Amabilidad": calculate_mean_score(responses, CATEGORIES.get('big5_amabilidad', [])),
        "Big5_Responsabilidad": calculate_mean_score(responses, CATEGORIES.get('big5_responsabilidad', [])),
        "Big5_Neuroticismo": calculate_mean_score(responses, CATEGORIES.get('big5_neuroticismo', [])),
        "Big5_Apertura": calculate_mean_score(responses, CATEGORIES.get('big5_apertura', [])),
        
        # --- Phishing ---
        "Phish_Actitud_Riesgo": calculate_mean_score(responses, CATEGORIES.get('phish_actitud', [])),
        "Phish_Awareness": calculate_mean_score(responses, CATEGORIES.get('phish_awareness', [])),
        "Phish_Riesgo_Percibido": calculate_mean_score(responses, CATEGORIES.get('phish_riesgo', [])),
        "Phish_Autoeficacia": calculate_mean_score(responses, CATEGORIES.get('phish_autoeficacia', [])),
        "Phish_Susceptibilidad": calculate_mean_score(responses, CATEGORIES.get('phish_susceptibilidad', [])),
    }

    # --- FATIGA (UNIFICADA) ---
    # Aquí juntamos las 3 sub-escalas en una sola lista para el cálculo
    fatiga_items = (
        CATEGORIES.get('fatiga_emocional', []) + 
        CATEGORIES.get('fatiga_cinismo', []) + 
        CATEGORIES.get('fatiga_deseo', [])
    )
    
    # Calculamos UN SOLO score global que es el que espera la base de datos
    scores["Fatiga_Global_Score"] = calculate_mean_score(responses, fatiga_items, "Fatiga Global")

    return scores