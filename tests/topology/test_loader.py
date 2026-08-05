"""
=========================================================
Test: Loader

Objetivo:
    Validar la carga de modelos GLB utilizados por el
    pipeline.

Estado:
    En desarrollo
=========================================================
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))


from topology.loader import load_glb, has_skin

def main():
    
    glb_path = Path(__file__).parent / "glb" / "oso_polar.glb"
    gltf = load_glb(str(glb_path))
    
    print(f"Modelo cargado desde: {glb_path}")
    print(f"Contiene skin?: {has_skin(gltf)}")
    
if __name__ == "__main__":
    main()
    