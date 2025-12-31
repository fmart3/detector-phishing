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
    Renderiza una página de preguntas tipo Likert (1–5).

    questions: lista de dicts:
    {
        "code": "AE01",
        "text": "Yo creo en la importancia del arte.",
        "reverse": False
    }
    """

    # -----------------------------
    # Inicialización de estado
    # -----------------------------
    if "responses" not in st.session_state:
        st.session_state.responses = {}

    if "page" not in st.session_state:
        st.session_state.page = 1

    # -----------------------------
    # UI - Header
    # -----------------------------
    st.markdown(f"## {title}")
    st.write(description)
    st.divider()

    unanswered = []

    # -----------------------------
    # Preguntas
    # -----------------------------
    
    for q in questions:
        st.markdown(
            f"<div style='font-size:18px; font-weight:500'>{q['text']}</div>",
            unsafe_allow_html=True
        )

        response_label = st.radio(
            label="",
            options=list(LIKERT_5.keys()),
            index=None,              # obliga selección
            horizontal=True,
            key=f"{q['code']}_ui"
        )

        if response_label is None:
            unanswered.append(q["code"])
        else:
            value = LIKERT_5[response_label]
            if q.get("reverse", False):
                value = invert_likert(value)

            st.session_state.responses[q["code"]] = value

        st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------
    # Navegación
    # -----------------------------
    col1, col2, col3 = st.columns([1, 3, 1])

    # ⬅️ Atrás
    if prev_page is not None:
        with col1:
            st.button(
                "⬅️ Atrás",
                on_click=lambda: st.session_state.update(page=prev_page)
            )

    # ➡️ Siguiente (con validación)
    with col3:
        if unanswered:
            st.button("Siguiente ➡️", disabled=True)
        else:
            st.button(
                "Siguiente ➡️",
                on_click=lambda: st.session_state.update(page=next_page)
            )

    # -----------------------------
    # Mensaje de validación
    # -----------------------------
    if unanswered:
        st.warning("⚠️ Debe responder todas las preguntas para continuar.")