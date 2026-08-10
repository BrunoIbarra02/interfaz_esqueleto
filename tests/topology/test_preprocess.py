"""
Test: Preprocess

Objetivo:
Validar la carga y validación de las mallas GLB
utilizadas por la Vía 2.
"""

from pathlib import Path

from topology.preprocess import (
    load_mesh,
    validate_mesh,
)


GLB_DIR = Path(__file__).parent / "glb"


def test_load_and_validate_meshes():

    glb_files = sorted(
        GLB_DIR.glob("*.glb")
    )

    assert glb_files, "No se encontraron archivos GLB."

    for glb_path in glb_files:

        mesh = load_mesh(
            str(glb_path)
        )

        assert validate_mesh(mesh) is True

        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0

        print()
        print("=" * 50)
        print(f"Modelo      : {glb_path.name}")
        print(f"Tipo        : {type(mesh).__name__}")
        print(f"Vértices    : {len(mesh.vertices)}")
        print(f"Caras       : {len(mesh.faces)}")
        print(f"Watertight  : {mesh.is_watertight}")