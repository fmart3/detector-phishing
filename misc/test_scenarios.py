import pandas as pd
import joblib
import os
import sys
import itertools
from IPython.display import display

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

    if model is None: return

    print(f"✅ Modelo cargado: {type(model).__name__}")
    print("\n--- 🧪 EJECUTANDO ESCENARIOS BASADOS EN EVIDENCIA ---")

    scenarios_data = [
        # CASO 1: EL INMUNIZADO (Bajo riesgo en todo)
        # Org pequeña, pocas horas, PERCIBE EL RIESGO (5.0), poca apertura.
        {
            "Nombre": "🛡️ Usuario Blindado",
            "Demo_Tamano_Org": 1,       # 100 o menos
            "Demo_Rol_Trabajo": 1,      # Administrativo
            "Big5_Apertura": 1.0,       # Poca curiosidad
            "Demo_Horas": 2,            # 2-5 horas
            "Phish_Riesgo_Percibido": 5.0, # "¡Tengo mucho miedo de caer!" (Alerta máxima)
            "Fatiga_Global_Score": 1.0  # Fresco como una lechuga
        },
        
        # CASO 2: LA VÍCTIMA PERFECTA (Basado en tu escáner: 99.9% Riesgo)
        # Org gigante, +10 horas, CONFIADO (Riesgo 1.0), Fatiga Alta, Curioso
        {
            "Nombre": "💣 Víctima Perfecta",
            "Demo_Tamano_Org": 7,       # >50.000
            "Demo_Rol_Trabajo": 3,      # Rol técnico/específico
            "Big5_Apertura": 5.0,       # Muy curioso
            "Demo_Horas": 5,            # >10 horas
            "Phish_Riesgo_Percibido": 1.0, # "Esto no me va a pasar a mí" (Exceso confianza)
            "Fatiga_Global_Score": 1.0  # Agotado
        },

        # CASO 3: EL EMPLEADO PROMEDIO (Riesgo Medio)
        # Org mediana, horas normales, fatiga media
        {
            "Nombre": "😐 Usuario Promedio",
            "Demo_Tamano_Org": 4,       # 1000-3000
            "Demo_Rol_Trabajo": 3,
            "Big5_Apertura": 3.0,
            "Demo_Horas": 3,            # 5-8 horas
            "Phish_Riesgo_Percibido": 4.5,
            "Fatiga_Global_Score": 3.0
        },

        # CASO 4: EL CURIOSO PELIGROSO
        # Perfil seguro, pero DEMASIADO curioso (Apertura 5)
        {
            "Nombre": "👀 El Curioso",
            "Demo_Tamano_Org": 4,
            "Demo_Rol_Trabajo": 3,
            "Big5_Apertura": 5.0,       # <--- Factor de riesgo
            "Demo_Horas": 3,
            "Phish_Riesgo_Percibido": 5.0, # Alerta, pero...
            "Fatiga_Global_Score": 3.0
        }
    ]
    
    df_scenarios = pd.DataFrame(scenarios_data)
    X_test = df_scenarios[FEATURES_ORDER]

    try:
        probs = model.predict_proba(X_test)[:, 1]
        
        results = df_scenarios.copy()
        results['Riesgo_Detectado'] = (probs * 100).round(2)
        
        # Mostrar tabla limpia
        display_cols = ['Nombre', 'Riesgo_Detectado'] + FEATURES_ORDER
        
        print(f"{'NOMBRE':<20} | {'RIESGO':<10} | {'CONCLUSIÓN'}")
        print("-" * 50)
        for index, row in results.iterrows():
            p = row['Riesgo_Detectado']
            if p > 80:
                conclusion = "🔴 CRÍTICO: ¡Va a caer!"
            elif p > 40:
                conclusion = "🟡 ALERTA: Posible víctima"
            else:
                conclusion = "🟢 SEGURO: Difícil de engañar"
            
            print(f"{row['Nombre']:<20} | {p:>6}%   | {conclusion}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# --- PRUEBA DE SENSIBILIDAD A LA FATIGA ---
def run_fatigue_sensitivity():
    print("\n\n--- 📈 ANÁLISIS DE SENSIBILIDAD: FATIGA ---")
    print("Manteniendo todo constante y solo subiendo la fatiga de 1 a 5...")
    
    model = load_model()
    
    # Base: Usuario promedio
    base_user = {
        'Demo_Tamano_Org': 3,
        'Demo_Rol_Trabajo': 3,
        'Big5_Apertura': 3.0,
        'Demo_Horas': 3,
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

# # 1. Cargar el modelo
# model = joblib.load("phishing_model.pkl")

# features = [
#     'Demo_Tamano_Org', 'Demo_Rol_Trabajo', 'Big5_Apertura',
#     'Demo_Horas', 'Phish_Riesgo_Percibido', 'Fatiga_Global_Score'
# ]

# print("--- 🕵️ ESCANER DE VULNERABILIDAD ---")
# print("Probando combinaciones para encontrar qué dispara la alerta...")

# # 2. Definir los rangos posibles basados en lo que me has confirmado
# # Usamos pasos lógicos para no explotar la memoria, pero cubriendo los extremos
# rangos = {
#     'Demo_Tamano_Org': [1, 4, 7],        # Pequeña, Mediana, Gigante
#     'Demo_Rol_Trabajo': [1, 2, 3, 4],    # Probamos varios roles
#     'Big5_Apertura': [1.0, 3.0, 5.0],    # Baja, Media, Alta
#     'Demo_Horas': [1, 3, 5],             # Pocas, Normal, Muchas (10+)
#     'Phish_Riesgo_Percibido': [1.0, 3.0, 5.0], # Bajo, Medio, Alto
#     'Fatiga_Global_Score': [1.0, 3.0, 5.0]     # Baja, Media, Alta
# }

# # 3. Generar todas las combinaciones posibles (Producto Cartesiano)
# keys, values = zip(*rangos.items())
# permutations = [dict(zip(keys, v)) for v in itertools.product(*values)]
# df_simulado = pd.DataFrame(permutations)

# # Asegurar el orden correcto de columnas
# df_simulado = df_simulado[features]

# # 4. Predecir masivamente
# probs = model.predict_proba(df_simulado)[:, 1]
# df_simulado['Probabilidad_Riesgo'] = probs

# # 5. Mostrar los ganadores (El Top 5 de Riesgo)
# top_riesgo = df_simulado.sort_values(by='Probabilidad_Riesgo', ascending=False).head(5)

# print(f"\n✅ Se analizaron {len(df_simulado)} perfiles simulados.")
# print("\n🔥 TOP 5 PERFILES MÁS RIESGOSOS DETECTADOS POR EL MODELO:")
# print("=" * 80)
# # Formato bonito
# display_cols = ['Probabilidad_Riesgo'] + features
# # Convertir a porcentaje para leer mejor
# top_riesgo_view = top_riesgo.copy()
# top_riesgo_view['Probabilidad_Riesgo'] = (top_riesgo_view['Probabilidad_Riesgo'] * 100).round(2).astype(str) + '%'

# try:
#     display(top_riesgo_view[display_cols])
# except:
#     print(top_riesgo_view[display_cols].to_string())

# print("\n💡 CONCLUSIÓN:")
# print("Mira la columna 'Fatiga' y 'Riesgo Percibido' en el Top 1.")
# print("Esos son los valores EXACTOS que tu modelo odia.")