"""
prompts.py

Responsabilidad
-------------------
Definir los prompts de texto que representan cada categoría
para que OpenCLIP pueda compararlos con una imagen.

Entradas
-------------------
Ninguna.

Salidas
-------------------
Colecciones de prompts organizadas por categoría.

Dependencias
-------------------
Ninguna.

No hace
-------------------
- No carga modelos.
- No genera embeddings.
- No calcula similitudes.
- No selecciona esqueletos.
"""

BEAR = [
    "bear",
    "a bear",
]

BLACK_WIDOW = [
    "black widow spider",
    "a black widow spider",
]

CROCODILE = [
    "crocodile",
    "a crocodile",
]

DEER = [
    "deer",
    "a deer",
]

DRAGONFLY = [
    "dragonfly",
    "a dragonfly",
]

EAGLE = [
    "eagle",
    "an eagle",
]

GREAT_HORNED_OWL = [
    "great horned owl",
    "an owl",
]

HELLENIC_HOUND = [
    "dog",
    "a dog",
    "hellenic hound",
]

HORSE = [
    "horse",
    "a horse",
]

INDIAN_ELEPHANT = [
    "indian elephant",
    "an elephant",
]

SQUID = [
    "squid",
    "a squid",
]

WHITE_SHARK = [
    "great white shark",
    "white shark",
    "a shark",
]

PROMPTS = {
    "Bear": BEAR,
    "BlackWidow": BLACK_WIDOW,
    "Crocodile": CROCODILE,
    "Deer": DEER,
    "DragonFly": DRAGONFLY,
    "Eagle": EAGLE,
    "GreatHornedOwl": GREAT_HORNED_OWL,
    "HellenicHound": HELLENIC_HOUND,
    "Horse": HORSE,
    "IndianElephant": INDIAN_ELEPHANT,
    "Squid": SQUID,
    "WhiteShark": WHITE_SHARK,
}