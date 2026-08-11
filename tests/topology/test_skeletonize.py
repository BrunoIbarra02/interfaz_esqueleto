"""
Test: Skeletonize

Objetivo:
Validar la generación de un curve skeleton a partir
de una malla preparada.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)

from topology.preprocess import (
    load_mesh,
    validate_mesh,
)

from topology.skeletonize import generate_skeleton


GLB_DIR = Path(__file__).parent / "glb"


def test_skeletonize():

    glb_path = GLB_DIR / "oso_polar.glb"

    mesh = load_mesh(
        str(glb_path)
    )

    validate_mesh(mesh)

    skeleton = generate_skeleton(
        mesh,
        sampling_dist=0.05,
    )

    assert skeleton is not None

    assert len(skeleton.vertices) > 0
    assert len(skeleton.edges) > 0

    assert len(skeleton.roots) > 0
    assert len(skeleton.leafs) > 0

    print()
    print("=" * 60)
    print("Skeletonize")
    print("=" * 60)

    print(
        f"Modelo      : {glb_path.name}"
    )

    print(
        f"Skeleton    : {type(skeleton).__name__}"
    )

    print(
        f"Vértices    : {len(skeleton.vertices)}"
    )

    print(
        f"Aristas     : {len(skeleton.edges)}"
    )

    print(
        f"Raíces      : {len(skeleton.roots)}"
    )

    print(
        f"Hojas       : {len(skeleton.leafs)}"
    )