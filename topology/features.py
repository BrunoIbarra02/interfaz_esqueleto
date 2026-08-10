"""
Skeleton Features

Características extraídas de un Bone Tree.
"""

import numpy as np

from dataclasses import dataclass



@dataclass
class SkeletonFeatures:
    """
    Características estructurales y geométricas
    de un esqueleto.
    """

    ################################################
    # TOPOLOGÍA
    ################################################

    node_count: int = 0
    leaf_count: int = 0
    branch_count: int = 0
    max_children: int = 0
    max_depth: int = 0

    ################################################
    # GEOMETRÍA
    ################################################

    bone_length_min: float = 0.0
    bone_length_max: float = 0.0
    bone_length_mean: float = 0.0
    bone_length_std: float = 0.0


################################################
# TOPOLOGY
################################################

def _extract_topology(root_bone, features):
    """
    Extrae las características topológicas
    del Bone Tree.
    """

    stack = [(root_bone, 0)]

    while stack:

        bone, depth = stack.pop()

        features.node_count += 1

        features.max_depth = max(
            features.max_depth,
            depth,
        )

        child_count = len(bone.children)

        if child_count == 0:
            features.leaf_count += 1

        if child_count > 1:
            features.branch_count += 1

        features.max_children = max(
            features.max_children,
            child_count,
        )

        for child in bone.children:
            stack.append(
                (child, depth + 1)
            )


################################################
# GEOMETRY
################################################

def _walk_lengths(bone):
    """
    Calcula la longitud de cada hueso
    respecto a su padre.
    """

    for child in bone.children:

        child.length = np.linalg.norm(
            np.array(child.position)
            - np.array(bone.position)
        )

        _walk_lengths(child)


def _collect_bone_lengths(bone, lengths):
    """
    Recoge las longitudes de todos los huesos.
    """

    if bone.parent is not None:
        lengths.append(bone.length)

    for child in bone.children:
        _collect_bone_lengths(
            child,
            lengths,
        )


def _extract_geometry(root_bone, features):
    """
    Extrae estadísticas de las longitudes
    de los huesos.
    """

    _walk_lengths(root_bone)

    lengths = []

    _collect_bone_lengths(
        root_bone,
        lengths,
    )

    if not lengths:
        return

    features.bone_length_min = min(lengths)

    features.bone_length_max = max(lengths)

    features.bone_length_mean = (
        sum(lengths)
        / len(lengths)
    )

    features.bone_length_std = float(
        np.std(lengths)
    )


################################################
# MAIN
################################################

def extract_features(root_bone):
    """
    Extrae las características de un Bone Tree.
    """

    features = SkeletonFeatures()

    _extract_topology(
        root_bone,
        features,
    )

    _extract_geometry(
        root_bone,
        features,
    )

    return features