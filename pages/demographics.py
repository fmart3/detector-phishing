import streamlit as st

# -----------------------------
# Catálogos / codificaciones
# -----------------------------

COUNTRIES = {
    "Chile": 1,
    "Colombia": 2,
    "Honduras": 3,
    "México": 4,
    "Panamá": 5
}

ORG_TYPE = {
    "Pública": 1,
    "Privada": 2,
    "Sin fines de lucro": 3,
    "Otra": 4
}

INDUSTRY = {
    "Agricultura": 1,
    "Bancos o Financiera": 2,
    "Seguros": 3,
    "Tecnologia y/o Telecomunicaciones": 4,
    "Publicidad, Marketing y/o Comunicaciones": 5,
    "Transporte": 6,
    "Clinicas o Isapres (Salud)": 7,
    "Administradora Fondos de Pensiones": 8,
    "Sector Público": 9,
    "Energia": 10,
    "Mineria": 11,
    "Oil & Gas": 12,
    "Retail": 13,
    "Universidades o Educación": 14,
    "Servicios Profesionales y/o Consultoria": 15,
    "Construcción": 16,
    "Manufactura": 17,
    "Otras": 18
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

HOURS = {
    "Menos de 2 horas": 1,
    "Entre 2 y 5 horas": 2,
    "Entre 5 y 8 horas": 3,
    "Entre 8 y 10 horas": 4,
    "Más de 10 horas": 5
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

    # # -----------------------------
    # # País
    # # -----------------------------
    # country = st.selectbox(
    #     "Seleccione el país donde reside",
    #     options=list(COUNTRIES.keys()),
    #     index=None
    # )
    # st.session_state.responses["Demo_Pais"] = COUNTRIES[country]

    # # -----------------------------
    # # Tipo de organización
    # # -----------------------------
    # org_type = st.radio(
    #     "Seleccione el tipo de organización",
    #     options=list(ORG_TYPE.keys())
    # )
    # st.session_state.responses["Demo_Tipo_Organización"] = ORG_TYPE[org_type]

    # # -----------------------------
    # # Industria (texto libre controlado)
    # # -----------------------------
    # industry = st.selectbox(
    #     "Seleccione la industria a la cual pertenece su organización",
    #     options=list(INDUSTRY.keys()),
    #     index=None
    # )
    # st.session_state.responses["Demo_Industria"] = INDUSTRY[industry]

    # # -----------------------------
    # # Tamaño organización
    # # -----------------------------
    # employees = st.radio(
    #     "Seleccione el número de colaboradores que trabajan en su organización",
    #     options=list(EMPLOYEES.keys())
    # )
    # st.session_state.responses["Demo_Tamano_Org"] = EMPLOYEES[employees]

    # # -----------------------------
    # # Rol
    # # -----------------------------
    # role = st.radio(
    #     "Seleccione lo que define mejor su rol en su puesto de trabajo actual",
    #     options=list(ROLE.keys())
    # )
    # st.session_state.responses["Demo_Rol_Trabajo"] = ROLE[role]

    # # -----------------------------
    # # Generación
    # # -----------------------------
    # generation = st.radio(
    #     "Seleccione a qué generación pertenece",
    #     options=list(GENERATION.keys())
    # )
    # st.session_state.responses["Demo_Generacion_Edad"] = GENERATION[generation]

    # # -----------------------------
    # # Género
    # # -----------------------------
    # gender = st.radio(
    #     "¿Qué describe mejor su género?",
    #     options=list(GENDER.keys())
    # )
    # st.session_state.responses["Demo_Genero"] = GENDER[gender]
    
    # # -----------------------------
    # # Educación
    # # -----------------------------
    # education = st.radio(
    #     "Seleccione su nivel más alto de educación",
    #     options=list(EDUCATION.keys())
    # )
    # st.session_state.responses["Demo_Nivel_Educacion"] = EDUCATION[education]
    
    # # -----------------------------
    # # Horas en PC
    # # -----------------------------
    # hours = st.radio(
    #     "Seleccione las horas que está conectado a su computador de trabajo en el día",
    #     options=list(HOURS.keys())
    # )
    # st.session_state.responses["Demo_Horas"] = HOURS[hours]
    
    # Abres una Card
    st.markdown('<div class="bootstrap-card">', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        country = st.selectbox("País", list(COUNTRIES.keys()), index=None)
        org_type = st.selectbox("Tipo Organización", list(ORG_TYPE.keys()), index=None)
        industry = st.selectbox("Industria", list(INDUSTRY.keys()), index=None)
        employees = st.selectbox("Tamaño Empresa", list(EMPLOYEES.keys()), index=None)

    with c2:
        role = st.selectbox("Rol", list(ROLE.keys()), index=None)
        generation = st.selectbox("Generación", list(GENERATION.keys()), index=None)
        gender = st.selectbox("Género", list(GENDER.keys()), index=None)
        education = st.selectbox("Educación", list(EDUCATION.keys()), index=None)

    # La pregunta de horas puede ir abajo ocupando todo el ancho
    hours = st.radio("Horas conectado", list(HOURS.keys()), horizontal=True)

    st.markdown('</div>', unsafe_allow_html=True) # Cierras la Card

    # -----------------------------
    # Validación
    # -----------------------------
    all_answered = (
        country is not None and
        org_type is not None and
        industry is not None and
        employees is not None and
        role is not None and
        generation is not None and
        gender is not None and
        education is not None and
        hours is not None
    )

    st.divider()
    col1, col2 = st.columns([1, 1])

    with col1:
        # Botón atrás (ajusta el número de página según tu flujo)
        if st.button("⬅️ Atrás"):
            st.session_state.page -= 1
            st.rerun()

    with col2:
        if st.button("Finalizar", type="primary", disabled=not all_answered):
            
            # --- AQUÍ OCURRE LA MAGIA ---
            # Solo intentamos buscar en los diccionarios SI el usuario ya respondió.
            # Así evitamos el KeyError: None
            
            st.session_state.responses.update({
                "Demo_Pais": COUNTRIES[country],
                "Demo_Tipo_Organizacion": ORG_TYPE[org_type],
                "Demo_Industria": INDUSTRY[industry],
                "Demo_Tamano_Org": EMPLOYEES[employees],
                "Demo_Rol_Trabajo": ROLE[role],
                "Demo_Generacion_Edad": GENERATION[generation],
                "Demo_Genero": GENDER[gender],
                "Demo_Nivel_Educacion": EDUCATION[education],
                "Demo_Horas": HOURS[hours]
            })
            
            # Redirigir a resultados
            st.session_state.page = 99
            st.rerun()
        
        # Mensaje de ayuda si el botón está deshabilitado
        elif not all_answered:
            st.caption("⚠️ Complete todos los campos para finalizar.")