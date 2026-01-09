🛡️ Phishing Susceptibility Detection System

Sistema de detección de susceptibilidad a phishing basado en factores humanos, entrenado con Gradient Boosting, desplegado en Databricks Model Serving e integrado con Streamlit y Evidently AI para monitoreo.

📐 Arquitectura General
Google Colab
  └── Entrenamiento del modelo (MLflow)
        └── Registro en Databricks (Unity Catalog)
              └── Databricks Model Serving (Endpoint REST)
                    └── Streamlit App (Predicción en tiempo real)
                          └── Evidently AI (Drift & Monitoring)

🔁 Flujo de Actualización del Modelo (ALTA IMPORTANCIA)

Cuando se entrena un nuevo modelo, NO se crea un nuevo endpoint.
Se actualiza la versión del modelo servido.

1️⃣ Entrenamiento del Modelo (Google Colab)

El entrenamiento se realiza en Google Colab, usando mlflow conectado a Databricks.

Requisitos

Token de Databricks

URI del Workspace

MLflow configurado con Unity Catalog

import mlflow
mlflow.set_registry_uri("databricks-uc")


El modelo se registra siempre con el mismo nombre:

registered_model_name = "workspace.default.phishing_detector_tree"


📌 Importante
Cada entrenamiento crea una nueva versión:

v1, v2, v3, ...

2️⃣ Verificar la Nueva Versión en Databricks

En Databricks Workspace:

Ir a Models

Buscar phishing_detector_tree

Verificar:

Nueva versión creada

Métricas correctas

Signature definida (obligatorio)

⚠️ Databricks exige signature (input + output).

3️⃣ Actualizar el Modelo en Serving (PASO CRÍTICO)
NO crear un endpoint nuevo ❌
Actualizar el modelo servido en el endpoint existente ✅
🔧 Pasos en Databricks UI

Ir a Serving

Seleccionar el endpoint (ej: api_phishing)

Click en Edit / Update configuration

En Served Models:

Cambiar la versión del modelo
Ejemplo:

phishing_detector_tree : v3


Guardar cambios

⏳ El endpoint se reinicia automáticamente.

4️⃣ Verificar el Endpoint
Endpoint URL
https://<DATABRICKS-HOST>/serving-endpoints/api_phishing/invocations

Headers requeridos
Authorization: Bearer <DATABRICKS_TOKEN>
Content-Type: application/json

Payload esperado
{
  "dataframe_records": [
    {
      "Fatiga_Global_Score": 1.8,
      "Big5_Responsabilidad": 3.9,
      "Big5_Apertura": 4.1,
      "Demo_Generacion_Edad": 3,
      "Demo_Rol_Trabajo": 2,
      "Demo_Horas": 4
    }
  ]
}

5️⃣ Cambios en Streamlit (Si aplica)

⚠️ Normalmente NO es necesario cambiar nada si:

Las features se mantienen

El schema del modelo no cambia

Solo revisar si:

Se agregan nuevas variables

Se cambia el orden / nombre de columnas

6️⃣ Logging de Predicciones (Producción)

Las predicciones se almacenan localmente en:

production_predictions.csv


Cada registro contiene:

Timestamp

Features de entrada

Predicción del modelo

Este archivo se utiliza para:

Evidently AI

Análisis de drift

Auditoría de decisiones

7️⃣ Evidently AI (Monitoreo)

El monitoreo se ejecuta desde la app Streamlit.

Baseline requerido

Archivo:

training_baseline.csv


Ubicación recomendada:

/data/training_baseline.csv


Este archivo contiene:

Features del dataset de entrenamiento

Sin la variable objetivo

Generación del Reporte

Desde la página de resultados:

Click en 📈 Generar reporte de monitoreo

Se genera:

evidently_phishing_report.html


Se renderiza directamente en la app

📌 Nota:
El análisis de clasificación (accuracy, recall, etc.) NO se ejecuta si no existe target real en producción.

⚠️ Consideraciones Importantes de Databricks
Community / No Full Version

❌ No hay Inference Tables

❌ No hay Auto-logging en Serving

❌ No hay Jobs programados

Por eso:

El logging se hace desde la app

Evidently corre localmente

Errores Comunes
Error	Causa
ENDPOINT_NOT_FOUND	URL incorrecta
Model has no signature	Modelo registrado sin signature
ConnectionClosedError	Red pública / firewall
probability = null	Modelo no expone predict_proba
📌 Buenas Prácticas

✔ Mantener el mismo nombre de modelo
✔ Versionar solo el modelo, no el endpoint
✔ No entrenar en Databricks si no es necesario
✔ Usar Evidently para drift, no para accuracy en prod
✔ Documentar cada cambio de versión

📄 Archivos Clave del Repositorio
├── app.py
├── pages/
│   └── results.py
├── utils/
│   ├── databricks.py
│   ├── scoring.py
│   └── logging.py
├── data/
│   └── training_baseline.csv
├── production_predictions.csv
└── README.md

👤 Autor

Proyecto académico / aplicado en ciberseguridad y factores humanos.
Enfocado en prevención, concientización y riesgo humano.
