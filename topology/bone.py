import numpy as np


class Bone:
    """
    Representa un hueso del esqueleto.
    """

    def __init__(self, node_id, position):

        self.node_id = node_id
        self.position = position

        self.parent = None
        self.children = []

        self.length = 0.0
        self.depth = 0

    def __repr__(self):
        return f"Bone({self.node_id})"


def build_bone_tree(skeleton):
    """
    Convierte el Skeleton de Skeletor en una jerarquía de Bone.
    """

    graph = skeleton.get_graph().reverse(copy=False)

    swc = skeleton.swc

    # Posiciones de los nodos
    positions = {}

    for _, row in swc.iterrows():

        positions[row.node_id] = np.array(
            [
                row.x,
                row.y,
                row.z,
            ],
            dtype=float,
        )

    # Crear los Bone
    bones = {}

    for node in graph.nodes():

        bones[node] = Bone(
            node,
            positions[node],
        )

    # Conectar padres e hijos
    for parent_id, child_id in graph.edges():

        parent = bones[parent_id]
        child = bones[child_id]

        parent.children.append(child)
        child.parent = parent

    # Buscar la raíz
    root = next(
        node
        for node, indegree in graph.in_degree()
        if indegree == 0
    )

    return bones[root]


def get_root_to_leaf_paths(root):
    """
    Devuelve todos los caminos desde la raíz
    hasta cada hoja.
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