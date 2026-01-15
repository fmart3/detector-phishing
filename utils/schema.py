REQUIRED_RESPONSE_FIELDS = [
    # Big Five
    *[f"EX{str(i).zfill(2)}" for i in range(1, 11)],
    *[f"AM{str(i).zfill(2)}" for i in range(1, 11)],
    *[f"CO{str(i).zfill(2)}" for i in range(1, 11)],
    *[f"NE{str(i).zfill(2)}" for i in range(1, 11)],
    *[f"AE{str(i).zfill(2)}" for i in range(1, 11)],

    # Phishing
    *[f"ER{str(i).zfill(2)}" for i in range(1, 11)],
    "AW01", "AW02", "AW03",
    "PR01", "PR02", "PR03",
    "CP01", "CP02", "CP03",
    "SU01", "SU02", "SU03", "SU04",

    # Fatiga
    "FE01", "FE02", "FE03",
    "FC01", "FC02", "FC03",
    "DS01", "DS02",

    # Demográficos
    "Demo_Pais",
    "Demo_Tipo_Organizacion",
    "Demo_Industria",
    "Demo_Tamano_Org",
    "Demo_Rol_Trabajo",
    "Demo_Generacion_Edad",
    "Demo_Genero",
    "Demo_Nivel_Educacion",
    "Demo_Horas"
]
