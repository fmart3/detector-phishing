import joblib
import pandas as pd
import sys
import os

# ==============================================================================
# BLOQUE DE AJUSTE DE RUTAS (AGREGAR ESTO AL INICIO)
# ==============================================================================
# 1. Obtener la ruta absoluta de la carpeta donde está este script (misc)
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Obtener la ruta raíz del proyecto (un nivel arriba de misc)
project_root = os.path.abspath(os.path.join(current_script_dir, '..'))

# 3. Agregar la raíz al 'sys.path' para poder importar 'utils'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 4. CAMBIAR EL DIRECTORIO DE TRABAJO A LA RAÍZ
# Esto es vital: hace que cuando los otros scripts busquen "questions.json" 
# o ".env", los encuentren en la raíz y no busquen en 'misc'.
os.chdir(project_root)
# ==============================================================================

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