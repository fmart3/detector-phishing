LIKERT_5 = {
    "Muy en desacuerdo": 1,
    "Ligeramente en desacuerdo": 2,
    "Ni de acuerdo ni en desacuerdo": 3,
    "Ligeramente de acuerdo": 4,
    "Muy de acuerdo": 5
}

def invert_likert(value: int) -> int:
    return 6 - value

INIT_PAGE = 0