import streamlit as st

def page_app_alt():

    st.title("🧪 Test rápido – Modelo Phishing")
    st.caption("Ingreso manual de scores")

    st.divider()

    Fatiga_Global_Score = st.slider("Fatiga Global Score", 1.0, 5.0, 3.0, 0.1)
    Phish_Susceptibilidad  = st.slider("Phish – Susceptibilidad", 1.0, 5.0, 3.0, 0.1)
    Big5_Apertura = st.slider("Big5 – Apertura", 1.0, 5.0, 3.0, 0.1)
    Phish_Riesgo_Percibido = st.slider("Phish – Riesgo Percibido", 1.0, 5.0, 3.0, 0.1)

    Demo_Rol_Trabajo = st.selectbox(
        "Rol de trabajo",
        {
            "Liderazgo": 1,
            "Supervisión": 2,
            "Profesional / Analista": 3,
            "Otro": 4
        }.items(),
        format_func=lambda x: x[0]
    )[1]

    Demo_Horas = st.selectbox(
        "Horas diarias frente al computador",
        {
            "Menos de 2 horas": 1,
            "Entre 2 y 5 horas": 2,
            "Entre 5 y 8 horas": 3,
            "Entre 8 y 10 horas": 4,
            "Más de 10 horas": 5
        }.items(),
        format_func=lambda x: x[0]
    )[1]

    st.divider()

    if st.button("🚀 Evaluar susceptibilidad"):

        st.session_state.scores = {
            "Fatiga_Global_Score": Fatiga_Global_Score,
            "Phish_Susceptibilidad": Phish_Susceptibilidad,
            "Big5_Apertura": Big5_Apertura,
            "Phish_Riesgo_Percibido": Phish_Riesgo_Percibido,
            "Demo_Rol_Trabajo": Demo_Rol_Trabajo,
            "Demo_Horas": Demo_Horas
        }

        # Limpiar estado previo
        for k in ["prediction", "logged"]:
            st.session_state.pop(k, None)

        # IR A RESULTADOS
        st.session_state.page = 99
        st.rerun()
