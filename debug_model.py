import joblib
import pandas as pd

# Cargar modelo
model = joblib.load("phishing_model.pkl")

print("=== 🔍 INSPECCIÓN DEL MODELO ===")

# 1. Verificar si tiene nombres de features guardados
if hasattr(model, "feature_names_in_"):
    print("\n✅ El modelo espera EXACTAMENTE estas columnas en este orden:")
    print(model.feature_names_in_)
else:
    print("\n⚠️ El modelo no tiene 'feature_names_in_'.") 
    # Si es un Pipeline, a veces hay que buscar dentro del paso del clasificador
    try:
        print("Intentando buscar en el classifier del pipeline...")
        print(model.named_steps['classifier'].feature_names_in_)
    except:
        print("❌ No se pudo determinar el orden automático. Debes mirar tu notebook de entrenamiento (X_train.columns).")

print("\n=== 🧪 COEFICIENTES (Pesos) ===")
try:
    # Si es regresión logística
    if hasattr(model, "coef_"):
        print(model.coef_)
    elif hasattr(model.named_steps['classifier'], "coef_"):
        print(model.named_steps['classifier'].coef_)
    else:
        print("No es un modelo lineal simple (es Random Forest, XGBoost, etc).")
except:
    pass