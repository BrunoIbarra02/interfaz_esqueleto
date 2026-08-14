"""
fbx.py

Conversión de la jerarquía de un FBX a nuestro
Bone Tree interno utilizando assimp-py.

No hace:
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


# ============================================================
# LOAD
# ============================================================

def load_fbx_skeleton(fbx_path):
    """
    Carga un FBX y convierte su jerarquía esquelética
    en nuestro Bone Tree.

    La detección del root no depende de nombres concretos.
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

    joint_root = _find_skeleton_root(
        scene.root_node
    )

    if joint_root is None:
        raise ValueError(
            "No se encontró una jerarquía "
            "esquelética en el FBX."
        )

    return _build_bone_tree(
        joint_root
    )


# ============================================================
# SKELETON ROOT DETECTION
# ============================================================

def _count_descendants(node):
    """
    Cuenta recursivamente los descendientes de un nodo.
    """

    count = 0

    for child in node.children:

        count += 1
        count += _count_descendants(
            child
        )

    return count

def _find_skeleton_root(root):
    """
    Busca la raíz de la jerarquía esquelética.

    El FBX suele contener un nodo contenedor que tiene
    como hijos la jerarquía de huesos y la geometría.

    No se utilizan nombres concretos.

    Se selecciona el hijo con mayor número de
    descendientes estructurales.
    """

    def count_descendants(node):

        count = 0

        for child in node.children:

            count += 1
            count += count_descendants(child)

        return count

    # --------------------------------------------------
    # Caso habitual:
    #
    # RootNode
    #   └── Container
    #        ├── Skeleton
    #        └── Mesh
    #
    # Primero descendemos hasta el container.
    # --------------------------------------------------

    if not root.children:
        return None

    # RootNode normalmente tiene un único container.
    container = root.children[0]

    if not container.children:
        return None

    candidates = []

    for child in container.children:

        descendants = count_descendants(
            child
        )

        if descendants > 0:

            candidates.append(
                (
                    descendants,
                    child,
                )
            )

    if not candidates:
        return None

    # Mayor jerarquía = candidato esquelético.
    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates[0][1]


# ============================================================
# BONE TREE
# ============================================================

def _build_bone_tree(
    node,
    parent_transform=None,
    parent_bone=None,
):
    """
    Convierte recursivamente un nodo Assimp
    en nuestro Bone Tree.

    Se conservan todos los nodos de la jerarquía
    seleccionada.
    """

    local_transform = np.array(
        node.transformation,
        dtype=float,
    )

    if parent_transform is None:

        global_transform = (
            local_transform
        )

    else:

        global_transform = (
            parent_transform
            @ local_transform
        )

    position = global_transform[
        :3,
        3,
    ]

    node_id = (
        node.node_id
        if hasattr(node, "node_id")
        else node.name
    )

    bone = Bone(
        node_id,
        position.copy(),
    )

    # Nombre real del nodo FBX.
    bone.name = node.name

    if parent_bone is not None:

        bone.parent = parent_bone

        parent_bone.children.append(
            bone
        )

    for child in node.children:

        _build_bone_tree(
            child,
            global_transform,
            bone,
        )

    return bone