"""
Test: Bone Tree

Objetivo:
Validar la conversión del Skeleton generado por Skeletor
a nuestra jerarquía interna de Bone.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)

from topology.preprocess import load_mesh
from topology.skeletonize import generate_skeleton
from topology.bone import build_bone_tree


GLB_DIR = Path(__file__).parent / "glb"


def test_build_bone_tree():

    glb_path = GLB_DIR / "oso_polar.glb"

    mesh = load_mesh(str(glb_path))

    skeleton = generate_skeleton(
        mesh,
        sampling_dist=0.05,
    )

    root = build_bone_tree(
        skeleton
    )

    assert root is not None
    assert root.parent is None
    assert len(root.children) > 0

    print()
    print("=" * 60)
    print("Bone Tree")
    print("=" * 60)

    print(f"Root     : {root}")
    print(f"Children : {len(root.children)}")