# /utils/scoring.py

# ============================
# 1. MAPEO DE SINÓNIMOS (NORMALIZADOR)
# ============================
# Aquí le enseñamos al código que "E" es lo mismo que "EX", etc.
KEY_MAPPING = {
    # Big 5
    "E": "EX",  "EXT": "EX", # Extraversion
    "A": "AM",  "AGR": "AM", # Amabilidad
    "C": "CO",  "CON": "CO", "CS": "CO", # Responsabilidad (Conscientiousness)
    "N": "NE",  "NEU": "NE", # Neuroticismo
    "O": "AE",  "OPE": "AE", # Apertura (Openness) -> AE
    
    # Phishing (Prefijos probables vs Scoring)
    "AR": "ER", # Actitud Riesgo
    "AW": "AW", 
    "SE": "CP", # Self-Efficacy (Autoeficacia) -> CP
    "SU": "SU"
}

def normalize_response_keys(responses):
    """
    Crea un nuevo diccionario donde las llaves raras (E1, C01)
    se renombran a las estándar (EX01, CO01).
    """
    normalized = responses.copy()
    
    for key, value in responses.items():
        # Saltamos llaves largas (como demográficos)
        if len(key) > 5: continue
        
        # Separamos letras y números (Ej: "E1" -> "E", "1")
        import re
        match = re.match(r"([a-zA-Z]+)(\d+)", key)
        if match:
            prefix, num_str = match.groups()
            prefix = prefix.upper()
            num = int(num_str)
            
            # Si el prefijo está en nuestro mapa, creamos la versión estándar
            if prefix in KEY_MAPPING:
                std_prefix = KEY_MAPPING[prefix]
                # Generamos EX01 y EX1 para asegurar compatibilidad
                std_key_long = f"{std_prefix}{num:02d}" # EX01
                std_key_short = f"{std_prefix}{num}"    # EX1
                
                normalized[std_key_long] = value
                normalized[std_key_short] = value
                
    return normalized

# ============================
# 2. FUNCIONES DE CÁLCULO
# ============================

def get_smart_value(responses, key):
    # Intenta EX01
    if key in responses: return float(responses[key])
    # Intenta EX1
    try:
        prefix = key[:2]
        number = int(key[2:])
        alt = f"{prefix}{number}"
        if alt in responses: return float(responses[alt])
    except: pass
    return 0.0

def calculate_mean_score(responses, keys):
    values = [get_smart_value(responses, k) for k in keys]
    # Filtramos ceros SOLO si sospechamos que no se respondieron (opcional)
    # Pero aquí asumimos 0 es "no encontrado". 
    # Mejor contar solo los encontrados > 0 para depurar? 
    # No, mantengamos el promedio simple.
    
    # Debug visual en consola para saber qué está sumando
    found = [v for v in values if v > 0]
    if len(found) == 0 and len(keys) > 0:
        # Si todo es 0, es sospechoso para estas claves
        print(f"⚠️ Alerta: Score 0 para {keys[0][:2]}... ¿Llaves correctas?")
        
    return sum(values) / len(keys) if len(keys) > 0 else 0

# ============================
# 3. DEFINICIONES DE LLAVES (Las que TÚ quieres usar)
# ============================
extraversion = [f"EX{i:02d}" for i in range(1, 11)]
amabilidad = [f"AM{i:02d}" for i in range(1, 11)]
responsabilidad = [f"CO{i:02d}" for i in range(1, 11)]
neuroticismo = [f"NE{i:02d}" for i in range(1, 11)]
apertura = [f"AE{i:02d}" for i in range(1, 11)]

phish_actitud = [f"ER{i:02d}" for i in range(1, 11)]
phish_awareness = [f"AW{i:02d}" for i in range(1, 4)]
phish_riesgo = [f"PR{i:02d}" for i in range(1, 4)]
phish_autoeficacia = [f"CP{i:02d}" for i in range(1, 4)]
phish_susceptibilidad = [f"SU{i:02d}" for i in range(1, 5)]

fatiga = ["FE01", "FE02", "FE03", "FC01", "FC02", "FC03", "FC04", "DS01", "DS02"]

# ============================
# 4. FUNCIÓN PRINCIPAL
# ============================

def compute_scores(responses: dict) -> dict:
    
    # 1. PASO CRÍTICO: Normalizar llaves antes de calcular
    # Esto convierte "E1" en "EX01", "C5" en "CO05", etc.
    clean_responses = normalize_response_keys(responses)
    
    scores = {
        "Big5_Extraversion": calculate_mean_score(clean_responses, extraversion),
        "Big5_Amabilidad": calculate_mean_score(clean_responses, amabilidad),
        "Big5_Responsabilidad": calculate_mean_score(clean_responses, responsabilidad),
        "Big5_Neuroticismo": calculate_mean_score(clean_responses, neuroticismo),
        "Big5_Apertura": calculate_mean_score(clean_responses, apertura),
        
        "Phish_Actitud_Riesgo": calculate_mean_score(clean_responses, phish_actitud),
        "Phish_Awareness": calculate_mean_score(clean_responses, phish_awareness),
        "Phish_Riesgo_Percibido": calculate_mean_score(clean_responses, phish_riesgo),
        "Phish_Autoeficacia": calculate_mean_score(clean_responses, phish_autoeficacia),
        "Phish_Susceptibilidad": calculate_mean_score(clean_responses, phish_susceptibilidad),
        
        "Fatiga_Global_Score": calculate_mean_score(clean_responses, fatiga)
    }
    
    return scores