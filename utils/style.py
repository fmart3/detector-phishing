import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* Estilo para simular una 'Card' de Bootstrap */
        .bootstrap-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
        }
        
        /* Ajustar títulos para que se vean más limpios */
        h1, h2, h3 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-weight: 600;
            color: #343a40;
        }
        
        /* Mejorar la apariencia de las métricas */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            color: #0d6efd;
        }
        </style>
    """, unsafe_allow_html=True)