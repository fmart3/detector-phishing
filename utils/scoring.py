# /utils/scoring.py
import streamlit as st

# ==========================================
# 1. GENERADOR DE LLAVES (EXACTAS AL DEBUG)
# ==========================================
# Usamos f"{i:02d}" para asegurar que el 1 sea "01"

extraversion = [f"EX{i:02d}" for i in range(1, 11)]    # EX01...EX10
amabilidad = [f"AM{i:02d}" for i in range(1, 11)]      # AM01...AM10
responsabilidad = [f"CO{i:02d}" for i in range(1, 11)] # CO01...CO10
neuroticismo = [f"NE{i:02d}" for i in range(1, 11)]    # NE01...NE10
apertura = [f"AE{i:02d}" for i in range(1, 11)]        # AE01...AE10

phish_actitud_riesgo = [f"ER{i:02d}" for i in range(1, 11)] # ER01...ER10
phish_awareness = [f"AW{i:02d}" for i in range(1, 4)]       # AW01...AW03
phish_riesgo_percibido = [f"PR{i:02d}" for i in range(1, 4)] # PR01...PR03
phish_autoeficacia = [f"CP{i:02d}" for i in range(1, 4)]     # CP01...CP03
phish_susceptibilidad = [f"SU{i:02d}" for i in range(1, 5)]  # SU01...SU04

# Fatiga (Mezcla manual según tus llaves)
fatiga = ["FE01", "FE02", "FE03", "FC01", "FC02", "FC03", "FC04", "DS01", "DS02"]

# ==========================================
# 2. FUNCIÓN DE CÁLCULO ROBUSTA
# ==========================================

def calculate_mean_score(responses, keys, category_name="Unknown"):
    total = 0.0
    count = 0
    
    for k in keys:
        # Obtenemos el valor. Si no existe, devuelve None
        val = responses.get(k)
        
        if val is not None:
            try:
                # Forzamos conversión a float (por si viene como string "5")
                total += float(val)
                count += 1
            except ValueError:
                print(f"⚠️ Error: El valor de {k} no es un número: {val}")
        else:
            # Descomenta esto solo si quieres ver qué falta en la consola negra
            # print(f"ℹ️ Nota: Falta la respuesta para {k}")
            pass

    if count == 0:
        return 0.0
    
    return total / count

# ==========================================
# 3. FUNCIÓN PRINCIPAL
# ==========================================

def compute_scores(responses: dict) -> dict:
    
    # Debug en consola para verificar que está corriendo la versión NUEVA
    print("🔄 Ejecutando compute_scores (Versión Definitiva)...")

    scores = {
        # --- Big Five
        "Big5_Extraversion": calculate_mean_score(responses, extraversion, "Extraversion"),
        "Big5_Amabilidad": calculate_mean_score(responses, amabilidad, "Amabilidad"),
        "Big5_Responsabilidad": calculate_mean_score(responses, responsabilidad, "Responsabilidad"),
        "Big5_Neuroticismo": calculate_mean_score(responses, neuroticismo, "Neuroticismo"),
        "Big5_Apertura": calculate_mean_score(responses, apertura, "Apertura"),
        
        # --- Phishing
        "Phish_Actitud_Riesgo": calculate_mean_score(responses, phish_actitud_riesgo, "Actitud"),
        "Phish_Awareness": calculate_mean_score(responses, phish_awareness, "Awareness"),
        "Phish_Riesgo_Percibido": calculate_mean_score(responses, phish_riesgo_percibido, "Riesgo"),
        "Phish_Autoeficacia": calculate_mean_score(responses, phish_autoeficacia, "Autoeficacia"),
        "Phish_Susceptibilidad": calculate_mean_score(responses, phish_susceptibilidad, "Susceptibilidad"),

        # --- Fatiga
        "Fatiga_Global_Score": calculate_mean_score(responses, fatiga, "Fatiga")
    }
    
    return scores