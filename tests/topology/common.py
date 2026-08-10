"""
common.py

Funciones comunes utilizadas por los tests de topología.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import skeletor

from topology.preprocess import load_mesh


# ------------------------------------------------------------------
# Configuración
# ------------------------------------------------------------------

TEST_GLB = PROJECT_ROOT / "tests" / "topology" / "glb" / "Eagle.glb"


# ------------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------------

def print_title(title):
    """
    Imprime un título con un formato común.
    """

    print("=" * 60)
    print(title)
    print("=" * 60)


# ------------------------------------------------------------------
# Datos de prueba
# ------------------------------------------------------------------

def get_mesh(glb_path=TEST_GLB):
    """
    Carga la malla utilizada en las pruebas.
    """
    mesh = load_mesh(str(glb_path))
    
    return skeletor.pre.fix_mesh(
        mesh,
        remove_disconnected=5,
        inplace=False,
    )


def get_skeleton(glb_path=TEST_GLB):
    """
    Genera el Skeleton utilizado en las pruebas.
    """

    return skeletor.skeletonize.by_teasar(
        get_mesh(glb_path),
        inv_dist=0.1,
    )


def get_graph(glb_path=TEST_GLB):
    """
    Genera el grafo del Skeleton utilizado en las pruebas.
    """

    return get_skeleton(glb_path).get_graph()

def print_mesh_stats(name, mesh):
    """
    Muestra información básica de una malla.
    """

    print("=" * 60)
    print(name)
    print("=" * 60)

    print(f"Tipo        : {type(mesh).__name__}")
    print(f"Vértices    : {len(mesh.vertices)}")
    print(f"Caras       : {len(mesh.faces)}")
    print(f"Watertight  : {mesh.is_watertight}")

    print()
    print(mesh)