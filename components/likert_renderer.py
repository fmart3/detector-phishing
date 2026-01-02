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
    
    likert_labels = list(LIKERT_5.keys())
    value_to_label = {v: k for k, v in LIKERT_5.items()}

    # -----------------------------
    # Preguntas
    # -----------------------------
    
    for q in questions:
        st.markdown(
            f"<div style='font-size:18px; font-weight:500'>{q['text']}</div>",
            unsafe_allow_html=True
        )

        # 🔁 recuperar respuesta previa
        saved_value = st.session_state.responses.get(q["code"])
        saved_label = None

        if saved_value is not None:
            if q.get("reverse", False):
                saved_value = invert_likert(saved_value)
            saved_label = value_to_label[saved_value]

        response_label = st.radio(
            label="",
            options=likert_labels,
            index=likert_labels.index(saved_label) if saved_label else None,
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

    # Siguiente ➡️
    with col3:
        st.button(
            "Siguiente ➡️",
            disabled=bool(unanswered),
            on_click=lambda: st.session_state.update(page=next_page)
        )