"""
curve_graph.py

Conversión y simplificación de un curve skeleton de Skeletor.

Responsabilidad:
- Convertir el grafo de Skeletor a NetworkX.
- Conservar la posición 3D de los nodos.
- Calcular longitudes geométricas.
- Colapsar cadenas de nodos de grado 2.
- Conservar hojas y ramificaciones.
- Eliminar componentes claramente degeneradas.
- Mantener múltiples componentes cuando sean estructuralmente relevantes.

No hace:
- No carga GLB.
- No ejecuta Skeletor.
- No realiza matching.
- No calcula StructuralSignature.
- No exporta resultados.
"""

import networkx as nx
import numpy as np


# ============================================================
# SKELETON -> GRAPH
# ============================================================

def skeleton_to_graph(skeleton):
    """
    Convierte un Skeleton de Skeletor en un grafo
    NetworkX no dirigido.

    Los nodos contienen:

        position : np.ndarray shape (3,)

    Las aristas contienen:

        length : longitud geométrica de la arista.
    """

    raw_graph = skeleton.get_graph()

    graph = nx.Graph()

    vertices = np.asarray(
        skeleton.vertices,
        dtype=float,
    )

    # --------------------------------------------------------
    # NODOS
    # --------------------------------------------------------

    for node in raw_graph.nodes():

        node = int(node)

        graph.add_node(
            node,
            position=vertices[node].copy(),
        )

    # --------------------------------------------------------
    # ARISTAS
    # --------------------------------------------------------

    for a, b in raw_graph.edges():

        a = int(a)
        b = int(b)

        position_a = vertices[a]
        position_b = vertices[b]

        length = float(
            np.linalg.norm(
                position_b - position_a
            )
        )

        graph.add_edge(
            a,
            b,
            length=length,
        )

    return graph


# ============================================================
# CHAIN
# ============================================================

def _chain_between(
    graph,
    start,
    neighbour,
    anchors,
):
    """
    Recorre una cadena de nodos de grado 2.

    Parameters
    ----------
    graph : nx.Graph
        Grafo original.

    start : int
        Nodo anchor inicial.

    neighbour : int
        Primer nodo de la cadena.

    anchors : set
        Nodos que deben conservarse.

    Returns
    -------
    tuple
        (end, path, length)

    path contiene todos los nodos originales
    recorridos entre start y end.
    """

    path = [
        start,
        neighbour,
    ]

    previous = start
    current = neighbour

    length = graph.edges[
        previous,
        current,
    ]["length"]

    while current not in anchors:

        candidates = [
            node
            for node in graph.neighbors(current)
            if node != previous
        ]

        # En una cadena de grado 2 debería haber
        # exactamente un siguiente nodo.
        if len(candidates) != 1:
            break

        following = candidates[0]

        length += graph.edges[
            current,
            following,
        ]["length"]

        path.append(
            following
        )

        previous = current
        current = following

    return (
        current,
        path,
        float(length),
    )


# ============================================================
# DEGENERATE COMPONENTS
# ============================================================

def _is_degenerate_component(
    graph,
    component,
    relative_threshold=1e-3,
):
    """
    Determina si una componente debe considerarse
    degenerada.

    Actualmente solo se eliminan componentes que:

    - tienen exactamente 2 nodos;
    - tienen exactamente 1 arista;
    - su longitud es extremadamente pequeña respecto
      a la escala global del modelo.

    Esto evita eliminar componentes pequeñas que puedan
    contener información estructural real.
    """

    if len(component) != 2:
        return False

    subgraph = graph.subgraph(
        component
    )

    if subgraph.number_of_edges() != 1:
        return False

    edge_data = next(
        iter(
            subgraph.edges(
                data=True
            )
        )
    )

    length = float(
        edge_data[2].get(
            "length",
            0.0,
        )
    )

    # --------------------------------------------------------
    # Escala global del modelo.
    # --------------------------------------------------------

    positions = np.asarray(
        [
            graph.nodes[node]["position"]
            for node in graph.nodes()
        ],
        dtype=float,
    )

    if len(positions) == 0:
        return False

    bbox_min = positions.min(
        axis=0
    )

    bbox_max = positions.max(
        axis=0
    )

    model_scale = float(
        np.linalg.norm(
            bbox_max - bbox_min
        )
    )

    if model_scale <= 0.0:
        return False

    relative_length = (
        length / model_scale
    )

    return (
        relative_length
        < relative_threshold
    )


# ============================================================
# SIMPLIFICATION
# ============================================================

def simplify_curve_graph(
    graph,
    degenerate_threshold=1e-3,
):
    """
    Simplifica un curve skeleton.

    Proceso:

    1. Identifica anchors:
       - hojas
       - ramificaciones

    2. Colapsa cadenas de grado 2.

    3. Conserva la longitud geométrica total
       de cada cadena.

    4. Elimina únicamente componentes de 2 nodos
       cuya longitud sea extremadamente pequeña
       respecto a la escala del modelo.

    5. Mantiene el resto de componentes.

    Returns
    -------
    nx.Graph
        Grafo simplificado.
    """

    if graph.number_of_nodes() == 0:
        return nx.Graph()

    # --------------------------------------------------------
    # ANCHORS
    #
    # Todo nodo que NO sea de grado 2.
    #
    # degree 1 -> hoja
    # degree 3+ -> ramificación
    # --------------------------------------------------------

    anchors = {
        node
        for node in graph
        if graph.degree(node) != 2
    }

    simplified = nx.Graph()

    # --------------------------------------------------------
    # COPIAR ANCHORS
    # --------------------------------------------------------

    for node in anchors:

        simplified.add_node(
            node,
            position=graph.nodes[
                node
            ]["position"].copy(),
        )

    # --------------------------------------------------------
    # COMPONENTES SIN ANCHORS
    #
    # Caso especial: ciclos.
    #
    # No esperamos ciclos en nuestro curve skeleton
    # animal, pero mantenemos una representación
    # estable por seguridad.
    # --------------------------------------------------------

    for component in nx.connected_components(
        graph
    ):

        component = set(component)

        if not (
            anchors & component
        ):

            representative = min(
                component
            )

            simplified.add_node(
                representative,
                position=graph.nodes[
                    representative
                ]["position"].copy(),
            )

    # --------------------------------------------------------
    # RECORRER CADENAS
    # --------------------------------------------------------

    visited_edges = set()

    for origin in anchors:

        for neighbour in graph.neighbors(
            origin
        ):

            edge_key = frozenset(
                (
                    origin,
                    neighbour,
                )
            )

            if edge_key in visited_edges:
                continue

            end, path, length = (
                _chain_between(
                    graph,
                    origin,
                    neighbour,
                    anchors,
                )
            )

            # ------------------------------------------------
            # Marcar todas las aristas originales
            # pertenecientes a esta cadena.
            # ------------------------------------------------

            for a, b in zip(
                path[:-1],
                path[1:],
            ):

                visited_edges.add(
                    frozenset(
                        (
                            a,
                            b,
                        )
                    )
                )

            # ------------------------------------------------
            # Evitar auto-aristas.
            # ------------------------------------------------

            if end == origin:
                continue

            simplified.add_edge(
                origin,
                end,
                length=float(length),
                path=path,
            )

    # ========================================================
    # ELIMINACIÓN DE COMPONENTES DEGENERADAS
    # ========================================================

    components = list(
        nx.connected_components(
            simplified
        )
    )

    remove_nodes = set()

    for component in components:

        if _is_degenerate_component(
            simplified,
            component,
            relative_threshold=(
                degenerate_threshold
            ),
        ):

            remove_nodes.update(
                component
            )

    if remove_nodes:

        simplified.remove_nodes_from(
            remove_nodes
        )

    return simplified

def terminal_spatial_features(root):
    """
    Extrae características espaciales de las hojas
    de un Bone Tree.

    Las posiciones se normalizan respecto al centro
    y a la escala global del skeleton.

    Returns
    -------
    dict
        Características espaciales de los terminales.
    """

    # --------------------------------------------------
    # Recoger nodos
    # --------------------------------------------------

    nodes = []
    leaves = []

    stack = [root]

    while stack:

        bone = stack.pop()

        nodes.append(bone)

        if len(bone.children) == 0:
            leaves.append(bone)

        stack.extend(bone.children)

    if not nodes:
        raise ValueError(
            "El skeleton no contiene nodos."
        )

    positions = np.asarray(
        [
            bone.position
            for bone in nodes
        ],
        dtype=float,
    )

    leaf_positions = np.asarray(
        [
            bone.position
            for bone in leaves
        ],
        dtype=float,
    )

    # --------------------------------------------------
    # Centro geométrico
    # --------------------------------------------------

    center = positions.mean(
        axis=0
    )

    centered = positions - center

    # --------------------------------------------------
    # PCA
    # --------------------------------------------------

    covariance = np.cov(
        centered,
        rowvar=False,
    )

    eigenvalues, eigenvectors = np.linalg.eigh(
        covariance
    )

    order = np.argsort(
        eigenvalues
    )[::-1]

    eigenvalues = eigenvalues[
        order
    ]

    eigenvectors = eigenvectors[
        :,
        order
    ]

    # --------------------------------------------------
    # Transformar hojas al sistema PCA
    # --------------------------------------------------

    leaf_centered = (
        leaf_positions - center
    )

    leaf_pca = (
        leaf_centered
        @ eigenvectors
    )

    # --------------------------------------------------
    # Escala global
    # --------------------------------------------------

    scale = np.linalg.norm(
        centered,
        axis=1
    ).max()

    if scale <= 1e-12:
        scale = 1.0

    leaf_normalized = (
        leaf_pca / scale
    )

    return {
        "center": center,
        "scale": float(scale),
        "eigenvalues": eigenvalues,
        "eigenvectors": eigenvectors,
        "leaf_positions": leaf_positions,
        "leaf_normalized": leaf_normalized,
        "leaf_names": [
            getattr(
                bone,
                "name",
                str(bone.node_id),
            )
            for bone in leaves
        ],
    }