import streamlit as st
from utils.scales import LIKERT_5, invert_likert

def render_likert_page(
    title: str,
    description: str,
    questions: list,
    next_page: int,
    prev_page: int | None = None
):
    """
    Renderiza encuesta en formato VERTICAL (Lista).
    Es más amigable para lectura y dispositivos móviles.
    """

    # -----------------------------
    # 0. Estilos CSS (Tarjetas Limpias)
    # -----------------------------
    st.markdown("""
        <style>
        /* Tarjeta de la pregunta */
        .question-card {
            background-color: #262730; 
            padding: 20px 25px; 
            border-radius: 10px;
            margin-bottom: 10px; /* Margen inferior pequeño, la opción viene pegada */
            border: 1px solid #41444e;
            border-bottom: none; /* Unimos visualmente con las opciones */
            border-bottom-left-radius: 0;
            border-bottom-right-radius: 0;
        }
        
        /* Contenedor de las opciones */
        .options-container {
            background-color: #262730;
            border: 1px solid #41444e;
            border-top: none;
            border-bottom-left-radius: 10px;
            border-bottom-right-radius: 10px;
            padding: 0px 25px 20px 25px;
            margin-bottom: 30px; /* Espacio entre preguntas */
        }

        .question-text {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
        }

        /* Ajustes al Radio Button Vertical */
        div.row-widget.stRadio > div[role="radiogroup"] {
            gap: 10px; /* Espacio entre opciones */
        }
        
        /* Hacer que el texto de las opciones sea más legible */
        div.row-widget.stRadio label div[data-testid="stMarkdownContainer"] p {
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    # -----------------------------
    # 1. Configuración de Opciones
    # -----------------------------
    # Definimos las etiquetas de texto explícitas para la UI
    # Asumimos una escala estándar de 5 puntos
    options_text = [
        "Muy en desacuerdo",             # Valor 1
        "En desacuerdo",                 # Valor 2
        "Ni de acuerdo ni en desacuerdo",# Valor 3
        "De acuerdo",                    # Valor 4
        "Muy de acuerdo"                 # Valor 5
    ]
    
    # Mapeo inverso: Texto -> Número (Para guardar en la BD/Lógica)
    text_to_score = {
        "Muy en desacuerdo": 1,
        "En desacuerdo": 2,
        "Ni de acuerdo ni en desacuerdo": 3,
        "De acuerdo": 4,
        "Muy de acuerdo": 5
    }

    # -----------------------------
    # 2. Inicialización
    # -----------------------------
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "page" not in st.session_state:
        st.session_state.page = 1

    # -----------------------------
    # 3. Header
    # -----------------------------
    st.title(title)
    st.write(description)
    st.divider()

    unanswered = []
    
    # -----------------------------
    # 4. Renderizado de Preguntas
    # -----------------------------
    for i, q in enumerate(questions):
        
        # --- A. TARJETA VISUAL DE LA PREGUNTA ---
        st.markdown(f"""
        <div class="question-card">
            <div class="question-text">{i+1}. {q['text']}</div>
        </div>
        <div class="options-container">
        """, unsafe_allow_html=True)
        # Nota: Abrimos un div "options-container" pero lo cerraremos después del radio
        
        # --- B. RECUPERAR ESTADO PREVIO ---
        saved_score = st.session_state.responses.get(q["code"])
        
        # Si la pregunta es reversa, el valor guardado ya está invertido (ej: guardó 5, pero el usuario marcó 1)
        # Para mostrarlo en la UI, debemos "des-invertirlo" para saber qué botón marcó el usuario visualmente.
        ui_score = saved_score
        if saved_score is not None and q.get("reverse", False):
            ui_score = invert_likert(saved_score)

        # Convertir el Score numérico (1-5) al Texto de la opción
        # Si ui_score es 1 -> index 0 ("Muy en desacuerdo")
        current_selection_index = None
        if ui_score is not None and 1 <= ui_score <= 5:
            current_selection_index = ui_score - 1

        # --- C. WIDGET DE SELECCIÓN VERTICAL ---
        selection_text = st.radio(
            label=q['text'], # Invisible por label_visibility
            options=options_text,
            index=current_selection_index,
            key=f"{q['code']}_ui",
            label_visibility="collapsed" # Ocultamos el label repetido
        )

        # Cerraremos el contenedor visual
        st.markdown("</div>", unsafe_allow_html=True)

        # --- D. GUARDAR RESPUESTA ---
        if selection_text is None:
            # Esto pasa la primera vez si index es None
            unanswered.append(q["code"])
        else:
            # 1. Convertir texto a número
            raw_score = text_to_score[selection_text]
            
            # 2. Aplicar lógica de inversión si es necesario
            final_score = raw_score
            if q.get("reverse", False):
                final_score = invert_likert(raw_score)
            
            # 3. Guardar
            st.session_state.responses[q["code"]] = final_score

    st.divider()

    # -----------------------------
    # 5. Navegación
    # -----------------------------
    col1, col2, col3 = st.columns([1, 3, 1])

    if prev_page is not None:
        with col1:
            st.button("⬅️ Atrás", on_click=lambda: st.session_state.update(page=prev_page), use_container_width=True)

    with col3:
        btn_disabled = len(unanswered) > 0
        btn_text = f"Faltan {len(unanswered)}" if btn_disabled else "Siguiente ➡️"
        
        st.button(
            btn_text,
            disabled=btn_disabled,
            on_click=lambda: st.session_state.update(page=next_page),
            type="primary" if not btn_disabled else "secondary",
            use_container_width=True
        )