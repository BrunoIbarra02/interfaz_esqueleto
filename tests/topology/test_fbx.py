"""
Test: FBX

Objetivo:
Validar la conversión de la jerarquía de un FBX
a nuestro Bone Tree.
"""

from pathlib import Path
import sys
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT_ROOT),)
FBX_DIR = PROJECT_ROOT / "skeletons"



from topology.fbx import load_fbx_skeleton




def walk_bones(bone):
    """
    Cuenta recursivamente los Bones del árbol.
    """

    count = 1

    for child in bone.children:
        count += walk_bones(child)

    return count


def test_fbx():

    fbx_path = FBX_DIR / "Bear.FBX"

    root = load_fbx_skeleton(
        str(fbx_path)
    )

    assert root is not None
    assert root.parent is None

    count = walk_bones(root)

    assert count > 0

    print()
    print("=" * 60)
    print("FBX Skeleton")
    print("=" * 60)

    print(
        f"Archivo : {fbx_path.name}"
    )

    print(
        f"Root    : {root}"
    )

    print(
        f"Bones   : {count}"
    )

    print(
        f"Children: {len(root.children)}"
    )
    
def test_fbx_structure():

    fbx_path = FBX_DIR / "Bear.FBX"

    root = load_fbx_skeleton(
        str(fbx_path)
    )

    assert root.name == "Bear_MAINSHJnt"

    assert root.parent is None

    assert len(root.children) == 1

    child = root.children[0]

    assert child.name == "Bear_ROOTSHJnt"

    assert child.parent is root

    assert len(child.children) > 0

    print()
    print("=" * 60)
    print("FBX Structure")
    print("=" * 60)

    print(f"Root  : {root.name}")
    print(f"Child : {child.name}")
    print(f"Grandchildren : {len(child.children)}")
    
def test_fbx_positions():

    fbx_path = FBX_DIR / "Bear.FBX"

    root = load_fbx_skeleton(
        str(fbx_path)
    )

    print()
    print("=" * 60)
    print("FBX Bone Positions")
    print("=" * 60)

    def walk(bone):

        print(
            f"{bone.name:40} "
            f"pos=("
            f"{bone.position[0]:10.4f}, "
            f"{bone.position[1]:10.4f}, "
            f"{bone.position[2]:10.4f}"
            f")"
        )

        if bone.parent is not None:

            length = np.linalg.norm(
                np.asarray(bone.position)
                - np.asarray(bone.parent.position)
            )

            print(
                f"{'':40} "
                f"length={length:.6f}"
            )

        for child in bone.children:
            walk(child)

    walk(root)


def main():

    test_fbx()
    test_fbx_structure()
    test_fbx_positions()


if __name__ == "__main__":
    main()