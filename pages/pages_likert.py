# from components.likert_renderer import render_likert_page
# from components.questions_likert import (
#     BIG5_EXTRAVERSION,
#     BIG5_AMABILIDAD,
#     BIG5_RESPONSABILIDAD,
#     BIG5_NEUROTICISMO,
#     BIG5_APERTURA,

#     PHISH_ACTITUD_RIESGO,
#     PHISH_AWARENESS,
#     PHISH_RIESGO_PERCIBIDO,
#     PHISH_AUTOEFICACIA,
#     PHISH_SUSCEPTIBILIDAD,

#     FATIGA_EMOCIONAL,
#     FATIGA_CINISMO,
#     FATIGA_ABANDONO
# )

# # ----------------------------
# # BIG FIVE
# # ----------------------------

# def page_big5_extraversion():
#     render_likert_page(
#         title="🧠 Personalidad – Extraversión",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=BIG5_EXTRAVERSION,
#         next_page=2
#     )

# def page_big5_amabilidad():
#     render_likert_page(
#         title="🧠 Personalidad – Amabilidad",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=BIG5_AMABILIDAD,
#         prev_page=1,
#         next_page=3
#     )

# def page_big5_responsabilidad():
#     render_likert_page(
#         title="🧠 Personalidad – Responsabilidad",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=BIG5_RESPONSABILIDAD,
#         prev_page=2,
#         next_page=4
#     )

# def page_big5_neuroticismo():
#     render_likert_page(
#         title="🧠 Personalidad – Neuroticismo",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=BIG5_NEUROTICISMO,
#         prev_page=3,
#         next_page=5
#     )

# def page_big5_apertura():
#     render_likert_page(
#         title="🧠 Personalidad – Apertura a la Experiencia",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=BIG5_APERTURA,
#         prev_page=4,
#         next_page=6
#     )

# # ----------------------------
# # PHISHING
# # ----------------------------

# def page_phish_actitud_riesgo():
#     render_likert_page(
#         title="🎣 Phishing – Actitud al Riesgo",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=PHISH_ACTITUD_RIESGO,
#         prev_page=5,
#         next_page=7
#     )

# def page_phish_awareness():
#     render_likert_page(
#         title="🎣 Phishing – Conocimiento y Conciencia",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=PHISH_AWARENESS,
#         prev_page=6,
#         next_page=8
#     )

# def page_phish_riesgo_percibido():
#     render_likert_page(
#         title="🎣 Phishing – Riesgo Percibido",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=PHISH_RIESGO_PERCIBIDO,
#         prev_page=7,
#         next_page=9
#     )

# def page_phish_autoeficacia():
#     render_likert_page(
#         title="🎣 Phishing – Autoeficacia",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=PHISH_AUTOEFICACIA,
#         prev_page=8,
#         next_page=10
#     )

# def page_phish_susceptibilidad():
#     render_likert_page(
#         title="🎣 Phishing – Susceptibilidad",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=PHISH_SUSCEPTIBILIDAD,
#         prev_page=9,
#         next_page=11
#     )

# # ----------------------------
# # FATIGA
# # ----------------------------

# def page_fatiga_emocional():
#     render_likert_page(
#         title="😴 Fatiga de Seguridad – Agotamiento Emocional",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=FATIGA_EMOCIONAL,
#         prev_page=10,
#         next_page=12
#     )

# def page_fatiga_cinismo():
#     render_likert_page(
#         title="😴 Fatiga de Seguridad – Cinismo",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=FATIGA_CINISMO,
#         prev_page=11,
#         next_page=13
#     )

# def page_fatiga_abandono():
#     render_likert_page(
#         title="😴 Fatiga de Seguridad – Intención de Abandono",
#         description="Indique su grado de acuerdo con las siguientes afirmaciones:",
#         questions=FATIGA_ABANDONO,
#         prev_page=12,
#         next_page=14
#     )
from components.likert_renderer import render_likert_page
from components.questions_likert import (
    BIG5_RESPONSABILIDAD,
    BIG5_APERTURA,
    PHISH_RIESGO_PERCIBIDO,
    FATIGA_EMOCIONAL,
    FATIGA_CINISMO,
    FATIGA_ABANDONO
)

# ----------------------------
# BIG FIVE
# ----------------------------

def page_big5_responsabilidad():
    render_likert_page(
        title="🧠 Personalidad – Responsabilidad",
        description="Indique su grado de acuerdo con las siguientes afirmaciones:",
        questions=BIG5_RESPONSABILIDAD,
        next_page=2
    )
    
def page_big5_apertura():
    render_likert_page(
        title="🧠 Personalidad – Apertura a la Experiencia",
        description="Indique su grado de acuerdo con las siguientes afirmaciones:",
        questions=BIG5_APERTURA,
        prev_page=1,
        next_page=3
    )
    
# ----------------------------
# PHISHING
# ----------------------------

def page_phish_riesgo_percibido():
    render_likert_page(
        title="🎣 Phishing – Riesgo Percibido",
        description="Indique su grado de acuerdo con las siguientes afirmaciones:",
        questions=PHISH_RIESGO_PERCIBIDO,
        prev_page=2,
        next_page=4
    )

# ----------------------------
# FATIGA
# ----------------------------

def page_fatiga_emocional():
    render_likert_page(
        title="😴 Fatiga de Seguridad – Agotamiento Emocional",
        description="Indique su grado de acuerdo con las siguientes afirmaciones:",
        questions=FATIGA_EMOCIONAL,
        prev_page=3,
        next_page=5
    )

def page_fatiga_cinismo():
    render_likert_page(
        title="😴 Fatiga de Seguridad – Cinismo",
        description="Indique su grado de acuerdo con las siguientes afirmaciones:",
        questions=FATIGA_CINISMO,
        prev_page=4,
        next_page=6
    )

def page_fatiga_abandono():
    render_likert_page(
        title="😴 Fatiga de Seguridad – Intención de Abandono",
        description="Indique su grado de acuerdo con las siguientes afirmaciones:",
        questions=FATIGA_ABANDONO,
        prev_page=5,
        next_page=7
    )