import streamlit as st

def page_app_alt():

    st.markdown("## ⚡ Modo Rápido – Testing Full Pipeline")
    st.caption("Ingreso manual de scores + demografía (solo enteros)")

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    r = st.session_state.responses

    # =====================================================
    # SCORES PSICOLÓGICOS (1–5)
    # =====================================================
    st.divider()
    st.markdown("### 🧠 Big Five")

    r["Big5_Extraversion"]     = st.number_input("Extraversion", 1, 5, 3)
    r["Big5_Amabilidad"]       = st.number_input("Amabilidad", 1, 5, 3)
    r["Big5_Responsabilidad"]  = st.number_input("Responsabilidad", 1, 5, 3)
    r["Big5_Neuroticismo"]     = st.number_input("Neuroticismo", 1, 5, 3)
    r["Big5_Apertura"]         = st.number_input("Apertura", 1, 5, 3)

    st.divider()
    st.markdown("### 🎣 Phishing")

    r["Phish_Actitud_Riesgo"]      = st.number_input("Actitud al Riesgo", 1, 5, 3)
    r["Phish_Awareness"]           = st.number_input("Awareness", 1, 5, 3)
    r["Phish_Riesgo_Percibido"]    = st.number_input("Riesgo Percibido", 1, 5, 3)
    r["Phish_Autoeficacia"]        = st.number_input("Autoeficacia", 1, 5, 3)
    r["Phish_Susceptibilidad"]     = st.number_input("Susceptibilidad", 1, 5, 3)

    st.divider()
    st.markdown("### 😵 Fatiga Digital")

    r["Fatiga_Emocional"]  = st.number_input("Fatiga Emocional", 1, 5, 3)
    r["Fatiga_Cinismo"]    = st.number_input("Fatiga Cinismo", 1, 5, 3)
    r["Fatiga_Abandono"]   = st.number_input("Fatiga Abandono", 1, 5, 3)

    # =====================================================
    # DEMOGRAFÍA (MISMAS KEYS QUE PRODUCCIÓN)
    # =====================================================
    st.divider()
    st.markdown("### 👤 Demografía (codificada)")

    r["Demo_Pais"] = st.number_input(
        "País (1=Chile,2=Colombia,3=Honduras,4=México,5=Panamá)",
        1, 5, 1
    )

    r["Demo_Tipo_Organizacion"] = st.number_input(
        "Tipo Organización (1=Pública,2=Privada,3=Sin fines lucro,4=Otra)",
        1, 4, 2
    )

    r["Demo_Industria"] = st.number_input(
        "Industria (1–18)",
        1, 18, 4
    )

    r["Demo_Tamano_Org"] = st.number_input(
        "Tamaño Organización (1–7)",
        1, 7, 3
    )

    r["Demo_Rol_Trabajo"] = st.number_input(
        "Rol Trabajo (1=Liderazgo,2=Supervisión,3=Admin/Técnico,4=Otro)",
        1, 4, 3
    )

    r["Demo_Generacion_Edad"] = st.number_input(
        "Generación (1–5)",
        1, 5, 4
    )

    r["Demo_Genero"] = st.number_input(
        "Género (1=Masculino,2=Femenino,3=No Binario)",
        1, 3, 1
    )

    r["Demo_Nivel_Educacion"] = st.number_input(
        "Nivel Educación (1–5)",
        1, 5, 4
    )

    r["Demo_Horas"] = st.number_input(
        "Horas PC (1=<2h … 5=>10h)",
        1, 5, 3
    )

    # =====================================================
    # CONTROL
    # =====================================================
    st.divider()

    with st.expander("🧪 DEBUG – responses"):
        st.json(r)

    if st.button("🚀 Ir a resultados"):
        st.session_state.page = 99
        st.rerun()
