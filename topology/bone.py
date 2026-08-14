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

def build_bone_forest(skeleton):
    """
    Convierte el Skeleton de Skeletor en un bosque
    de jerarquías Bone.

    Devuelve una lista con una raíz por cada
    componente del Skeleton.
    """

    graph = skeleton.get_graph().reverse(copy=False)

    swc = skeleton.swc

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

    bones = {}

    for node in graph.nodes():

        bones[node] = Bone(
            node,
            positions[node],
        )

    for parent_id, child_id in graph.edges():

        parent = bones[parent_id]
        child = bones[child_id]

        parent.children.append(child)
        child.parent = parent

    roots = [
        bones[node]
        for node, indegree in graph.in_degree()
        if indegree == 0
    ]

    return roots

def simplify_bone_tree(
    root,
    remove_ik=True,
):
    """
    Simplifica un Bone Tree eliminando controles IK
    y contrayendo cadenas de un único hijo.

    El árbol original no se modifica.
    """

    def clone_filtered(
        bone,
        parent=None,
    ):
        name = getattr(
            bone,
            "name",
            "",
        )

        if (
            remove_ik
            and "IK" in name.upper()
        ):
            return None

        new_bone = Bone(
            bone.node_id,
            np.asarray(
                bone.position,
                dtype=float,
            ).copy(),
        )

        new_bone.name = name
        new_bone.parent = parent

        for child in bone.children:

            copied = clone_filtered(
                child,
                new_bone,
            )

            if copied is not None:
                new_bone.children.append(
                    copied
                )

        return new_bone

    filtered = clone_filtered(root)

    if filtered is None:
        raise ValueError(
            "La raíz fue eliminada."
        )

    def distance(a, b):

        return float(
            np.linalg.norm(
                b.position
                - a.position
            )
        )

    def collapse(
        bone,
        is_root=False,
    ):
        """
        Simplifica recursivamente un nodo.

        Los nodos con un único hijo se atraviesan
        hasta encontrar el siguiente punto estructural.
        """

        new_children = []

        for child in bone.children:

            current = child
            accumulated_length = distance(
                bone,
                current,
            )

            # ------------------------------------------
            # Atravesar cadena de grado 1.
            # ------------------------------------------

            while len(
                current.children
            ) == 1:

                next_bone = (
                    current.children[0]
                )

                accumulated_length += (
                    distance(
                        current,
                        next_bone,
                    )
                )

                current = next_bone

            # ------------------------------------------
            # Simplificar recursivamente el punto
            # estructural encontrado.
            # ------------------------------------------

            current.parent = bone

            collapse(
                current,
                is_root=False,
            )

            current.length = (
                accumulated_length
            )

            new_children.append(
                current
            )

        bone.children = new_children

        return bone

    collapse(
        filtered,
        is_root=True,
    )

    filtered.parent = None

    return filtered

def is_rig_control(bone):
    """
    Determina si un Bone parece ser un control del rig.

    La detección es deliberadamente conservadora.
    """

    name = getattr(
        bone,
        "name",
        "",
    ).upper()

    control_tokens = (
        "_IK",
        "IK_",
        "_IK_",
        "CTRL",
        "CONTROL",
        "MCH",
    )

    return any(
        token in name
        for token in control_tokens
    )

def remove_rig_controls(root):
    """
    Elimina controles claramente identificables
    del Bone Tree.

    No modifica el árbol original.
    """

    def clone_filtered(
        bone,
        parent=None,
    ):

        if is_rig_control(bone):
            return None

        new_bone = Bone(
            bone.node_id,
            np.asarray(
                bone.position,
                dtype=float,
            ).copy(),
        )

        new_bone.name = getattr(
            bone,
            "name",
            "",
        )

        new_bone.parent = parent

        for child in bone.children:

            child_copy = clone_filtered(
                child,
                new_bone,
            )

            if child_copy is not None:

                new_bone.children.append(
                    child_copy
                )

        return new_bone

    result = clone_filtered(root)

    if result is None:

        raise ValueError(
            "La raíz fue identificada "
            "como control del rig."
        )

    return result

def extract_anatomical_skeleton(root):
    """
    Extrae una representación anatómica aproximada
    desde un Bone Tree de rig.

    Pipeline:

        Bone Tree
            ↓
        eliminar controles
            ↓
        Bone Tree anatómico

    No modifica el árbol original.
    """

    return remove_rig_controls(root)

def analyze_bone_roles(root):
    """
    Genera información estructural de cada nodo
    para estudiar posibles elementos auxiliares.

    No elimina nada.
    """

    def subtree_size(bone):

        return (
            1
            + sum(
                subtree_size(child)
                for child in bone.children
            )
        )

    def walk(bone, depth=0):

        info = {
            "name": getattr(
                bone,
                "name",
                "",
            ),
            "depth": depth,
            "children": len(
                bone.children
            ),
            "subtree_size": subtree_size(
                bone
            ),
            "is_leaf": (
                len(bone.children) == 0
            ),
        }

        print(info)

        for child in bone.children:

            walk(
                child,
                depth + 1,
            )

    walk(root)