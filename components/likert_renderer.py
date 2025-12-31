import streamlit as st
from utils.scales import LIKERT_5, invert_likert


def render_likert_page(
    title: str,
    description: str,
    questions: list,
    next_page: int
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
        st.session_state.page = 0

    # -----------------------------
    # UI
    # -----------------------------
    st.header(title)
    st.write(description)
    st.divider()

    for q in questions:
        response_label = st.radio(
            label=q["text"],
            options=list(LIKERT_5.keys()),
            index=None,              # fuerza selección explícita
            horizontal=True,         # estilo Qualtrics
            key=f"{q['code']}_ui"
        )

        if response_label is not None:
            value = LIKERT_5[response_label]

            if q.get("reverse", False):
                value = invert_likert(value)

            st.session_state.responses[q["code"]] = value

        st.markdown("---")

    # -----------------------------
    # Navegación
    # -----------------------------
    col1, col2 = st.columns([4, 1])

    with col2:
        st.button(
            "Siguiente ➡️",
            on_click=lambda: st.session_state.update(page=next_page)
        )
