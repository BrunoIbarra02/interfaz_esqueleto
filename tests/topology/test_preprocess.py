from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))

from topology.preprocess import load_mesh,validate_mesh


def main():

    glb_dir = Path(__file__).parent / "glb"

    for glb_path in sorted(glb_dir.glob("*.glb")):

        mesh = load_mesh(str(glb_path))

        print("=" * 50)
        print(f"Validación  : {validate_mesh(mesh)}")
        print(f"Modelo      : {glb_path.name}")
        print(f"Tipo        : {type(mesh).__name__}")
        print(f"Vértices    : {len(mesh.vertices)}")
        print(f"Caras       : {len(mesh.faces)}")
        print(f"Watertight  : {mesh.is_watertight}")

        

if __name__ == "__main__":
    main()