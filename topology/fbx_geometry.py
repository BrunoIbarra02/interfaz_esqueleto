"""
fbx_geometry.py

Extrae la geometría de un FBX mediante Assimp
y genera una firma geométrica compatible con
el algoritmo de clasificación.
"""

from pathlib import Path

import assimp_py
import numpy as np

from topology.features import shape_signature


# ============================================================
# FBX GEOMETRY SIGNATURE
# ============================================================

def fbx_geometry_signature(fbx_path):
    """
    Extrae los vértices de las mallas de un FBX
    mediante Assimp y genera su GeometrySignature.

    Parameters
    ----------
    fbx_path : str | Path
        Ruta al archivo FBX.

    Returns
    -------
    GeometrySignature
        Firma geométrica del FBX.
    """

    fbx_path = Path(fbx_path)

    if not fbx_path.exists():
        raise FileNotFoundError(
            f"FBX no encontrado: {fbx_path}"
        )

    scene = assimp_py.import_file(
        str(fbx_path),
        0,
    )

    if scene is None:
        raise ValueError(
            f"No se pudo cargar el FBX: {fbx_path}"
        )

    arrays = []

    # --------------------------------------------------------
    # Extraer vértices de las mallas
    # --------------------------------------------------------

    for mesh in scene.meshes:

        vertices = np.asarray(
            mesh.vertices,
            dtype=np.float32,
        )

        if vertices.size == 0:
            continue

        # Assimp devuelve los vértices como un
        # memoryview plano: [x, y, z, x, y, z, ...]
        if vertices.size % 3 != 0:
            raise ValueError(
                f"Geometría inválida en "
                f"{fbx_path.name}: "
                f"{vertices.size} valores de vértices."
            )

        vertices = vertices.reshape(
            -1,
            3,
        )

        arrays.append(
            vertices
        )

    # --------------------------------------------------------
    # Comprobar que hemos encontrado geometría
    # --------------------------------------------------------

    if not arrays:
        raise ValueError(
            f"No se encontraron vértices "
            f"en {fbx_path.name}"
        )

    # --------------------------------------------------------
    # Utilizar la malla con mayor número de vértices
    # --------------------------------------------------------

    vertices = max(
        arrays,
        key=lambda values: values.size,
    )

    # --------------------------------------------------------
    # Generar firma geométrica
    # --------------------------------------------------------

    return shape_signature(
        vertices
    )
    
def load_fbx_mesh(path: Path):
    """
    Carga la geometría principal de un FBX como Trimesh.

    Se utiliza para aplicar el mismo pipeline geométrico
    a los FBX de referencia y a los GLB sin skin.
    """

    import trimesh

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"FBX no encontrado: {path}"
        )

    scene = assimp_py.import_file(
        str(path),
        0,
    )

    if scene is None or not scene.meshes:
        raise ValueError(
            f"No se encontró geometría en {path}"
        )

    # Usamos la malla con mayor número de vértices.
    source_mesh = max(
        scene.meshes,
        key=lambda mesh: mesh.num_vertices,
    )

    vertices = np.asarray(
        source_mesh.vertices,
        dtype=np.float32,
    ).reshape(-1, 3)

    indices = np.asarray(
        source_mesh.indices,
        dtype=np.int64,
    )

    if len(indices) == 0:
        raise ValueError(
            f"No se encontraron índices en {path}"
        )

    faces = indices.reshape(-1, 3)

    return trimesh.Trimesh(
        vertices=vertices,
        faces=faces,
        process=False,
    )