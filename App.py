import streamlit as st

from pages.pages_likert import *
from pages.demographics import *

from utils.scoring import compute_scores
#from utils.mappings import mapping
from utils.databricks import predict


PAGES = {
    1: page_big5_extraversion,
    2: page_big5_amabilidad,
    3: page_big5_responsabilidad,
    4: page_big5_neuroticismo,
    5: page_big5_apertura,
    6: page_phish_actitud_riesgo,
    7: page_phish_awareness,
    8: page_phish_riesgo_percibido,
    9: page_phish_autoeficacia,
    10: page_phish_susceptibilidad,
    11: page_fatiga_emocional,
    12: page_fatiga_cinismo,
    13: page_fatiga_abandono
}

PAGES[st.session_state.page]()