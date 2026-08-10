"""
Skeleton Features

Representación de las características extraídas de un
esqueleto topológico.
"""

import numpy as np

from dataclasses import dataclass, field

from topology.bone import Bone, get_root_to_leaf_paths
from topology.branch import Branch


@dataclass
class SkeletonFeatures:
    """
    Características extraídas de un Skeleton.
    """

    ################################################
    # TOPOLOGÍA
    ################################################

    node_count: int = 0
    edge_count: int = 0

    root_count: int = 0
    leaf_count: int = 0

    branch_count: int = 0
    max_children: int = 0
    max_depth: int = 0

    ################################################
    # RAMAS
    ################################################

    branches: list[Branch] = field(default_factory=list)

    branch_length_min: float = 0.0
    branch_length_max: float = 0.0
    branch_length_mean: float = 0.0

    ################################################
    # GEOMETRÍA
    ################################################

    bone_length_min: float = 0.0
    bone_length_max: float = 0.0
    bone_length_mean: float = 0.0
    bone_length_std: float = 0.0

    ################################################
    # PROPORCIONES
    ################################################

    bbox = None

    bbox_extents: tuple[float, float, float] | None = None
    
    bbox_width_ratio: float = 0.0
    bbox_height_ratio: float = 0.0

    bbox_width: float = 0.0
    bbox_height: float = 0.0
    bbox_depth: float = 0.0


################################################
# TOPOLOGY
################################################

def _extract_topology(root_bone, features):
    """
    Extrae las características topológicas.
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

        features.edge_count += child_count

        for child in bone.children:
            stack.append((child, depth + 1))

    features.root_count = 1



################################################
# AUXILIAR
################################################

def _walk_lengths(bone):

    for child in bone.children:

        child.length = np.linalg.norm(
            np.array(child.position)
            - np.array(bone.position)
        )

        _walk_lengths(child)
        
def _collect_bone_lengths(bone, lengths):

    if bone.parent is not None:
        lengths.append(bone.length)

    for child in bone.children:
        _collect_bone_lengths(child, lengths)

################################################
# BRANCHES
################################################

def _extract_branch_lengths(root_bone,features):
    """
    Calcula la longitud geométrica de cada rama principal.
    """
    
    paths = get_root_to_leaf_paths(root_bone)
    
    for path in paths:

        length = 0.0

        for i in range(len(path) - 1):

            parent = path[i]
            child = path[i + 1]

            length += np.linalg.norm(
                np.array(child.position)
                - np.array(parent.position)
            )

        branch = Branch()
        branch.bones = path
        branch.bone_count = len(path)
        branch.length = length
        features.branches.append(branch)

    if features.branches:

        lengths = [
            branch.length
            for branch in features.branches
        ]

        features.branch_length_min = min(lengths)

        features.branch_length_max = max(lengths)

        features.branch_length_mean = (
            sum(lengths)
            / len(lengths)
        )


def _extract_branch_ratios(features):
    """
    Calcula el porcentaje que representa cada rama
    respecto al total.
    """

    total = sum(
        branch.length
        for branch in features.branches
    )

    if total == 0:
        return

    for branch in features.branches:

        branch.ratio = (
            branch.length / total
        )

    features.branches.sort(
        key=lambda branch: branch.ratio,
        reverse=True,
    )


################################################
# GEOMETRY
################################################

def _extract_geometry(root_bone, features):

    _walk_lengths(root_bone)

    lengths = []

    _collect_bone_lengths(
        root_bone,
        lengths,
    )

    if lengths:

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
# BBOX
################################################

def _extract_bbox(mesh, features):
    """
    Extrae la Bounding Box del modelo.
    """

    box = mesh.bounding_box_oriented

    features.bbox = box

    features.bbox_extents = tuple(
        box.extents
    )

    features.bbox_width = box.extents[0]
    features.bbox_height = box.extents[1]
    features.bbox_depth = box.extents[2]
    
    if features.bbox_depth > 0:
    
        features.bbox_width_ratio = (
            features.bbox_width /
            features.bbox_depth
        )
        
        features.bbox_height_ratio = (
            features.bbox_height /
            features.bbox_depth
        )


################################################
# MAIN
################################################

def extract_features(mesh, root_bone):
    """
    Extrae las características de un Skeleton.
    """

    features = SkeletonFeatures()

    _extract_topology(
        root_bone,
        features,
    )

    _extract_branch_lengths(root_bone,features)

    _extract_branch_ratios(features)

    _extract_geometry(
        root_bone,
        features,
    )

    _extract_bbox(
        mesh,
        features,
    )

    return features