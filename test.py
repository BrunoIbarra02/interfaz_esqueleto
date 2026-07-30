from skeleton_selector.classifier import (
    load_model,
    encode_image,
    encode_text,
    compute_similarity,
)


def main():
    print("Cargando OpenCLIP...")

    model, preprocess, tokenizer = load_model()

    print("Modelo cargado correctamente.")

    image_path = "tests/images/oso_pardo.png"

    labels = [
        "bear",
        "deer",
        "horse",
        "wolf",
    ]

    print("Generando embedding de la imagen...")

    image_embedding = encode_image(
        model,
        preprocess,
        image_path,
    )

    print("Generando embeddings de texto...")

    text_embeddings = encode_text(
        model,
        tokenizer,
        labels,
    )
    print("Calculando similitud...")

    similarities = compute_similarity(
        image_embedding,
        text_embeddings,
    )

    results = sorted(
        zip(labels, similarities.tolist()),
        key=lambda x: x[1],
        reverse=True,
    )

    print("\nRanking:")

    for label, score in results:
        print(f"{label:10} {score:.4f}")

if __name__ == "__main__":
    main()