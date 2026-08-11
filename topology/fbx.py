"""
fbx.py

Conversión de la jerarquía de un FBX a nuestro
Bone Tree interno utilizando assimp-py.

## No hace

- No modifica el FBX.
- No utiliza Blender.
- No realiza skinning.
- No realiza matching.
- No exporta resultados.
"""

from pathlib import Path

import assimp_py
import numpy as np

from topology.bone import Bone


def load_fbx_skeleton(fbx_path):
    """
    Carga un FBX y convierte su jerarquía de joints
    en nuestro Bone Tree.

    Parameters
    ----------
    fbx_path : str
        Ruta del archivo FBX.

    Returns
    -------
    Bone
        Raíz del Bone Tree.
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

    # --------------------------------------------------
    # Buscar el primer joint
    # --------------------------------------------------

    joint_root = _find_joint_root(
        scene.root_node
    )

    if joint_root is None:
        raise ValueError(
            "No se encontró ningún joint en el FBX."
        )

    # --------------------------------------------------
    # Construir Bone Tree
    # --------------------------------------------------

    return _build_bone_tree(
        joint_root
    )


def _find_joint_root(node):
    """
    Busca el primer nodo que pertenece a la jerarquía
    de joints.
    """

    if node.name.endswith("SHJnt"):
        return node

    for child in node.children:

        result = _find_joint_root(child)

        if result is not None:
            return result

    return None


def _build_bone_tree(
    node,
    parent_transform=None,
    parent_bone=None,
):
    """
    Convierte recursivamente un nodo Assimp
    en un Bone.
    """

    local_transform = np.array(
        node.transformation,
        dtype=float,
    )

    if parent_transform is None:

        global_transform = local_transform

    else:

        global_transform = (
            parent_transform
            @ local_transform
        )

    position = global_transform[:3, 3]

    bone = Bone(
        node.node_id if hasattr(node, "node_id") else node.name,
        position.copy(),
    )

    # Guardamos el nombre real del joint.
    bone.name = node.name

    if parent_bone is not None:

        bone.parent = parent_bone
        parent_bone.children.append(bone)

    for child in node.children:

        if not child.name.endswith("SHJnt"):
            continue

        _build_bone_tree(
            child,
            global_transform,
            bone,
        )

    return bone