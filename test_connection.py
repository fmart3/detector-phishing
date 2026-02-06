import os
import requests
from databricks import sql
from dotenv import load_dotenv
import pytz
from datetime import datetime

# Cargar variables
load_dotenv()

print("\n🔍 --- DIAGNÓSTICO DE CONEXIÓN ---")

# 1. VERIFICAR VARIABLES
host = os.getenv("DATABRICKS_HOST")
token = os.getenv("DATABRICKS_TOKEN")
http_path = os.getenv("DATABRICKS_HTTP_PATH")

print(f"1. Variables .env:")
print(f"   - HOST:      {'✅ OK' if host else '❌ FALTA'}")
print(f"   - TOKEN:     {'✅ OK' if token else '❌ FALTA'}")
print(f"   - HTTP_PATH: {'✅ OK' if http_path else '❌ FALTA'}")

if not (host and token and http_path):
    print("\n⚠️ DETENIDO: Crea un archivo .env con tus credenciales.")
    exit()

# 2. VERIFICAR FORMATO HOST
if not host.startswith("https://"):
    print("   ⚠️ ADVERTENCIA: DATABRICKS_HOST debería empezar con 'https://'")

# 3. PROBAR CONEXIÓN SQL (BASE DE DATOS)
print("\n2. Probando Base de Datos (SQL)...")
try:
    server_hostname = host.replace("https://", "").replace("http://", "").rstrip("/")
    with sql.connect(server_hostname=server_hostname, http_path=http_path, access_token=token) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("   ✅ ¡Conexión SQL EXITOSA!")
except Exception as e:
    print(f"   ❌ FALLÓ SQL: {e}")

# 4. PROBAR CONEXIÓN MODELO (ENDPOINT)
print("\n3. Probando Modelo (Endpoint)...")
endpoint_name = "phishing-endpoint" # Asegúrate que este sea el nombre correcto
url = f"{host.rstrip('/')}/serving-endpoints/{endpoint_name}/invocations"
headers = {"Authorization": f"Bearer {token}"}
try:
    # Enviamos un JSON vacío solo para ver si responde (esperamos 400 o 200, no ConnectionError)
    res = requests.post(url, headers=headers, json={}, timeout=5)
    if res.status_code in [200, 400, 422]:
        print(f"   ✅ El Endpoint es ALCANZABLE (Status {res.status_code})")
    elif res.status_code == 404:
        print(f"   ❌ Error 404: No existe el endpoint '{endpoint_name}'. Revisa el nombre en databricks.py.")
    elif res.status_code == 403:
        print("   ❌ Error 403: Token inválido o sin permisos.")
    else:
        print(f"   ⚠️ Respuesta: {res.status_code}")
except Exception as e:
    print(f"   ❌ FALLÓ CONEXIÓN MODELO: {e}")

# 5. PROBAR HORA CHILE
print("\n4. Probando Librería de Tiempo...")
try:
    cl_time = datetime.now(pytz.timezone("America/Santiago"))
    print(f"   ✅ Hora Chile Actual: {cl_time.strftime('%H:%M:%S')}")
except Exception as e:
    print(f"   ❌ Error con pytz: {e}. Ejecuta: pip install pytz")

print("\n-----------------------------------\n")