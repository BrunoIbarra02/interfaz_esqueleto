from skeleton_selector.classifier import load_model, encode_image


def main():
    print("Cargando OpenCLIP...")

    model, preprocess, tokenizer = load_model()

    print("Modelo cargado correctamente.")

    print("Generando embedding de la imagen...")
    
    TEST_IMAGE = "tests/images/oso_pardo.png"

    embedding = encode_image(
        model,
        preprocess,
        TEST_IMAGE,
    )

    print("Embedding generado correctamente.")
    print(f"Shape: {embedding.shape}")
    print(f"Device: {embedding.device}")
    print(f"Dtype: {embedding.dtype}")
if __name__ == "__main__":
    main()