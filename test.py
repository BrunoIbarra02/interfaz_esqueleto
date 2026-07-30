from skeleton_selector.selector import select_skeleton


def main():

    result = select_skeleton(
        "tests/images/oso_pardo.png"
    )

    print(result)


if __name__ == "__main__":
    main()
