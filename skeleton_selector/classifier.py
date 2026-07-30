"""
classifier.py

Clasifica una imagen de un animal utilizando la API de OpenAI.

El módulo envía una imagen al modelo GPT-5 Nano y obtiene como respuesta
una única categoría perteneciente al conjunto de esqueletos soportados
por el proyecto.

La función principal es ``classify_image()``, que devuelve el nombre de
la categoría detectada.

"""
import base64
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Carga las variables de entorno (.env)
load_dotenv()

# Cliente OpenAI
client = OpenAI()

#: Categorías válidas soportadas por el proyecto.
CATEGORIES = [
    "Bear",
    "BlackWidow",
    "Crocodile",
    "Deer",
    "DragonFly",
    "Eagle",
    "GreatHornedOwl",
    "HellenicHound",
    "Horse",
    "IndianElephant",
    "Squid",
    "WhiteShark",
]

# Prompt enviado al modelo.
PROMPT = f"""
You are an image classifier.

Classify the animal shown in the image.

You MUST answer using ONLY one of these categories:

{", ".join(CATEGORIES)}

Return ONLY the category name.
Do not add explanations.
Do not use punctuation.
"""


def classify_image(image_path: str) -> str:
    """
    Clasifica una imagen mediante OpenAI.

    Args:
        image_path (str):
            Ruta de la imagen que se desea clasificar.

    Returns:
        str:
            Categoría detectada. Siempre será una de las definidas en CATEGORIES

    Raises:
        FileNotFoundError:
            Si la imagen no existe.

        ValueError:
            Si OpenAI devuelve una categoría no válida.
            
        OpenAIError:
            Si ocurre un error durante la llamada a la API
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with image_path.open("rb") as image_file:
        image_base64 = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": PROMPT,
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:image/png;base64,{image_base64}"
                        ),
                    },
                ],
            }
        ],
    )

    category = response.output_text.strip()

    if category not in CATEGORIES:
        raise ValueError(
            f"Invalid category returned by OpenAI: {category}"
        )

    return category