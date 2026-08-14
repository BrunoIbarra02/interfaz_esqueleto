"""
FBX topology signature.

Convierte la geometría de un FBX en una firma topológica
utilizando exactamente el mismo proceso que utilizaremos
para un GLB sin skin.
"""

from pathlib import Path

import skeletor

from topology.fbx_geometry import load_fbx_mesh
from topology.skeletonize import generate_skeleton
from topology.features import extract_forest_features


def fbx_topology_signature(fbx_path: str | Path):
    """
    Genera una firma topológica a partir de la geometría de un FBX.

    El FBX no se analiza por nombres de bones.
    La geometría se procesa mediante el mismo pipeline
    utilizado para modelos GLB sin skin.
    """

    fbx_path = Path(fbx_path)

    if not fbx_path.is_file():
        raise FileNotFoundError(
            f"FBX no encontrado: {fbx_path}"
        )

    mesh = load_fbx_mesh(
        fbx_path
    )

    mesh = skeletor.pre.fix_mesh(
        mesh,
        remove_disconnected=5,
        inplace=False,
    )

    skeleton = generate_skeleton(
        mesh,
        0.1,
    )

    return extract_forest_features(
        skeleton
    )
