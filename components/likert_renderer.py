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
    Renderiza encuesta usando CSS GRID para forzar la distribución exacta.
    Divide el ancho en 5 columnas iguales (1fr cada una).
    """

    # -----------------------------
    # 0. CSS GRID (La solución definitiva)
    # -----------------------------
    st.markdown("""
        <style>
        /* 1. Tarjeta de la pregunta */
        .question-card {
            background-color: #262730; 
            padding: 20px 25px; 
            border-radius: 12px;
            margin-bottom: 25px;
            border: 1px solid #41444e;
        }
        
        .question-text {
            font-size: 19px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 15px;
        }

        /* 2. FORZAR GRID EN LOS RADIO BUTTONS */
        
        /* El contenedor principal de las opciones se convierte en una GRILLA de 5 columnas */
        div.row-widget.stRadio > div[role="radiogroup"] {
            display: grid !important;
            grid-template-columns: repeat(5, 1fr) !important; /* 5 Columnas Iguales */
            justify-items: center !important;     /* Centrar horizontalmente en su celda */
            width: 100% !important;               /* Ocupar todo el ancho disponible */
            gap: 0 !important;                    /* Sin espacios extraños */
        }

        /* Cada opción individual (Círculo + Número) */
        div.row-widget.stRadio > div[role="radiogroup"] > label {
            width: 100% !important;       /* Usa toda su celda de la grilla */
            display: flex !important;
            flex-direction: column !important; /* Número arriba/abajo del círculo */
            align-items: center !important;    /* Centrado perfecto */
            justify-content: center !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* El texto del número (1, 2, 3...) */
        div.row-widget.stRadio label div[data-testid="stMarkdownContainer"] p {
            font-size: 20px !important; 
            font-weight: bold;
            margin-bottom: 5px !important; 
        }

        /* Ocultar el indicador de foco azul feo si aparece */
        div.row-widget.stRadio > div[role="radiogroup"] > label:focus-within {
             background-color: transparent !important;
        }

        /* 3. Leyenda superior */
        .legend-box {
            background-color: #0e1117;
            border: 1px solid #41444e;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .legend-scale {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            color: #bdc2c9;
            padding: 0 5%; /* Padding para alinear visualmente con la grilla */
        }
        </style>
    """, unsafe_allow_html=True)

    # -----------------------------
    # 1. Inicialización
    # -----------------------------
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "page" not in st.session_state:
        st.session_state.page = 1

    # -----------------------------
    # 2. Header
    # -----------------------------
    st.title(title)
    st.write(description)
    
    st.markdown("""
    <div class="legend-box">
        <div style="text-align:center; font-weight:bold; margin-bottom:10px; color: white;">Escala de Acuerdo</div>
        <div class="legend-scale">
            <div style="text-align:center; width: 80px;">1<br><span style="font-size:12px">Muy en<br>Desacuerdo</span></div>
            <div style="text-align:center;">3<br><span style="font-size:12px">Neutro</span></div>
            <div style="text-align:center; width: 80px;">5<br><span style="font-size:12px">Muy de<br>Acuerdo</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    unanswered = []
    # Usamos números enteros para la lógica, pero labels simples
    options_numeric = [1, 2, 3, 4, 5]
    
    # -----------------------------
    # 3. Renderizado de Preguntas
    # -----------------------------
    for i, q in enumerate(questions):
        # Contenedor visual
        with st.container():
            st.markdown(f"""
            <div class="question-card">
                <div class="question-text">{i+1}. {q['text']}</div>
            """, unsafe_allow_html=True) 
            
            st.markdown("</div>", unsafe_allow_html=True) 

            # Recuperar valor
            saved_val = st.session_state.responses.get(q["code"])
            display_val = saved_val
            if saved_val is not None and q.get("reverse", False):
                display_val = invert_likert(saved_val)

            # RADIO BUTTON
            # Nota: options deben ser string o int. Usamos int para que coincida con la grilla.
            selection = st.radio(
                label=q['text'], 
                options=options_numeric,
                index=options_numeric.index(display_val) if display_val in options_numeric else None,
                horizontal=True,
                label_visibility="collapsed",
                key=f"{q['code']}_ui"
            )

            if selection is None:
                unanswered.append(q["code"])
            else:
                final_value = selection
                if q.get("reverse", False):
                    final_value = invert_likert(selection)
                st.session_state.responses[q["code"]] = final_value
            
            st.markdown("<div style='margin-bottom: 5px'></div>", unsafe_allow_html=True)

    st.divider()

    # -----------------------------
    # 4. Navegación
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