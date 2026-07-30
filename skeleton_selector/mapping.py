"""
mapping.py

Responsabilidad
-------------------
Asociar cada categoría con el fichero de esqueleto
que debe utilizar el sistema.

Entradas
-------------------
Ninguna.

Salidas
-------------------
Diccionario con la correspondencia entre categorías
y esqueletos.

Dependencias
-------------------
Ninguna.

No hace
-------------------
- No carga modelos.
- No calcula similitudes.
- No selecciona categorías.
"""

SKELETON_MAPPING = {
    "Bear": "Bear.FBX",
    "BlackWidow": "BlackWidow.FBX",
    "Crocodile": "Crocodile.FBX",
    "Deer": "Deer.FBX",
    "DragonFly": "DragonFly.FBX",
    "Eagle": "Eagle.FBX",
    "GreatHornedOwl": "GreatHornedOwl.FBX",
    "HellenicHound": "HellenicHound.FBX",
    "Horse": "Horse.FBX",
    "IndianElephant": "IndianElephant.FBX",
    "Squid": "Squid.FBX",
    "WhiteShark": "WhiteShark.FBX",
}