from utils.persistence import insert_survey_response
from utils.scoring import compute_scores

responses = {
    "EX01": 3, "EX02": 4, "EX03": 2, "EX04": 3, "EX05": 4,
    "EX06": 3, "EX07": 4, "EX08": 2, "EX09": 3, "EX10": 4,

    "AM01": 3, "AM02": 3, "AM03": 4, "AM04": 4, "AM05": 3,
    "AM06": 4, "AM07": 3, "AM08": 4, "AM09": 3, "AM10": 4,

    "CO01": 3, "CO02": 4, "CO03": 3, "CO04": 4, "CO05": 3,
    "CO06": 4, "CO07": 3, "CO08": 4, "CO09": 3, "CO10": 4,

    "NE01": 2, "NE02": 3, "NE03": 2, "NE04": 3, "NE05": 2,
    "NE06": 3, "NE07": 2, "NE08": 3, "NE09": 2, "NE10": 3,

    "AE01": 4, "AE02": 4, "AE03": 3, "AE04": 4, "AE05": 3,
    "AE06": 4, "AE07": 4, "AE08": 3, "AE09": 4, "AE10": 3,

    "ER01": 2, "ER02": 2, "ER03": 3, "ER04": 2, "ER05": 3,
    "ER06": 2, "ER07": 3, "ER08": 2, "ER09": 3, "ER10": 2,

    "AW01": 4, "AW02": 4, "AW03": 3,
    "PR01": 3, "PR02": 3, "PR03": 3,
    "CP01": 4, "CP02": 3, "CP03": 4,
    "SU01": 2, "SU02": 3, "SU03": 2, "SU04": 3,

    "FE01": 2, "FE02": 3, "FE03": 2,
    "FC01": 3, "FC02": 3, "FC03": 2,
    "DS01": 2, "DS02": 3,

    "Demo_Pais": 1,
    "Demo_Tipo_Organizacion": 2,
    "Demo_Industria": 3,
    "Demo_Tamano_Org": 2,
    "Demo_Rol_Trabajo": 3,
    "Demo_Generacion_Edad": 2,
    "Demo_Genero": 1,
    "Demo_Nivel_Educacion": 4,
    "Demo_Horas": 2
}

scores = compute_scores(responses)

insert_survey_response(
    responses=responses,
    scores=scores,
    model_output={
        "probability": 0.63,
        "risk_level": "MEDIO"
    }
)
print("Inserción de prueba completada.")