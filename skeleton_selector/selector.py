"""
selector.py

Responsabilidad
-------------------
Seleccionar el esqueleto más adecuado para una imagen utilizando
la clasificación obtenida mediante OpenAI.

Entradas
-------------------
Ruta de una imagen.

Salidas
-------------------
Información del esqueleto seleccionado.

Dependencias
-------------------
classifier.py
mapping.py

No hace
-------------------
- No clasifica imágenes.
- No implementa llamadas a OpenAI.
- No almacena esqueletos.
"""

from skeleton_selector.classifier import classify_image
from skeleton_selector.mapping import SKELETON_MAPPING


def select_skeleton(image_path: str) -> dict:
    """
    Selecciona el esqueleto más adecuado para una imagen.

    Parámetros
    -------------------

    image_path
        Ruta de la imagen.

    Retorna
    -------------------

    dict
        Información del esqueleto seleccionado.
    """

    category = classify_image(image_path)

    skeleton = SKELETON_MAPPING[category]

    return {
        "category": category,
        "skeleton": skeleton,
    }