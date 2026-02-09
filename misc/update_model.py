import os
import sys
import shutil

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

# --- CARGA DE SECRETOS ---
try:
    from dotenv import load_dotenv
    load_dotenv() 
    print("🔐 Secretos cargados desde .env.")
except ImportError:
    print("⚠️ 'python-dotenv' no instalado. Usando variables de entorno del sistema.")

# --- CONFIGURACIÓN ---
# 🚨 AJUSTA ESTO PARA QUE COINCIDA CON LO QUE PUSISTE EN EL NOTEBOOK
CATALOGO = "phishing"              # Tu catálogo en Databricks
ESQUEMA = "default"                # Tu esquema
NOMBRE_MODELO = "Phishing_Detector_Model" # El nombre que definimos en el notebook
FULL_MODEL_NAME = f"{CATALOGO}.{ESQUEMA}.{NOMBRE_MODELO}"

ALIAS = "Champion"                 # La etiqueta del ganador
OUTPUT_FILE = "phishing_model.pkl" # Nombre del archivo final en tu PC

print("--- ACTUALIZADOR DE MODELO PHISHING (MODO UNITY CATALOG) ---")

try:
    import mlflow
    import mlflow.sklearn
    import joblib
    print("✅ Librerías cargadas.")
except ImportError:
    print("❌ Faltan librerías. Ejecuta: pip install mlflow pandas python-dotenv joblib")
    sys.exit(1)

def download_phishing_model():
    # 1. Validar Credenciales
    token = os.environ.get("DATABRICKS_TOKEN")
    host = os.environ.get("DATABRICKS_HOST")
    
    if not token or not host:
        print("❌ Error: Faltan credenciales DATABRICKS_HOST o DATABRICKS_TOKEN.")
        return

    print(f"🔄 Conectando a Databricks ({host})...")
    
    # 2. Configurar MLflow para Unity Catalog
    mlflow.set_tracking_uri("databricks")
    mlflow.set_registry_uri("databricks-uc") 
    
    try:
        # 3. Construir la URI del Modelo Champion
        model_uri = f"models:/{FULL_MODEL_NAME}@{ALIAS}"
        
        print(f"🔍 Buscando modelo certificado: {model_uri}")
        print(f"📥 Descargando Pipeline completo...")
        
        # 4. Cargar el Pipeline directamente desde Databricks
        loaded_pipeline = mlflow.sklearn.load_model(model_uri)
        
        # 5. Guardar en disco local
        joblib.dump(loaded_pipeline, OUTPUT_FILE)
        
        print("-" * 50)
        print(f"🎉 ¡ÉXITO! Se ha descargado el modelo de Phishing.")
        print(f"📂 Archivo guardado: {OUTPUT_FILE}")
        print("   Este archivo contiene el Scaler y el Modelo listos para predecir.")
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error descargando el modelo: {e}")
        print("💡 Consejo: Verifica que hayas ejecutado el Notebook de entrenamiento y que el Alias 'Champion' exista.")

if __name__ == "__main__":
    download_phishing_model()