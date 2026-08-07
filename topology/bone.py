import numpy as np


class Bone:
    """
    Representa un hueso del esqueleto.
    """

    def __init__(self, node_id, position):

        ################################################
        # IDENTIDAD
        ################################################

        self.node_id = node_id

        ################################################
        # GEOMETRÍA
        ################################################

        self.position = position

        ################################################
        # ÁRBOL
        ################################################

        self.parent = None
        self.children = []

        ################################################
        # FEATURES
        ################################################

        self.length = 0.0
        self.depth = 0

    def __repr__(self):
        return f"Bone({self.node_id})"


def get_root_to_leaf_paths(root):
    """
    Devuelve todos los caminos desde la raíz hasta cada hoja.
    """

    paths = []

    def walk(bone, path):

        path.append(bone)

        if not bone.children:
            paths.append(path.copy())

        else:
            for child in bone.children:
                walk(child, path)

        path.pop()

    walk(root, [])

    return paths

def get_brances(root):
    pass