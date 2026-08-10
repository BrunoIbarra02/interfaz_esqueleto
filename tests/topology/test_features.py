"""
Test: Features

Objetivo:
Validar la extracción de características de un Bone Tree.
"""

from pathlib import Path

from topology.preprocess import load_mesh
from topology.skeletonize import generate_skeleton
from topology.bone import build_bone_tree
from topology.features import extract_features


GLB_DIR = Path(__file__).parent / "glb"


def test_features():

    glb_path = GLB_DIR / "oso_polar.glb"

    mesh = load_mesh(
        str(glb_path)
    )

    skeleton = generate_skeleton(
        mesh,
        sampling_dist=0.05,
    )

    root = build_bone_tree(
        skeleton
    )

    features = extract_features(
        root
    )

    assert features is not None

    assert features.node_count > 0
    assert features.leaf_count > 0

    assert features.bone_length_mean > 0

    print()
    print("=" * 60)
    print("Features")
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
        f"Bone mean    : {features.bone_length_mean:.6f}"
    )