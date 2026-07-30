from skeleton_selector.classifier import load_model


def main():
    print("Cargando OpenCLIP...")

    model, preprocess, tokenizer = load_model()

    print("Modelo cargado correctamente.")
    print(type(model))
    print(type(preprocess))
    print(type(tokenizer))


if __name__ == "__main__":
    main()