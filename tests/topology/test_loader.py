"""
Test: Loader

Objetivo:
Validar la carga de modelos GLB utilizados por el pipeline.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)

from topology.loader import load_glb, has_skin


GLB_DIR = Path(__file__).parent / "glb"


def test_load_glb():

    glb_path = GLB_DIR / "oso_polar.glb"

    gltf = load_glb(str(glb_path))

    assert gltf is not None


def test_has_skin():

    glb_path = GLB_DIR / "oso_polar.glb"

    gltf = load_glb(str(glb_path))

    result = has_skin(gltf)

    assert isinstance(result, bool)

    print(
        f"Modelo: {glb_path.name}"
    )

    print(
        f"Contiene skin: {result}"
    )