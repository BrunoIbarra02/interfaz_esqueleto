"""
Skeleton Features

Características extraídas de Bone Trees y grafos
de esqueletos.

Este módulo contiene:

- características básicas de un Bone Tree;
- características agregadas de un Skeleton/Forest;
- firmas de skin;
- firmas geométricas;
- firma estructural común para comparar:
    - rigs de FBX;
    - skins de GLB;
    - curve skeletons de GLB sin skin.
"""

from dataclasses import dataclass, field

import networkx as nx
import numpy as np


# ============================================================
# SKELETON FEATURES
# ============================================================

@dataclass
class SkeletonFeatures:
    """
    Características estructurales y geométricas
    de un Bone Tree.
    """

    # --------------------------------------------------------
    # TOPOLOGÍA
    # --------------------------------------------------------

    node_count: int = 0
    leaf_count: int = 0
    branch_count: int = 0
    max_children: int = 0
    max_depth: int = 0

    # --------------------------------------------------------
    # GEOMETRÍA
    # --------------------------------------------------------

    bone_length_min: float = 0.0
    bone_length_max: float = 0.0
    bone_length_mean: float = 0.0
    bone_length_std: float = 0.0


# ============================================================
# FOREST FEATURES
# ============================================================

@dataclass
class ForestFeatures:
    """
    Características estructurales de un bosque
    de esqueletos desconectados.

    Se utiliza para modelos GLB sin skin
    cuya geometría produce múltiples componentes.
    """

    # --------------------------------------------------------
    # GLOBAL
    # --------------------------------------------------------

    component_count: int = 0
    node_count: int = 0
    edge_count: int = 0
    leaf_count: int = 0
    branch_count: int = 0

    # --------------------------------------------------------
    # COMPONENT SIZE
    # --------------------------------------------------------

    component_size_mean: float = 0.0
    component_size_median: float = 0.0
    component_size_std: float = 0.0

    component_size_p25: float = 0.0
    component_size_p75: float = 0.0
    component_size_p90: float = 0.0

    # --------------------------------------------------------
    # LEAVES
    # --------------------------------------------------------

    leaf_mean: float = 0.0
    leaf_median: float = 0.0

    # --------------------------------------------------------
    # BRANCHES
    # --------------------------------------------------------

    branch_mean: float = 0.0
    branch_median: float = 0.0

    # --------------------------------------------------------
    # STRUCTURAL DENSITY
    # --------------------------------------------------------

    leaf_density: float = 0.0
    branch_density: float = 0.0

    # --------------------------------------------------------
    # DEGREE
    # --------------------------------------------------------

    degree_histogram: list[int] = field(
        default_factory=list
    )

    max_degree: int = 0

    # --------------------------------------------------------
    # DEPTH
    # --------------------------------------------------------

    max_depth: int = 0
    depth_mean: float = 0.0
    depth_median: float = 0.0

    # --------------------------------------------------------
    # LENGTHS
    # --------------------------------------------------------

    normalized_length_min: float = 0.0
    normalized_length_max: float = 0.0
    normalized_length_mean: float = 0.0
    normalized_length_std: float = 0.0

    normalized_lengths: list[float] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # SYMMETRY
    # --------------------------------------------------------

    symmetry_score: float = 0.0


# ============================================================
# STRUCTURAL SIGNATURE
# ============================================================

@dataclass
class StructuralSignature:
    """
    Representación estructural común utilizada para
    comparar esqueletos.

    Puede construirse a partir de:

    - un Bone Tree;
    - un grafo de joints de un FBX;
    - un grafo de joints de un GLB con skin;
    - un curve skeleton de un GLB sin skin.
    """

    source: str = "unknown"

    # --------------------------------------------------------
    # TOPOLOGÍA
    # --------------------------------------------------------

    node_count: int = 0
    edge_count: int = 0

    leaf_count: int = 0
    branch_count: int = 0

    max_degree: int = 0

    degree_histogram: list[int] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # PROFUNDIDAD
    # --------------------------------------------------------

    max_depth: int = 0
    depth_mean: float = 0.0
    depth_median: float = 0.0

    # --------------------------------------------------------
    # LONGITUDES NORMALIZADAS
    # --------------------------------------------------------

    normalized_lengths: list[float] = field(
        default_factory=list
    )

    normalized_length_min: float = 0.0
    normalized_length_max: float = 0.0
    normalized_length_mean: float = 0.0
    normalized_length_std: float = 0.0

    # --------------------------------------------------------
    # SIMETRÍA
    # --------------------------------------------------------

    symmetry_score: float = 0.0

    # --------------------------------------------------------
    # MORFOLOGÍA
    # --------------------------------------------------------
    # Se genera a partir del mismo grafo estructural.
    # La importación de MorphologySignature se mantiene
    # diferida para evitar acoplamiento/ciclos de importación.
    morphology_signature: "MorphologySignature | None" = None


# ============================================================
# GLB SKIN SIGNATURE
# ============================================================

@dataclass
class SkinSignature:
    """
    Firma estructural de un GLB que contiene skin.
    """

    source: str = "skin"

    joint_count: int = 0
    leaf_count: int = 0
    root_count: int = 0

    names: list[str] = field(
        default_factory=list
    )


# ============================================================
# GLB GEOMETRY SIGNATURE
# ============================================================

@dataclass
class GeometrySignature:
    """
    Firma geométrica de un modelo sin skin.

    Es independiente de orientación y escala.
    """

    source: str = "geometry"

    aspect_signature: list[float] = field(
        default_factory=list
    )

    shape_histogram: list[float] = field(
        default_factory=list
    )

    vertex_count: int = 0


# ============================================================
# TOPOLOGY - BONE TREE
# ============================================================

def _extract_topology(
    root_bone,
    features,
):
    """
    Extrae las características topológicas
    del Bone Tree.
    """

    stack = [
        (
            root_bone,
            0,
        )
    ]

    while stack:

        bone, depth = stack.pop()

        features.node_count += 1

        features.max_depth = max(
            features.max_depth,
            depth,
        )

        child_count = len(
            bone.children
        )

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
                (
                    child,
                    depth + 1,
                )
            )


# ============================================================
# GEOMETRY - BONE TREE
# ============================================================

def _walk_lengths(
    bone,
):
    """
    Calcula la longitud de cada Bone
    respecto a su padre.
    """

    for child in bone.children:

        child.length = np.linalg.norm(
            np.asarray(
                child.position,
                dtype=float,
            )
            -
            np.asarray(
                bone.position,
                dtype=float,
            )
        )

        _walk_lengths(
            child
        )


def _collect_bone_lengths(
    bone,
    lengths,
):
    """
    Recoge las longitudes de todos los Bones.
    """

    if bone.parent is not None:

        lengths.append(
            bone.length
        )

    for child in bone.children:

        _collect_bone_lengths(
            child,
            lengths,
        )


def _extract_geometry(
    root_bone,
    features,
):
    """
    Extrae estadísticas de las longitudes
    de los Bones.
    """

    _walk_lengths(
        root_bone
    )

    lengths = []

    _collect_bone_lengths(
        root_bone,
        lengths,
    )

    if not lengths:
        return

    features.bone_length_min = min(
        lengths
    )

    features.bone_length_max = max(
        lengths
    )

    features.bone_length_mean = (
        sum(lengths)
        / len(lengths)
    )

    features.bone_length_std = float(
        np.std(
            lengths
        )
    )


# ============================================================
# SKELETON FEATURES
# ============================================================

def extract_features(
    root_bone,
):
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


# ============================================================
# FOREST FEATURES
# ============================================================

def extract_forest_features(
    skeleton,
):
    """
    Extrae características estructurales de un Skeleton
    que puede contener múltiples componentes desconectados.

    Parameters
    ----------
    skeleton
        Objeto skeletor.Skeleton.

    Returns
    -------
    ForestFeatures
        Firma agregada del bosque.
    """

    features = ForestFeatures()

    graph = skeleton.get_graph()

    if graph.is_directed():

        graph = graph.to_undirected()

    components = list(
        nx.connected_components(
            graph
        )
    )

    if not components:

        return features

    # --------------------------------------------------------
    # GLOBAL
    # --------------------------------------------------------

    features.component_count = len(
        components
    )

    features.node_count = (
        graph.number_of_nodes()
    )

    features.edge_count = (
        graph.number_of_edges()
    )

    # --------------------------------------------------------
    # COMPONENTES
    # --------------------------------------------------------

    component_sizes = []
    component_leaves = []
    component_branches = []

    for component in components:

        subgraph = graph.subgraph(
            component
        )

        size = (
            subgraph.number_of_nodes()
        )

        component_sizes.append(
            size
        )

        leaves = sum(
            degree == 1
            for _, degree
            in subgraph.degree()
        )

        branches = sum(
            degree > 2
            for _, degree
            in subgraph.degree()
        )

        component_leaves.append(
            leaves
        )

        component_branches.append(
            branches
        )

        features.leaf_count += leaves
        features.branch_count += branches

    # --------------------------------------------------------
    # COMPONENT SIZE
    # --------------------------------------------------------

    features.component_size_mean = float(
        np.mean(
            component_sizes
        )
    )

    features.component_size_median = float(
        np.median(
            component_sizes
        )
    )

    features.component_size_std = float(
        np.std(
            component_sizes
        )
    )

    features.component_size_p25 = float(
        np.percentile(
            component_sizes,
            25,
        )
    )

    features.component_size_p75 = float(
        np.percentile(
            component_sizes,
            75,
        )
    )

    features.component_size_p90 = float(
        np.percentile(
            component_sizes,
            90,
        )
    )

    # --------------------------------------------------------
    # LEAVES
    # --------------------------------------------------------

    features.leaf_mean = float(
        np.mean(
            component_leaves
        )
    )

    features.leaf_median = float(
        np.median(
            component_leaves
        )
    )

    # --------------------------------------------------------
    # BRANCHES
    # --------------------------------------------------------

    features.branch_mean = float(
        np.mean(
            component_branches
        )
    )

    features.branch_median = float(
        np.median(
            component_branches
        )
    )

    # --------------------------------------------------------
    # STRUCTURAL FEATURES
    # --------------------------------------------------------

    features.leaf_density = (
        features.leaf_count
        / max(
            features.node_count,
            1,
        )
    )

    features.branch_density = (
        features.branch_count
        / max(
            features.node_count,
            1,
        )
    )

    features.max_degree = max(
        (
            degree
            for _, degree
            in graph.degree()
        ),
        default=0,
    )

    features.degree_histogram = (
        _degree_histogram(
            graph
        )
    )

    depths = _graph_depths(
        graph
    )

    if depths:

        depth_values = list(
            depths.values()
        )

        features.max_depth = max(
            depth_values
        )

        features.depth_mean = float(
            np.mean(
                depth_values
            )
        )

        features.depth_median = float(
            np.median(
                depth_values
            )
        )

    normalized_lengths = (
        _normalized_graph_lengths(
            graph
        )
    )

    features.normalized_lengths = (
        normalized_lengths
    )

    if normalized_lengths:

        features.normalized_length_min = min(
            normalized_lengths
        )

        features.normalized_length_max = max(
            normalized_lengths
        )

        features.normalized_length_mean = float(
            np.mean(
                normalized_lengths
            )
        )

        features.normalized_length_std = float(
            np.std(
                normalized_lengths
            )
        )

    features.symmetry_score = (
        graph_symmetry(
            graph
        )
    )

    return features


# ============================================================
# GRAPH DEGREE HISTOGRAM
# ============================================================

def _degree_histogram(
    graph,
):
    """
    Genera:

        degree 0
        degree 1
        degree 2
        degree 3
        degree 4
        degree >=5
    """

    histogram = [
        0,
        0,
        0,
        0,
        0,
        0,
    ]

    for _, degree in graph.degree():

        if degree >= 5:

            histogram[5] += 1

        else:

            histogram[degree] += 1

    return histogram

# ============================================================
# GRAPH DEPTH
# ============================================================

def _graph_depths(graph, roots=None):
    """
    Calcula la profundidad topológica de los nodos.

    Parameters
    ----------
    graph : nx.Graph
        Grafo no dirigido.

    roots : iterable, optional
        Raíces explícitas por componente.

        Si se proporciona una raíz para una componente,
        se utiliza esa raíz.

        Si no se proporciona raíz para una componente,
        se utiliza el centro topológico de dicha componente.

    Returns
    -------
    dict
        node -> depth
    """

    depths = {}

    # --------------------------------------------------
    # Normalizar roots
    # --------------------------------------------------

    root_set = set(
        roots
        if roots is not None
        else []
    )

    # --------------------------------------------------
    # Procesar cada componente por separado.
    # --------------------------------------------------

    for component in nx.connected_components(
        graph
    ):

        component = set(component)

        # ----------------------------------------------
        # Buscar raíz explícita perteneciente
        # a esta componente.
        # ----------------------------------------------

        component_roots = (
            root_set & component
        )

        if component_roots:

            # Si hay varias raíces explícitas,
            # usamos una de forma determinista.
            root = min(
                component_roots
            )

        else:

            # ------------------------------------------
            # Sin raíz explícita:
            # utilizar el centro topológico.
            # ------------------------------------------

            subgraph = graph.subgraph(
                component
            )

            centers = nx.center(
                subgraph
            )

            root = min(
                centers
            )

        # ----------------------------------------------
        # BFS desde la raíz.
        # ----------------------------------------------

        component_depths = nx.single_source_shortest_path_length(
            graph,
            root,
        )

        depths.update(
            component_depths
        )

    return depths


# ============================================================
# GRAPH LENGTHS
# ============================================================

def _edge_length(
    graph,
    a,
    b,
):
    """
    Obtiene la longitud de una arista.

    Prioridad:

    1. posiciones de los nodos;
    2. atributo 'length';
    3. 1.0 como fallback.
    """

    position_a = graph.nodes[
        a
    ].get(
        "position"
    )

    position_b = graph.nodes[
        b
    ].get(
        "position"
    )

    if (
        position_a is not None
        and position_b is not None
    ):

        return float(
            np.linalg.norm(
                np.asarray(
                    position_a,
                    dtype=float,
                )
                -
                np.asarray(
                    position_b,
                    dtype=float,
                )
            )
        )

    length = graph.edges[
        a,
        b
    ].get(
        "length"
    )

    if length is not None:

        return float(
            length
        )

    return 1.0


def _normalized_graph_lengths(
    graph,
):
    """
    Devuelve las longitudes de las aristas
    normalizadas respecto a la longitud total.
    """

    if graph.number_of_edges() == 0:

        return []

    lengths = [
        _edge_length(
            graph,
            a,
            b,
        )
        for a, b
        in graph.edges()
    ]

    total = sum(
        lengths
    )

    if total <= 1e-12:

        return [
            0.0
            for _ in lengths
        ]

    return [
        float(
            length / total
        )
        for length in lengths
    ]


# ============================================================
# GRAPH SYMMETRY
# ============================================================

def graph_symmetry(
    graph,
):
    """
    Estima simetría bilateral cuando el grafo dispone
    de posiciones 3D.

    No intenta inferir anatomía a partir de nombres.

    Si no hay posiciones suficientes devuelve 0.0.
    """

    positions = []

    nodes = []

    for node in graph.nodes:

        position = graph.nodes[
            node
        ].get(
            "position"
        )

        if position is None:

            continue

        positions.append(
            np.asarray(
                position,
                dtype=float,
            )
        )

        nodes.append(
            node
        )

    if len(positions) < 4:

        return 0.0

    points = np.asarray(
        positions,
        dtype=float,
    )

    centered = (
        points
        - points.mean(
            axis=0
        )
    )

    _, _, basis = np.linalg.svd(
        centered,
        full_matrices=False,
    )

    canonical = (
        centered
        @ basis.T
    )

    spans = np.ptp(
        canonical,
        axis=0,
    )

    longitudinal_axis = int(
        np.argmax(
            spans
        )
    )

    lateral_candidates = [
        index
        for index in range(3)
        if index != longitudinal_axis
    ]

    if not lateral_candidates:

        return 0.0

    lateral_axis = max(
        lateral_candidates,
        key=lambda index:
            spans[index],
    )

    lateral = canonical[
        :,
        lateral_axis,
    ]

    positive = [
        index
        for index, value
        in enumerate(lateral)
        if value > 0
    ]

    negative = [
        index
        for index, value
        in enumerate(lateral)
        if value < 0
    ]

    if not positive or not negative:

        return 0.0

    # --------------------------------------------------------
    # Para cada punto de un lado buscamos el punto más próximo
    # reflejado en el otro lado.
    # --------------------------------------------------------

    positive_points = canonical[
        positive
    ]

    negative_points = canonical[
        negative
    ]

    reflected_positive = (
        positive_points.copy()
    )

    reflected_positive[
        :,
        lateral_axis
    ] *= -1.0

    distances = []

    for point in reflected_positive:

        distances.append(
            np.min(
                np.linalg.norm(
                    negative_points
                    - point,
                    axis=1,
                )
            )
        )

    scale = max(
        float(
            np.linalg.norm(
                spans
            )
        ),
        1e-9,
    )

    mean_distance = (
        float(
            np.mean(
                distances
            )
        )
        / scale
    )

    return float(
        np.clip(
            1.0
            - mean_distance,
            0.0,
            1.0,
        )
    )


# ============================================================
# STRUCTURAL SIGNATURE FROM GRAPH
# ============================================================

def structural_signature_from_graph(
    graph,
    source="graph",
    roots=None,
):
    """
    Convierte un networkx.Graph en StructuralSignature.

    Esta es la función que posteriormente utilizarán:

        FBX rig
        GLB skin
        GLB curve skeleton

    para acabar todos en la misma representación.
    """

    if graph is None:

        return StructuralSignature(
            source=source
        )

    if graph.is_directed():

        graph = graph.to_undirected()

    graph = graph.copy()

    node_count = (
        graph.number_of_nodes()
    )

    edge_count = (
        graph.number_of_edges()
    )

    leaf_count = sum(
        graph.degree(node) == 1
        for node in graph
    )

    branch_count = sum(
        graph.degree(node) >= 3
        for node in graph
    )

    max_degree = max(
        (
            degree
            for _, degree
            in graph.degree()
        ),
        default=0,
    )

    degree_histogram = (
        _degree_histogram(
            graph
        )
    )

    depths = _graph_depths(
        graph,
        roots=roots,
    )

    depth_values = list(
        depths.values()
    )

    if depth_values:

        max_depth = max(
            depth_values
        )

        depth_mean = float(
            np.mean(
                depth_values
            )
        )

        depth_median = float(
            np.median(
                depth_values
            )
        )

    else:

        max_depth = 0
        depth_mean = 0.0
        depth_median = 0.0

    normalized_lengths = (
        _normalized_graph_lengths(
            graph
        )
    )

    if normalized_lengths:

        length_min = min(
            normalized_lengths
        )

        length_max = max(
            normalized_lengths
        )

        length_mean = float(
            np.mean(
                normalized_lengths
            )
        )

        length_std = float(
            np.std(
                normalized_lengths
            )
        )

    else:

        length_min = 0.0
        length_max = 0.0
        length_mean = 0.0
        length_std = 0.0

    # --------------------------------------------------------
    # MORFOLOGÍA
    # --------------------------------------------------------
    # Se calcula sobre exactamente el mismo grafo que alimenta
    # StructuralSignature. No se reconstruye el skeleton.
    from topology.morphology import build_morphology_signature

    morphology_signature = build_morphology_signature(
        graph,
        source=source,
    )

    return StructuralSignature(
        source=source,
        node_count=node_count,
        edge_count=edge_count,
        leaf_count=leaf_count,
        branch_count=branch_count,
        max_degree=max_degree,
        degree_histogram=degree_histogram,
        max_depth=max_depth,
        depth_mean=depth_mean,
        depth_median=depth_median,
        normalized_lengths=normalized_lengths,
        normalized_length_min=length_min,
        normalized_length_max=length_max,
        normalized_length_mean=length_mean,
        normalized_length_std=length_std,
        symmetry_score=graph_symmetry(
            graph
        ),
        morphology_signature=morphology_signature,
    )


# ============================================================
# STRUCTURAL SIGNATURE FROM BONE TREE
# ============================================================

def structural_signature_from_bone_tree(
    root_bone,
    source="bone_tree",
):
    """
    Convierte nuestro Bone Tree en StructuralSignature.

    No depende de los nombres de los huesos.
    """

    graph = nx.Graph()

    counter = 0

    stack = [
        (
            root_bone,
            None,
        )
    ]

    ids = {}

    while stack:

        bone, parent_id = stack.pop()

        node_id = counter
        counter += 1

        ids[id(bone)] = node_id

        position = getattr(
            bone,
            "position",
            None,
        )

        graph.add_node(
            node_id,
            name=getattr(
                bone,
                "name",
                None,
            ),
            position=(
                np.asarray(
                    position,
                    dtype=float,
                )
                if position is not None
                else None
            ),
        )

        if parent_id is not None:

            graph.add_edge(
                parent_id,
                node_id,
            )

        for child in bone.children:

            stack.append(
                (
                    child,
                    node_id,
                )
            )

    return structural_signature_from_graph(
        graph,
        source=source,
    )


# ============================================================
# SKIN SIGNATURE FROM BONE TREE
# ============================================================

def extract_skin_signature(
    root_bone,
):
    """
    Genera una firma de skin a partir de nuestro Bone Tree.

    No depende de los nombres para construir la jerarquía.
    """

    signature = SkinSignature()

    stack = [
        root_bone
    ]

    while stack:

        bone = stack.pop()

        signature.joint_count += 1

        child_count = len(
            bone.children
        )

        if child_count == 0:

            signature.leaf_count += 1

        if bone.parent is None:

            signature.root_count += 1

        name = getattr(
            bone,
            "name",
            None,
        )

        if name:

            signature.names.append(
                str(name)
            )

        for child in bone.children:

            stack.append(
                child
            )

    return signature


# ============================================================
# FOREST FEATURES FROM BONE TREE
# ============================================================

def forest_features_from_bone_tree(
    root_bone,
):
    """
    Convierte un Bone Tree en ForestFeatures.

    Se utiliza para comparar la estructura básica de un rig
    con las características de un curve skeleton.
    """

    features = ForestFeatures()

    stack = [
        root_bone
    ]

    while stack:

        bone = stack.pop()

        features.node_count += 1

        child_count = len(
            bone.children
        )

        if child_count == 0:

            features.leaf_count += 1

        if child_count > 1:

            features.branch_count += 1

        if bone.parent is not None:

            features.edge_count += 1

        for child in bone.children:

            stack.append(
                child
            )

    features.component_count = 1

    features.component_size_mean = float(
        features.node_count
    )

    features.component_size_median = float(
        features.node_count
    )

    features.component_size_std = 0.0

    features.component_size_p25 = float(
        features.node_count
    )

    features.component_size_p75 = float(
        features.node_count
    )

    features.component_size_p90 = float(
        features.node_count
    )

    features.leaf_mean = float(
        features.leaf_count
    )

    features.leaf_median = float(
        features.leaf_count
    )

    features.branch_mean = float(
        features.branch_count
    )

    features.branch_median = float(
        features.branch_count
    )

    features.leaf_density = (
        features.leaf_count
        / max(
            features.node_count,
            1,
        )
    )

    features.branch_density = (
        features.branch_count
        / max(
            features.node_count,
            1,
        )
    )

    return features


# ============================================================
# SHAPE SIGNATURE
# ============================================================

def shape_signature(
    vertices,
):
    """
    Genera una firma geométrica independiente
    de orientación y escala.

    Basado en el algoritmo original:

    - centra los vértices;
    - calcula PCA mediante SVD;
    - transforma los puntos a los ejes principales;
    - normaliza la escala;
    - discretiza en una rejilla 8x8x8;
    - genera un histograma espacial.

    Esta firma se conserva para utilizarla posteriormente
    como control de calidad o desempate.
    """

    vertices = np.asarray(
        vertices,
        dtype=float,
    )

    if (
        vertices.ndim != 2
        or vertices.shape[1] != 3
    ):

        raise ValueError(
            "vertices debe tener forma (N, 3)."
        )

    if len(vertices) == 0:

        return GeometrySignature()

    centered = (
        vertices
        - vertices.mean(
            axis=0
        )
    )

    _, _, basis = np.linalg.svd(
        centered,
        full_matrices=False,
    )

    points = (
        centered
        @ basis.T
    )

    spans = np.ptp(
        points,
        axis=0,
    )

    points = np.abs(
        points
        / np.maximum(
            spans / 2,
            1e-9,
        )
    )

    cells = np.clip(
        (
            points * 8
        ).astype(int),
        0,
        7,
    )

    histogram = np.zeros(
        (8, 8, 8),
        dtype=np.float64,
    )

    np.add.at(
        histogram,
        (
            cells[:, 0],
            cells[:, 1],
            cells[:, 2],
        ),
        1,
    )

    histogram /= max(
        histogram.sum(),
        1,
    )

    aspect = (
        spans
        / max(
            spans.max(),
            1e-9,
        )
    )

    return GeometrySignature(
        aspect_signature=[
            round(
                float(value),
                4,
            )
            for value in np.sort(
                aspect
            )
        ],
        shape_histogram=[
            round(
                float(value),
                8,
            )
            for value in histogram.ravel()
        ],
        vertex_count=len(
            vertices
        ),
    )