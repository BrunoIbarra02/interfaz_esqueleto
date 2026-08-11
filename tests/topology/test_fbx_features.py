"""
Test: FBX Features

Objetivo:
Validar la extracción de características de un
Bone Tree generado desde un FBX.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from topology.fbx import load_fbx_skeleton
from topology.features import extract_features


FBX_DIR = PROJECT_ROOT / "skeletons"


def test_fbx_features():

    fbx_path = FBX_DIR / "Bear.FBX"

    root = load_fbx_skeleton(
        str(fbx_path)
    )

    features = extract_features(
        root
    )

    assert features is not None

    assert features.node_count == 41

    assert features.leaf_count > 0

    assert features.branch_count > 0

    assert features.bone_length_mean > 0

    assert features.bone_length_min > 0

    assert features.bone_length_max > 0

    print()
    print("=" * 60)
    print("FBX Features")
    print("=" * 60)

    print(
        f"Nodes        : {features.node_count}"
    )

    print(
        f"Leaves       : {features.leaf_count}"
    )

    print(
        f"Branches     : {features.branch_count}"
    )

    print(
        f"Max children : {features.max_children}"
    )

    print(
        f"Max depth    : {features.max_depth}"
    )

    print(
        f"Bone min     : "
        f"{features.bone_length_min:.6f}"
    )

    print(
        f"Bone max     : "
        f"{features.bone_length_max:.6f}"
    )

    print(
        f"Bone mean    : "
        f"{features.bone_length_mean:.6f}"
    )

    print(
        f"Bone std     : "
        f"{features.bone_length_std:.6f}"
    )


def main():

    test_fbx_features()


if __name__ == "__main__":
    main()