import streamlit as st

# -----------------------------
# Catálogos / codificaciones
# -----------------------------

COUNTRIES = {
    "Chile": 35,
    "Argentina": 32,
    "Brasil": 36,
    "Colombia": 37,
    "México": 52,
    "Perú": 51,
    "Otro": 999
}

ORG_TYPE = {
    "Pública": 1,
    "Privada": 2,
    "Sin fines de lucro": 3,
    "Otra": 4
}

EMPLOYEES = {
    "100 o menos": 1,
    "Entre 100 y 500": 2,
    "Entre 500 y 1.000": 3,
    "Entre 1.000 y 3.000": 4,
    "Entre 3.000 y 10.000": 5,
    "Entre 10.000 y 50.000": 6,
    "Superior a 50.000": 7
}

ROLE = {
    "Liderazgo (Director, Gerencia, SubGerencia, otros)": 1,
    "Supervisión y Control (Supervisor, Jefatura)": 2,
    "Administrativo, Analista, Ingeniero": 3,
    "Otra": 4
}

GENERATION = {
    "Tradicionalistas (1928–1945)": 1,
    "Baby Boomers (1946–1964)": 2,
    "Generación X (1965–1979)": 3,
    "Generación Y / Millennials (1980–1995)": 4,
    "Generación Z (1996 o posterior)": 5
}

GENDER = {
    "Masculino": 1,
    "Femenino": 2,
    "No Binario": 3
}

EDUCATION = {
    "Educación básica / primaria": 1,
    "Grado Universitario / Licenciado": 2,
    "Diploma / Postítulo": 3,
    "Magíster / MBA / MSc": 4,
    "Doctorado": 5
}

# -----------------------------
# Página demográfica
# -----------------------------

def page_demographics():

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    st.markdown("## 📋 Información Demográfica")
    st.write("Por favor complete la siguiente información.")
    st.divider()

    # -----------------------------
    # País
    # -----------------------------
    country = st.selectbox(
        "Seleccione el país donde reside",
        options=list(COUNTRIES.keys()),
        index=None
    )

    # -----------------------------
    # Tipo de organización
    # -----------------------------
    org_type = st.radio(
        "Seleccione el tipo de organización",
        options=list(ORG_TYPE.keys())
    )

    # -----------------------------
    # Industria (texto libre controlado)
    # -----------------------------
    industry = st.text_input(
        "Seleccione la industria a la cual pertenece su organización"
    )

    # -----------------------------
    # Tamaño organización
    # -----------------------------
    employees = st.radio(
        "Seleccione el número de colaboradores que trabajan en su organización",
        options=list(EMPLOYEES.keys())
    )

    # -----------------------------
    # Rol
    # -----------------------------
    role = st.radio(
        "Seleccione lo que define mejor su rol en su puesto de trabajo actual",
        options=list(ROLE.keys())
    )

    # -----------------------------
    # Generación
    # -----------------------------
    generation = st.radio(
        "Seleccione a qué generación pertenece",
        options=list(GENERATION.keys())
    )

    # -----------------------------
    # Género
    # -----------------------------
    gender = st.radio(
        "¿Qué describe mejor su género?",
        options=list(GENDER.keys())
    )

    # -----------------------------
    # Educación
    # -----------------------------
    education = st.radio(
        "Seleccione su nivel más alto de educación",
        options=list(EDUCATION.keys())
    )

    # -----------------------------
    # Validación
    # -----------------------------
    all_answered = all([
        country,
        org_type,
        industry.strip() != "",
        employees,
        role,
        generation,
        gender,
        education
    ])

    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.button("⬅️ Atrás", on_click=lambda: st.session_state.update(page=12))

    with col2:
        if not all_answered:
            st.button("Finalizar", disabled=True)
            st.warning("Debe completar todas las preguntas.")
        else:
            if st.button("Finalizar"):
                st.session_state.responses.update({
                    "COUNTRY": COUNTRIES[country],
                    "ORG_TYPE": ORG_TYPE[org_type],
                    "INDUSTRY": industry,
                    "EMPLOYEES": EMPLOYEES[employees],
                    "ROLE": ROLE[role],
                    "GENERATION": GENERATION[generation],
                    "GENDER": GENDER[gender],
                    "EDUCATION": EDUCATION[education],
                })
                st.session_state.page = 99
