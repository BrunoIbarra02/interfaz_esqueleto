"""
selector.py

Responsabilidad
-------------------
Seleccionar el esqueleto más adecuado para una imagen utilizando
OpenCLIP y los prompts definidos en el proyecto.

Entradas
-------------------
Ruta de una imagen.

Salidas
-------------------
Información del esqueleto seleccionado.

Dependencias
-------------------
classifier.py
prompts.py
mapping.py

No hace
-------------------
- No define prompts.
- No implementa OpenCLIP.
- No almacena esqueletos.
"""

from skeleton_selector.classifier import (
    load_model,
    encode_image,
    encode_text,
    compute_similarity,
)

from skeleton_selector.prompts import PROMPTS
from skeleton_selector.mapping import SKELETON_MAPPING

def select_skeleton(image_path):
    """
    Selecciona el esqueleto más adecuado para una imagen.


    Parametros
    -------------------

    image_path
        Ruta de la imagen.


    Retorna
    -------------------

    dict
        Información del esqueleto seleccionado.

    """

    model, preprocess, tokenizer = load_model()

    image_embedding = encode_image(
        model,
        preprocess,
        image_path,
    )

    labels = list(PROMPTS.keys())

    texts = []

    for category in labels:
        texts.extend(PROMPTS[category])
        
    text_embeddings = encode_text(
        model,
        tokenizer,
        texts,
    )
    
    similarities = compute_similarity(
        image_embedding,
        text_embeddings,
    )
    
    category_scores = {}

    index = 0

    for category in labels:

        num_prompts = len(PROMPTS[category])

        scores = similarities[index:index + num_prompts]

        category_scores[category] = scores.max().item()

        index += num_prompts
        
    best_category = max(
        category_scores,
        key=category_scores.get,
    )
    
    skeleton = SKELETON_MAPPING[best_category]
    
    return {
        "category": best_category,
        "skeleton": skeleton,
        "score": category_scores[best_category],
    }