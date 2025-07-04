# this is based on from gumper.atonas_gl

atonas_gl = [
    # determinantes
    'o', 'a', 'os', 'as', 'do', 'da', 'dó', 'dás', 'dos', 'das',
    'co', 'ca', 'cos', 'coa', 'coas', 'cas', 'cá', 'cós', 'cás',
    'no', 'na', 'nos', 'nas', 'nó', 'ná', 'ńas',
    'po', 'pol', 'pó',
    'polo', 'pola', 'polos', 'polas',
    'pólo', 'póla', 'pólos', 'pólas',
    'poIo', 'poIa', 'poIos', 'poIas', # ocr errors
    'póIo', 'póIa', 'póIos', 'póIas',
    'poio', 'poia', 'poios', 'poias',  # ocr errors
    'póio', 'póia', 'póios', 'póias',
    'pos',
    'lo', 'la', 'los', 'las',
    # pronombres átonos
    'me', 'te', 'che', 'se', 'lle', 'lles', 'lhes', 'nos', 'vos', 'vó', "vó lo",
    'mo', 'ma', 'mos', 'mas', 'cho', 'cha', 'chos', 'chas',
    'cho', 'cha', 'chos', 'chas',
    'llo', 'lle', 'lles',
    'á', 'ás', 'â', 'âs',
    # preposiciones (used ## in some cases to avoid matching)
    'a', 'ante', 'perante', 'até', 'deica', 'baixo',
    'canda', 'cas', 'con', 'conforme', 'consonte',
    'contra', 'de', 'dende', 'desde', 'desd', 'en', 'entre',
    'antre', 'entr', 'antr', "entr'a", "antr'a", "hastra",
    'excepto', '##agás', 'bardante', 'malia',
    'mediante', 'para', 'pra', 'por', '##segundo',
    'sen', 'sin', '##senón', 'sobre', 'tras', 'xunta', 'onda',
    # contracciones
    'ò', 'ó', 'ao', 'ô',
    # títulos
    "don", "dona", "fray", "sor", "san", "santa",
    # conjunciones
    "coma", "anque",
    "que", "como", "e", "logo", "mentres", 'mentras', "nin",
    "onde", "ou", "pero", "porque", "que", "se", "si", "cando", "y",
    # posesivos (if preceded by a determiner, they are stressed, but this is handled in preprocessing)
    "meu", "meus", "miña", "miñas",
    "teu", "teus",
    "seu", "seus",
    "noso", "nosa", "nosos", "nosas",
    "voso", "vosa", "vosos", "vosas"
]

# Metrically relevant cases where GL orthography uses a stress mark "diacritically"
#(i.e. to distinguish between two words that would otherwise be homographs).
#Only listing case that matters for metrical purposes, i.e. one of the words is stressed
#phonologically (not just orthographically accented), and the other one is not.

diacritic_stress = {"mais": "máis", "nos": "nós"}