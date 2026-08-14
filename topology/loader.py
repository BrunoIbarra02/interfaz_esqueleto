"""
loader.py

Responsabilidad:

- Cargar un modelo GLB.
- Comprobar si contiene skin.
- Extraer información estructural del skin.
- Extraer la geometría del GLB.
- Construir una malla trimesh a partir de la geometría.

No hace:

- No preprocesa la malla.
- No skeletoniza.
- No construye grafos.
- No realiza matching.
- No exporta resultados.
"""

from pygltflib import GLTF2
import numpy as np
import trimesh


# ============================================================
# LOAD
# ============================================================

def load_glb(glb_path):
    """
    Carga un archivo GLB.

    Parameters
    ----------
    glb_path : str
        Ruta del archivo GLB.

    Returns
    -------
    GLTF2
        Objeto GLTF cargado.
    """

    return GLTF2().load(
        glb_path
    )


# ============================================================
# SKIN
# ============================================================

def has_skin(gltf):
    """
    Comprueba si un modelo GLB contiene un skin.

    Returns
    -------
    bool
        True si contiene al menos un skin.
    """

    return bool(
        gltf.skins
    )


def get_skins(gltf):
    """
    Devuelve los skins definidos en el GLB.

    Returns
    -------
    list
        Lista de objetos Skin.
    """

    return gltf.skins or []


def get_skin_joints(gltf, skin_index=0):
    """
    Devuelve los índices de los nodes que forman
    parte del skin.

    Parameters
    ----------
    gltf : GLTF2
        Modelo GLB cargado.

    skin_index : int
        Índice del skin que se quiere consultar.

    Returns
    -------
    list[int]
        Índices de los nodes correspondientes a joints.
    """

    skins = gltf.skins or []

    if not skins:
        return []

    if skin_index < 0 or skin_index >= len(skins):
        raise IndexError(
            f"skin_index fuera de rango: {skin_index}"
        )

    skin = skins[skin_index]

    return list(
        skin.joints or []
    )


# ============================================================
# SKIN JOINT INFORMATION
# ============================================================

def get_joint_info(gltf, skin_index=0):
    """
    Extrae información básica de los joints de un skin.

    No interpreta todavía pesos, IK ni controles.

    Returns
    -------
    list[dict]

        Cada elemento contiene:

            index
            name
            children
            parent
            is_root
    """

    joint_indices = get_skin_joints(
        gltf,
        skin_index,
    )

    if not joint_indices:
        return []

    nodes = gltf.nodes or []

    joint_set = set(
        joint_indices
    )

    # --------------------------------------------------------
    # Buscar padres dentro del conjunto de joints.
    # --------------------------------------------------------

    parents = {}

    for parent_index in joint_indices:

        if (
            parent_index < 0
            or parent_index >= len(nodes)
        ):
            continue

        node = nodes[
            parent_index
        ]

        for child_index in (
            node.children or []
        ):

            if child_index in joint_set:

                parents[
                    child_index
                ] = parent_index

    # --------------------------------------------------------
    # Construcción de información.
    # --------------------------------------------------------

    joints = []

    for index in joint_indices:

        if (
            index < 0
            or index >= len(nodes)
        ):
            continue

        node = nodes[
            index
        ]

        parent = parents.get(
            index
        )

        joints.append(
            {
                "index": index,
                "name": (
                    node.name
                    or f"joint_{index}"
                ),
                "children": [
                    child
                    for child in (
                        node.children or []
                    )
                    if child in joint_set
                ],
                "parent": parent,
                "is_root": parent is None,
            }
        )

    return joints


def get_root_joints(gltf, skin_index=0):
    """
    Devuelve los joints raíz de un skin.

    Un root joint es un joint que no tiene como padre
    a otro joint perteneciente al mismo skin.

    Returns
    -------
    list[int]
        Índices de los root joints.
    """

    joints = get_joint_info(
        gltf,
        skin_index,
    )

    return [
        joint["index"]
        for joint in joints
        if joint["is_root"]
    ]


# ============================================================
# BUFFER HELPERS
# ============================================================

def _get_buffer_data(
    gltf,
    buffer_index,
):
    """
    Obtiene los bytes correspondientes a un buffer GLTF.
    """

    buffer = gltf.buffers[
        buffer_index
    ]

    if buffer.uri:

        return gltf.get_data_from_buffer_uri(
            buffer.uri
        )

    return gltf.binary_blob()


def _component_dtype(
    component_type,
):
    """
    Convierte un componentType GLTF en dtype numpy.
    """

    mapping = {
        5121: np.uint8,
        5123: np.uint16,
        5125: np.uint32,
        5126: np.float32,
    }

    if component_type not in mapping:

        raise ValueError(
            "componentType GLTF no soportado: "
            f"{component_type}"
        )

    return mapping[
        component_type
    ]


# ============================================================
# ACCESSOR
# ============================================================

def _read_accessor(
    gltf,
    accessor_index,
):
    """
    Lee un accessor GLTF como numpy.

    Soporta:

    - FLOAT32
    - UNSIGNED_BYTE
    - UNSIGNED_SHORT
    - UNSIGNED_INT

    y tiene en cuenta byteOffset y byteStride.
    """

    accessor = gltf.accessors[
        accessor_index
    ]

    if accessor.bufferView is None:

        raise ValueError(
            "Accessor sin bufferView: "
            f"{accessor_index}"
        )

    view = gltf.bufferViews[
        accessor.bufferView
    ]

    data = _get_buffer_data(
        gltf,
        view.buffer,
    )

    dtype = _component_dtype(
        accessor.componentType
    )

    component_counts = {
        "SCALAR": 1,
        "VEC2": 2,
        "VEC3": 3,
        "VEC4": 4,
    }

    if accessor.type not in component_counts:

        raise ValueError(
            "Tipo de accessor GLTF no soportado: "
            f"{accessor.type}"
        )

    component_count = component_counts[
        accessor.type
    ]

    item_size = (
        np.dtype(dtype).itemsize
        * component_count
    )

    stride = (
        view.byteStride
        or item_size
    )

    base_offset = (
        (view.byteOffset or 0)
        + (accessor.byteOffset or 0)
    )

    count = accessor.count

    # --------------------------------------------------------
    # Caso habitual: elementos contiguos.
    # --------------------------------------------------------

    if stride == item_size:

        values = np.frombuffer(
            data,
            dtype=dtype,
            count=count * component_count,
            offset=base_offset,
        )

        return values.reshape(
            count,
            component_count,
        )

    # --------------------------------------------------------
    # Caso interleaved: byteStride > tamaño del elemento.
    # --------------------------------------------------------

    values = np.ndarray(
        shape=(
            count,
            component_count,
        ),
        dtype=dtype,
        buffer=data,
        offset=base_offset,
        strides=(
            stride,
            np.dtype(dtype).itemsize,
        ),
    )

    return np.asarray(
        values
    )


# ============================================================
# GEOMETRY
# ============================================================

def get_vertices(gltf):
    """
    Extrae todos los vértices POSITION de las mallas
    del GLB.

    Parameters
    ----------
    gltf : GLTF2
        Modelo GLTF cargado.

    Returns
    -------
    numpy.ndarray
        Array de forma (N, 3).
    """

    vectors = []

    for mesh in gltf.meshes or []:

        for primitive in mesh.primitives or []:

            accessor_index = (
                primitive.attributes.POSITION
            )

            if accessor_index is None:
                continue

            values = _read_accessor(
                gltf,
                accessor_index,
            )

            if values.shape[1] != 3:

                raise ValueError(
                    "El accessor POSITION "
                    "no es VEC3."
                )

            vectors.append(
                values.astype(
                    np.float32,
                    copy=False,
                )
            )

    if not vectors:

        return np.empty(
            (0, 3),
            dtype=np.float32,
        )

    return np.vstack(
        vectors
    )


# ============================================================
# FACES
# ============================================================

def get_faces(gltf):
    """
    Extrae las caras triangulares de todas las primitives
    del GLB.

    Las primitives sin índices utilizan índices secuenciales.

    Returns
    -------
    numpy.ndarray
        Array de forma (N, 3).
    """

    faces = []

    vertex_offset = 0

    for mesh in gltf.meshes or []:

        for primitive in mesh.primitives or []:

            position_index = (
                primitive.attributes.POSITION
            )

            if position_index is None:
                continue

            position_accessor = (
                gltf.accessors[
                    position_index
                ]
            )

            vertex_count = (
                position_accessor.count
            )

            # ------------------------------------------------
            # Solo soportamos TRIANGLES aquí.
            #
            # mode GLTF:
            # 4 = TRIANGLES
            # ------------------------------------------------

            mode = (
                primitive.mode
                if primitive.mode is not None
                else 4
            )

            if mode != 4:

                raise ValueError(
                    "La primitive utiliza un modo "
                    f"no triangular: {mode}"
                )

            # ------------------------------------------------
            # Primitive indexada.
            # ------------------------------------------------

            if primitive.indices is not None:

                values = _read_accessor(
                    gltf,
                    primitive.indices,
                )

                indices = (
                    values.reshape(
                        -1
                    )
                    .astype(
                        np.int64,
                        copy=False,
                    )
                )

            # ------------------------------------------------
            # Primitive sin índices.
            # ------------------------------------------------

            else:

                indices = np.arange(
                    vertex_count,
                    dtype=np.int64,
                )

            if len(indices) % 3 != 0:

                raise ValueError(
                    "La primitive no contiene "
                    "un número de índices múltiplo de 3."
                )

            triangles = (
                indices.reshape(
                    -1,
                    3,
                )
                + vertex_offset
            )

            faces.append(
                triangles
            )

            vertex_offset += vertex_count

    if not faces:

        return np.empty(
            (0, 3),
            dtype=np.int64,
        )

    return np.vstack(
        faces
    )


# ============================================================
# TRIMESH
# ============================================================

def get_mesh(gltf):
    """
    Construye una malla trimesh a partir del GLB.

    Extrae:

        POSITION
        índices de las primitives

    y los combina en una única malla.

    Parameters
    ----------
    gltf : GLTF2
        Modelo GLTF cargado.

    Returns
    -------
    trimesh.Trimesh
        Malla sin procesar automáticamente.
    """

    vertices = get_vertices(
        gltf
    )

    faces = get_faces(
        gltf
    )

    if len(vertices) == 0:

        raise ValueError(
            "El GLB no contiene vértices POSITION."
        )

    if len(faces) == 0:

        raise ValueError(
            "El GLB no contiene caras triangulares."
        )

    return trimesh.Trimesh(
        vertices=vertices,
        faces=faces,
        process=False,
    )