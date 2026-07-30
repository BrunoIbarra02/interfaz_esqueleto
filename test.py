from pathlib import Path

from skeleton_selector.selector import select_skeleton


def main():

    images_dir = Path("tests/images")

    for image_path in sorted(images_dir.iterdir()):

        if image_path.suffix.lower() not in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
        }:
            continue

        result = select_skeleton(str(image_path))

        print("=" * 50)
        print(f"Imagen    : {image_path.name}")
        print(f"Categoría : {result['category']}")
        print(f"Esqueleto : {result['skeleton']}")
        print(f"Score     : {result['score']:.4f}")


if __name__ == "__main__":
    main()