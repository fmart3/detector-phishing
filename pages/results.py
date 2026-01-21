import streamlit as st
import os
import time
import threading
import numpy as np

# Imports de tus utilidades
from utils.scoring import compute_scores
from utils.databricks import predict, prepare_features
from utils.persistence import insert_survey_response
from utils.scales import INIT_PAGE

# ==========================================================
# 1. HELPER: SANITIZAR DATOS (Convierte NumPy a Python puro)
# ==========================================================
def sanitize_dict(d):
    """Recursivamente convierte tipos numpy a nativos de python"""
    if isinstance(d, dict):
        return {k: sanitize_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [sanitize_dict(v) for v in d]
    elif isinstance(d, (np.integer, np.int64, np.int32)):
        return int(d)
    elif isinstance(d, (np.floating, np.float64, np.float32)):
        return float(d)
    elif pd.isna(d):  # Maneja NaN de pandas
        return None
    else:
        return d

import pandas as pd # Necesario para el pd.isna de arriba

# ==========================================================
# 2. FUNCIÓN WORKER (Segundo Plano)
# ==========================================================
def task_save_background(responses, scores, model_output):
    """
    Se ejecuta en un hilo aparte.
    """
    # Usamos flush=True para forzar que salga en la terminal inmediatamente
    print("🔄 [Background] Hilo iniciado...", flush=True)
    
    try:
        start_t = time.time()
        
        insert_survey_response(
            responses=responses,
            scores=scores,
            model_output=model_output
        )
        
        duration = time.time() - start_t
        print(f"✅ [Background] Guardado exitoso en {duration:.2f}s", flush=True)
        
    except Exception as e:
        print(f"❌ [Background] FATAL ERROR en DB: {e}", flush=True)

# ==========================================================
# 3. PÁGINA PRINCIPAL
# ==========================================================
def page_results():
    st.markdown('<div class="bootstrap-card">', unsafe_allow_html=True)
    st.markdown("## 📊 Resultado de la Evaluación")

    # ------------------------------------------------------
    # A. OBTENCIÓN DE DATOS
    # ------------------------------------------------------
    responses = st.session_state.get("responses")    
    if not responses:
        st.error("⚠️ No hay respuestas. Vuelva al inicio.")
        if st.button("Ir al Inicio"):
            st.session_state.page = INIT_PAGE
            st.rerun()
        return
    
    # --- DEBUGGER DE LLAVES ---
    if "responses" in st.session_state and st.session_state["responses"]:
        st.error("🛑 PARA: MIRA ESTAS LLAVES")
        keys_list = list(st.session_state["responses"].keys())
        # Filtramos solo las que parecen preguntas (cortas)
        short_keys = [k for k in keys_list if len(str(k)) < 6]
        st.write("Tus respuestas tienen estos nombres:", short_keys)
        st.stop() # Esto detendrá la app para que puedas leerlo
    # ---------------------------

    # Calcular Scores si no existen
    if st.session_state.get("scores") is None:
        scores = compute_scores(responses)
        st.session_state.scores = scores
    else:
        scores = st.session_state.scores

    # ------------------------------------------------------
    # B. PREDICCIÓN (IA)
    # ------------------------------------------------------
    if st.session_state.get("prediction") is None:
        with st.spinner("⏱️ Analizando patrones de comportamiento..."):
            try:
                # 1. Preparar features (Versión Lite 6 variables)
                model_features = prepare_features(scores, responses)
                
                # 2. Predecir
                pred_result = predict(model_features)
                st.session_state.prediction = pred_result
                
            except Exception as e:
                st.error(f"Error en el motor de IA: {e}")
                # Valores por defecto para no bloquear
                st.session_state.prediction = {"probability": 0.0, "prediction": 0}

    # Extraer valores seguros
    result = st.session_state.prediction
    probability = float(result.get("probability", 0.0))

    # Determinar Riesgo
    if probability < 0.33:
        risk_level = "BAJO"
        color = "green"
        msg_type = "success"
    elif probability < 0.40:
        risk_level = "MEDIO"
        color = "orange"
        msg_type = "warning"
    else:
        risk_level = "ALTO"
        color = "red"
        msg_type = "error"

    # ------------------------------------------------------
    # C. VISUALIZACIÓN (¡PRIORIDAD ALTA!)
    # ------------------------------------------------------
    # Mostramos esto ANTES de intentar guardar, para que el usuario siempre vea su resultado.
    
    st.write("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Probabilidad de Phishing", f"{probability*100:.1f}%")
        st.caption("Basado en el modelo XGBoost Lite")
        
    with col2:
        st.markdown(f"""
            <div style="background-color: {color}; padding: 10px; border-radius: 5px; color: white; text-align: center;">
                <h3 style="margin:0;">Riesgo {risk_level}</h3>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    if risk_level == "ALTO":
        st.error("🚨 Su perfil indica alta vulnerabilidad. Se recomienda entrenamiento intensivo.")
    elif risk_level == "MEDIO":
        st.warning("⚠️ Riesgo moderado. Preste atención a remitentes desconocidos.")
    else:
        st.success("✅ Buen nivel de ciberseguridad. Mantenga sus hábitos.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------------------
    # D. GUARDADO EN SEGUNDO PLANO (Fire and Forget)
    # ------------------------------------------------------
    # Lo hacemos al final dentro de un try/except gigante para que NADA rompa la UI.
    
    if not st.session_state.get("logged"):
        try:
            # 1. Sanitizar datos (Quitar NumPy)
            clean_responses = sanitize_dict(responses)
            clean_scores = sanitize_dict(scores)
            clean_output = {
                "probability": probability,
                "risk_level": risk_level
            }

            # 2. Iniciar Hilo
            db_thread = threading.Thread(
                target=task_save_background,
                args=(clean_responses, clean_scores, clean_output)
            )
            db_thread.start()
            
            # 3. Marcar y Notificar
            st.session_state.logged = True
            
            # Usamos toast en lugar de success fijo para no ensuciar la UI
            st.toast("✅ Resultados guardados exitosamente.", icon="💾")
            
        except Exception as e:
            # Si falla la preparación del hilo, lo mostramos en consola
            print(f"❌ Error iniciando guardado en background: {e}", flush=True)
            # Opcional: st.warning("No se pudo guardar el registro, pero sus resultados son correctos.")

    # ------------------------------------------------------
    # E. BOTÓN DE REINICIO
    # ------------------------------------------------------
    st.write("---")
    if st.button("🔄 Nueva Evaluación"):
        for k in ["page", "responses", "scores", "prediction", "logged"]:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state.page = INIT_PAGE
        st.rerun()