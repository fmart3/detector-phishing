import pandas as pd
import joblib
import os
import sys

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

# ==========================================
# CONFIGURACIÓN
# ==========================================
MODEL_PATH = "phishing_model.pkl"

# Estas son las columnas EXACTAS que mencionaste que usa tu modelo
FEATURES_ORDER = [
    'Demo_Tamano_Org',
    'Demo_Rol_Trabajo',
    'Big5_Apertura',
    'Demo_Horas',
    'Phish_Riesgo_Percibido',
    'Fatiga_Global_Score'
]

def load_model():
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: No se encuentra el archivo '{MODEL_PATH}' en esta carpeta.")
        sys.exit(1)
    try:
        model = joblib.load(MODEL_PATH)
        print(f"✅ Modelo cargado correctamente: {type(model).__name__}")
        return model
    except Exception as e:
        print(f"❌ Error cargando el modelo: {e}")
        sys.exit(1)

def run_scenarios():
    model = load_model()

    print("\n--- 🧪 DEFINIENDO ESCENARIOS DE PRUEBA ---")

    # Definimos una lista de diccionarios. Cada uno es un "usuario simulado".
    scenarios_data = [
        # CASO 1: El usuario "Ideal" (Descansado, horas normales, alta percepción de riesgo)
        {
            "Nombre": "Usuario Seguro",
            "Demo_Tamano_Org": 3,      # Empresa mediana
            "Demo_Rol_Trabajo": 1,     # Rol estándar
            "Big5_Apertura": 3.5,      # Apertura media
            "Demo_Horas": 8.0,         # Jornada normal
            "Phish_Riesgo_Percibido": 5.0, # Percibe mucho riesgo (Alerta)
            "Fatiga_Global_Score": 1.0 # Nada de fatiga
        },
        
        # CASO 2: El usuario "En Riesgo" (Agotado, muchas horas, baja percepción)
        {
            "Nombre": "Usuario Vulnerable",
            "Demo_Tamano_Org": 3,
            "Demo_Rol_Trabajo": 1,
            "Big5_Apertura": 3.5,
            "Demo_Horas": 12.0,        # Jornada muy larga
            "Phish_Riesgo_Percibido": 1.0, # Cree que no hay riesgo (Confiado)
            "Fatiga_Global_Score": 5.0 # Fatiga máxima
        },

        # CASO 3: Probando impacto de Tamaño Organización (Empresa Grande)
        {
            "Nombre": "Empresa Grande",
            "Demo_Tamano_Org": 5,      # Org muy grande
            "Demo_Rol_Trabajo": 3,
            "Big5_Apertura": 3.0,
            "Demo_Horas": 9.0,
            "Phish_Riesgo_Percibido": 3.0,
            "Fatiga_Global_Score": 3.0
        },

        # CASO 4: Probando impacto de Apertura (Muy curioso/abierto)
        {
            "Nombre": "Alta Apertura",
            "Demo_Tamano_Org": 3,
            "Demo_Rol_Trabajo": 1,
            "Big5_Apertura": 5.0,      # Máxima apertura (¿Más curioso = más clics?)
            "Demo_Horas": 8.0,
            "Phish_Riesgo_Percibido": 3.0,
            "Fatiga_Global_Score": 3.0
        }
    ]

    # Convertimos a DataFrame
    df_scenarios = pd.DataFrame(scenarios_data)

    # Separamos la columna de nombres para visualización, y dejamos solo los features para el modelo
    X_test = df_scenarios[FEATURES_ORDER]
    
    print("\n--- 🤖 EJECUTANDO PREDICCIONES ---")
    
    try:
        # Predecir probabilidades (nos interesa la clase 1 = Susceptible)
        # predict_proba devuelve [[prob_clase0, prob_clase1], ...]
        probs = model.predict_proba(X_test)[:, 1]
        
        # Predecir clase directa (0 o 1)
        preds = model.predict(X_test)
        
        # Unir resultados para mostrar
        results = df_scenarios.copy()
        results['Probabilidad_Phishing'] = probs
        results['Prediccion_Clase'] = preds
        
        # Formatear probabilidad a porcentaje
        results['Probabilidad (%)'] = (results['Probabilidad_Phishing'] * 100).round(2).astype(str) + '%'
        
        # Mostrar tabla limpia
        display_cols = ['Nombre', 'Probabilidad (%)', 'Prediccion_Clase'] + FEATURES_ORDER
        print(results[display_cols].to_string(index=False))
        
        print("\n" + "="*60)
        print("INTERPRETACIÓN RÁPIDA:")
        for index, row in results.iterrows():
            riesgo = "🔴 ALTO" if row['Probabilidad_Phishing'] > 0.7 else \
                     "🟡 MEDIO" if row['Probabilidad_Phishing'] > 0.4 else "🟢 BAJO"
            
            print(f"📌 {row['Nombre']}: {riesgo} ({row['Probabilidad (%)']})")
            
    except Exception as e:
        print(f"❌ Error al predecir: {e}")
        print("💡 Consejo: Verifica que los nombres de las columnas en 'FEATURES_ORDER' coincidan exactamente con tu entrenamiento.")

# --- PRUEBA DE SENSIBILIDAD A LA FATIGA ---
def run_fatigue_sensitivity():
    print("\n\n--- 📈 ANÁLISIS DE SENSIBILIDAD: FATIGA ---")
    print("Manteniendo todo constante y solo subiendo la fatiga de 1 a 5...")
    
    model = load_model()
    
    # Base: Usuario promedio
    base_user = {
        'Demo_Tamano_Org': 3,
        'Demo_Rol_Trabajo': 1,
        'Big5_Apertura': 3.0,
        'Demo_Horas': 9.0,
        'Phish_Riesgo_Percibido': 3.0,
        'Fatiga_Global_Score': 1.0 # Este valor cambiará
    }
    
    data = []
    for fatiga in [1.0, 2.0, 3.0, 4.0, 5.0]:
        row = base_user.copy()
        row['Fatiga_Global_Score'] = fatiga
        data.append(row)
        
    df = pd.DataFrame(data)[FEATURES_ORDER]
    probs = model.predict_proba(df)[:, 1]
    
    print(f"{'Fatiga Score':<15} | {'Probabilidad Phishing'}")
    print("-" * 40)
    for f, p in zip(df['Fatiga_Global_Score'], probs):
        bar = "█" * int(p * 20)
        print(f"{f:<15} | {p:.4f}  {bar}")

if __name__ == "__main__":
    run_scenarios()
    run_fatigue_sensitivity()