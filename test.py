"""
test.py

Ejecuta una prueba del selector de esqueletos.

Si se proporciona una imagen como argumento, se utiliza esa imagen.
En caso contrario recorre todas las imagenes de test para realizar la prueba
"""

from argparse import ArgumentParser
from pathlib import Path

from skeleton_selector.selector import select_skeleton


IMAGES_DIR = Path("tests/images")


def parse_arguments():
    """
    Procesa los argumentos de la línea de comandos.

    Returns
    -------------------
    argparse.Namespace
        Argumentos proporcionados por el usuario.
    """

    parser = ArgumentParser(
        description="Prueba del selector de esqueletos."
    )

    parser.add_argument(
        "image",
        nargs="?",
        help="Ruta de una imagen. Si no se indica, se procesan todas las imágenes de tests/images.",
    )

    return parser.parse_args()


def process_image(image_path: Path):
    """
    Procesa una única imagen y muestra el resultado.

    Args
    -------------------
    image_path
        Ruta de la imagen.
    """

    result = select_skeleton(str(image_path))

    print("=" * 50)
    print(f"Imagen    : {image_path.name}")
    print(f"Categoría : {result['category']}")
    print(f"Esqueleto : {result['skeleton']}")


def main():
    """
    Ejecuta las pruebas del selector.
    """

    args = parse_arguments()

    if args.image:
        process_image(Path(args.image))
        return

    for image_path in sorted(IMAGES_DIR.iterdir()):

        if image_path.suffix.lower() not in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
        }:
            continue

        process_image(image_path)


if __name__ == "__main__":
    main()