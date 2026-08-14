"""
morphology.py

Extracción de características morfológicas desde un grafo
estructural 3D.

Responsabilidad:

- Identificar una región corporal aproximada.
- Identificar ramas estructurales que salen de esa región.
- Medir dichas ramas.
- Describir su complejidad y distribución espacial.
- Generar una MorphologySignature.

No hace:

- No carga GLB.
- No carga FBX.
- No realiza matching.
- No calcula el score final.

La detección es deliberadamente exploratoria:
primero queremos observar la estructura obtenida,
antes de imponer una interpretación anatómica.
"""

from dataclasses import dataclass

import networkx as nx
import numpy as np


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class LimbFeature:
    """
    Características de una rama candidata a extremidad.
    """

    attachment_node: int

    terminal_nodes: list[int]

    path_nodes: list[int]

    length: float

    direction: np.ndarray

    radial_distance: float

    # Medidas normalizadas respecto a la escala global del modelo.
    length_normalized: float = 0.0
    radial_distance_normalized: float = 0.0

    # Complejidad interna de la rama candidata.
    terminal_count: int = 0

    branch_count: int = 0

    branch_depth: int = 0


@dataclass
class MorphologySignature:
    """
    Firma morfológica.

    body_nodes representa una región, no un único nodo.
    """

    source: str = "graph"

    body_nodes: list[int] | None = None

    # Número de candidatos que salen de la región corporal.
    # No debe interpretarse automáticamente como número de patas.
    limb_count: int = 0

    # Número total de terminales encontrados en los candidatos.
    terminal_count: int = 0

    # Complejidad media de ramificación de los candidatos.
    branching_complexity: float = 0.0

    # Profundidad media de ramificación de los candidatos.
    mean_branch_depth: float = 0.0

    # Tamaño relativo de la región corporal.
    body_ratio: float = 0.0

    # Dispersión angular de las direcciones de los candidatos.
    angular_spread: float = 0.0

    limbs: list[LimbFeature] | None = None

    symmetry_score: float = 0.0

    radial_distribution: float = 0.0

    mean_limb_length: float = 0.0

    limb_length_std: float = 0.0

    limb_length_min: float = 0.0

    limb_length_max: float = 0.0


# ============================================================
# POSITION HELPERS
# ============================================================

def _positions(graph):
    """
    Devuelve las posiciones 3D de todos los nodos.
    """

    result = {}

    for node, data in graph.nodes(
        data=True
    ):

        position = data.get(
            "position"
        )

        if position is None:

            raise ValueError(
                f"El nodo {node} "
                "no contiene 'position'."
            )

        result[node] = np.asarray(
            position,
            dtype=float,
        )

    return result


# ============================================================
# MODEL SCALE
# ============================================================

def _model_scale(graph):
    """
    Diagonal del bounding box del grafo.
    """

    positions = _positions(
        graph
    )

    if not positions:
        return 0.0

    values = np.asarray(
        list(
            positions.values()
        ),
        dtype=float,
    )

    minimum = values.min(
        axis=0
    )

    maximum = values.max(
        axis=0
    )

    return float(
        np.linalg.norm(
            maximum - minimum
        )
    )


# ============================================================
# MODEL CENTER
# ============================================================

def _model_center(graph):
    """
    Centro geométrico de los nodos.
    """

    positions = _positions(
        graph
    )

    if not positions:
        return np.zeros(3)

    return np.mean(
        np.asarray(
            list(
                positions.values()
            ),
            dtype=float,
        ),
        axis=0,
    )


# ============================================================
# STRUCTURAL NODES
# ============================================================
def _structural_nodes(graph):
    """
    Devuelve únicamente nodos de ramificación.

    Las hojas no forman parte de la región corporal.
    Las hojas se utilizarán posteriormente como terminales
    de las extremidades.
    """

    return [
        node
        for node in graph.nodes()
        if graph.degree(node) >= 3
    ]
# ============================================================
# NODE IMPORTANCE
# ============================================================

def _node_importance(
    graph,
    node,
):
    """
    Calcula una medida de importancia estructural.

    Combina:

    - betweenness centrality
    - grado
    - posición respecto al centro

    No es todavía un score anatómico.
    """

    betweenness = nx.betweenness_centrality(
        graph,
        normalized=True,
    )

    degree = graph.degree(
        node
    )

    maximum_degree = max(
        dict(
            graph.degree()
        ).values(),
        default=1,
    )

    degree_score = (
        degree
        / maximum_degree
    )

    center = _model_center(
        graph
    )

    position = np.asarray(
        graph.nodes[
            node
        ]["position"],
        dtype=float,
    )

    scale = _model_scale(
        graph
    )

    if scale > 0.0:

        center_distance = (
            np.linalg.norm(
                position - center
            )
            / scale
        )

    else:

        center_distance = 0.0

    central_position = float(
        np.exp(
            -3.0
            * center_distance
        )
    )

    return float(
        0.50 * betweenness[node]
        + 0.30 * degree_score
        + 0.20 * central_position
    )


# ============================================================
# BODY REGION
# ============================================================

def find_body_core_region(
    graph,
):
    """
    Busca una región corporal aproximada.

    IMPORTANTE:

    No intenta encontrar "el cuerpo" anatómicamente.
    Genera una región estructural compacta alrededor
    de los nodos más importantes.

    La región se construye partiendo del nodo con mayor
    importancia y añadiendo nodos estructurales cercanos
    mientras la incorporación siga siendo local.

    Esta primera versión está pensada para inspección,
    no para producir un resultado perfecto.
    """

    if graph.number_of_nodes() == 0:
        return []

    structural = _structural_nodes(
        graph
    )

    if not structural:
        return []

    importance = {
        node: _node_importance(
            graph,
            node,
        )
        for node in structural
    }

    seed = max(
        importance,
        key=importance.get,
    )

    # --------------------------------------------------------
    # Distancias topológicas desde el seed.
    # --------------------------------------------------------

    distances = nx.single_source_shortest_path_length(
        graph,
        seed,
    )

    # --------------------------------------------------------
    # Región inicial.
    #
    # En el grafo simplificado queremos una región pequeña
    # pero que pueda contener varias ramificaciones.
    # --------------------------------------------------------

    region = {
        seed
    }

    candidates = sorted(
        (
            (
                distance,
                -importance.get(
                    node,
                    0.0,
                ),
                node,
            )
            for node, distance
            in distances.items()
            if (
                node != seed
                and node in structural
            )
        ),
        key=lambda item: (
            item[0],
            item[1],
        ),
    )

    # --------------------------------------------------------
    # Añadimos nodos estructurales cercanos.
    #
    # No usamos un número fijo de nodos como resultado
    # anatómico. El límite es únicamente para mantener
    # la región local.
    # --------------------------------------------------------

    for distance, _, node in candidates:

        if distance > 2:
            break

        region.add(
            node
        )

    return sorted(
        region
    )


# ============================================================
# REGION COMPONENTS
# ============================================================

def _region_boundary_edges(
    graph,
    region,
):
    """
    Encuentra las aristas que salen de la región corporal.
    """

    region = set(
        region
    )

    result = []

    for node in region:

        for neighbour in graph.neighbors(
            node
        ):

            if neighbour not in region:

                result.append(
                    (
                        node,
                        neighbour,
                    )
                )

    return result


# ============================================================
# TRACE BRANCH
# ============================================================

def _trace_branch(
    graph,
    attachment,
    first_node,
    body_region,
):
    """
    Sigue una rama desde el cuerpo hasta sus terminales.

    Si aparecen bifurcaciones, se conservan todos los
    terminales pertenecientes a esa rama.
    """

    body_region = set(
        body_region
    )

    results = []

    first_position = np.asarray(
        graph.nodes[
            first_node
        ]["position"],
        dtype=float,
    )

    attachment_position = np.asarray(
        graph.nodes[
            attachment
        ]["position"],
        dtype=float,
    )

    initial_length = float(
        np.linalg.norm(
            first_position
            - attachment_position
        )
    )

    stack = [
        (
            first_node,
            attachment,
            [attachment, first_node],
            initial_length,
        )
    ]

    while stack:

        current, previous, path, length = (
            stack.pop()
        )

        neighbours = [
            node
            for node in graph.neighbors(
                current
            )
            if node != previous
            and node not in body_region
        ]

        # ----------------------------------------------------
        # Terminal
        # ----------------------------------------------------

        if not neighbours:

            results.append(
                (
                    current,
                    path,
                    length,
                )
            )

            continue

        # ----------------------------------------------------
        # Continue / branch
        # ----------------------------------------------------

        current_position = np.asarray(
            graph.nodes[
                current
            ]["position"],
            dtype=float,
        )

        for neighbour in neighbours:

            neighbour_position = np.asarray(
                graph.nodes[
                    neighbour
                ]["position"],
                dtype=float,
            )

            edge_length = float(
                np.linalg.norm(
                    neighbour_position
                    - current_position
                )
            )

            stack.append(
                (
                    neighbour,
                    current,
                    path + [neighbour],
                    length + edge_length,
                )
            )

    return results


# ============================================================
# LIMB CANDIDATES
# ============================================================

def find_limb_candidates(
    graph,
    body_region=None,
):
    """
    Extrae ramas que salen de la región corporal.

    Cada arista frontera produce inicialmente un candidato.

    TODAVÍA no afirmamos que cada candidato sea una
    extremidad anatómica.
    """

    if graph.number_of_nodes() == 0:
        return []

    if body_region is None:

        body_region = (
            find_body_core_region(
                graph
            )
        )

    if not body_region:
        return []

    boundary = _region_boundary_edges(
        graph,
        body_region,
    )

    limbs = []

    model_scale = _model_scale(graph)

    for attachment, first_node in boundary:

        paths = _trace_branch(
            graph,
            attachment,
            first_node,
            body_region,
        )

        if not paths:
            continue

        terminal_nodes = [
            terminal
            for terminal, _, _
            in paths
        ]

        # ----------------------------------------------------
        # Características estructurales del candidato.
        #
        # Los caminos devueltos por _trace_branch contienen
        # toda la información necesaria para saber si esta
        # rama es simple o internamente ramificada.
        # ----------------------------------------------------

        terminal_count = len(
            terminal_nodes
        )

        visited_nodes = set()

        for _, path, _ in paths:

            visited_nodes.update(
                path
            )

        subgraph = graph.subgraph(
            visited_nodes
        )

        branch_count = sum(
            1
            for node in subgraph.nodes()
            if subgraph.degree(node) >= 3
        )

        branch_depth = 0

        for _, path, _ in paths:

            # path incluye attachment como primer nodo.
            branch_depth = max(
                branch_depth,
                max(
                    len(path) - 1,
                    0,
                ),
            )

        longest = max(
            paths,
            key=lambda item: item[2],
        )

        terminal, path, length = (
            longest
        )

        attachment_position = np.asarray(
            graph.nodes[
                attachment
            ]["position"],
            dtype=float,
        )

        terminal_position = np.asarray(
            graph.nodes[
                terminal
            ]["position"],
            dtype=float,
        )

        vector = (
            terminal_position
            - attachment_position
        )

        distance = float(
            np.linalg.norm(
                vector
            )
        )

        if distance > 0.0:

            direction = (
                vector
                / distance
            )

        else:

            direction = np.zeros(3)

        limbs.append(
            LimbFeature(
                attachment_node=attachment,
                terminal_nodes=terminal_nodes,
                path_nodes=path,
                length=float(length),
                direction=direction,
                radial_distance=distance,
                length_normalized=(
                    float(length) / model_scale
                    if model_scale > 0.0
                    else 0.0
                ),
                radial_distance_normalized=(
                    distance / model_scale
                    if model_scale > 0.0
                    else 0.0
                ),
                terminal_count=terminal_count,
                branch_count=branch_count,
                branch_depth=branch_depth,
            )
        )

    return limbs


# ============================================================
# SYMMETRY
# ============================================================

def _calculate_symmetry(
    limbs,
):
    """
    Estima simetría direccional entre candidatos.

    Busca direcciones aproximadamente opuestas.
    """

    if len(limbs) < 2:
        return 0.0

    directions = [
        limb.direction
        for limb in limbs
    ]

    used = set()
    scores = []

    for i, direction_a in enumerate(
        directions
    ):

        if i in used:
            continue

        best_score = None
        best_j = None

        for j in range(
            i + 1,
            len(directions),
        ):

            if j in used:
                continue

            direction_b = directions[j]

            similarity = float(
                np.dot(
                    direction_a,
                    -direction_b,
                )
            )

            similarity = float(
                np.clip(
                    similarity,
                    -1.0,
                    1.0,
                )
            )

            if (
                best_score is None
                or similarity > best_score
            ):

                best_score = similarity
                best_j = j

        if best_score is not None:

            scores.append(
                max(
                    0.0,
                    best_score,
                )
            )

            used.add(i)
            used.add(best_j)

    if not scores:
        return 0.0

    return float(
        np.mean(scores)
    )


# ============================================================
# RADIAL DISTRIBUTION
# ============================================================

def _calculate_radial_distribution(
    limbs,
):
    """
    Mide la distribución espacial de las direcciones.

    No interpreta todavía si la distribución es bilateral,
    radial o anatómica.
    """

    if len(limbs) < 2:
        return 0.0

    directions = np.asarray(
        [
            limb.direction
            for limb in limbs
        ],
        dtype=float,
    )

    values = []

    for i in range(
        len(directions)
    ):

        for j in range(
            i + 1,
            len(directions),
        ):

            dot = abs(
                float(
                    np.dot(
                        directions[i],
                        directions[j],
                    )
                )
            )

            values.append(
                dot
            )

    if not values:
        return 0.0

    return float(
        np.clip(
            1.0
            - np.mean(values),
            0.0,
            1.0,
        )
    )




# ============================================================
# BODY RATIO
# ============================================================

def _calculate_body_ratio(
    graph,
    body_region,
):
    """
    Tamaño relativo de la región corporal.

    Se calcula como la diagonal del bounding box de la región
    corporal dividida por la diagonal del bounding box global.

    No pretende ser una medida anatómica exacta; describe cuánto
    espacio ocupa la región corporal respecto al modelo completo.
    """

    if not body_region:
        return 0.0

    scale = _model_scale(graph)

    if scale <= 0.0:
        return 0.0

    positions = _positions(graph)

    values = np.asarray(
        [
            positions[node]
            for node in body_region
            if node in positions
        ],
        dtype=float,
    )

    if len(values) == 0:
        return 0.0

    body_extent = float(
        np.linalg.norm(
            values.max(axis=0)
            - values.min(axis=0)
        )
    )

    return float(
        np.clip(
            body_extent / scale,
            0.0,
            1.0,
        )
    )


# ============================================================
# ANGULAR SPREAD
# ============================================================

def _calculate_angular_spread(
    limbs,
):
    """
    Mide cuánto se separan angularmente las direcciones
    de los candidatos.

    0.0 -> direcciones muy alineadas.
    1.0 -> direcciones muy separadas en el espacio.

    Se usa el ángulo entre direcciones, sin distinguir entre
    dos sentidos opuestos, porque aquí interesa la organización
    espacial del conjunto de apéndices.
    """

    if len(limbs) < 2:
        return 0.0

    directions = [
        np.asarray(
            limb.direction,
            dtype=float,
        )
        for limb in limbs
    ]

    values = []

    for i in range(
        len(directions)
    ):

        for j in range(
            i + 1,
            len(directions),
        ):

            a = directions[i]
            b = directions[j]

            norm_a = float(
                np.linalg.norm(a)
            )

            norm_b = float(
                np.linalg.norm(b)
            )

            if norm_a <= 0.0 or norm_b <= 0.0:
                continue

            cosine = abs(
                float(
                    np.dot(
                        a / norm_a,
                        b / norm_b,
                    )
                )
            )

            cosine = float(
                np.clip(
                    cosine,
                    -1.0,
                    1.0,
                )
            )

            angle = float(
                np.arccos(cosine)
            )

            values.append(
                angle / (np.pi / 2.0)
            )

    if not values:
        return 0.0

    return float(
        np.clip(
            np.mean(values),
            0.0,
            1.0,
        )
    )


# ============================================================
# BRANCHING COMPLEXITY
# ============================================================

def _calculate_branching_complexity(
    limbs,
):
    """
    Complejidad media de las ramas candidatas.

    Combina el número de puntos de ramificación y la cantidad
    de terminales. Se normaliza por el número de candidatos para
    que el valor no dependa directamente del tamaño del grafo.
    """

    if not limbs:
        return 0.0

    values = []

    for limb in limbs:

        terminals = max(
            limb.terminal_count,
            1,
        )

        branches = max(
            limb.branch_count,
            0,
        )

        complexity = (
            branches
            + max(terminals - 1, 0)
        )

        values.append(
            float(complexity)
        )

    # La función 1-exp(-x) evita que un candidato con muchas
    # ramificaciones domine completamente la firma.
    normalized = [
        1.0 - np.exp(-value)
        for value in values
    ]

    return float(
        np.clip(
            np.mean(normalized),
            0.0,
            1.0,
        )
    )


# ============================================================
# SIGNATURE
# ============================================================

def build_morphology_signature(
    graph,
    source="graph",
):
    """
    Construye una MorphologySignature.
    """

    if graph is None:

        return MorphologySignature(
            source=source
        )

    if graph.number_of_nodes() == 0:

        return MorphologySignature(
            source=source
        )

    body_region = (
        find_body_core_region(
            graph
        )
    )

    limbs = find_limb_candidates(
        graph,
        body_region=body_region,
    )

    lengths = [
        limb.length
        for limb in limbs
    ]

    terminal_count = sum(
        limb.terminal_count
        for limb in limbs
    )

    mean_branch_depth = float(
        np.mean(
            [
                limb.branch_depth
                for limb in limbs
            ]
        )
    ) if limbs else 0.0

    if lengths:

        mean_length = float(
            np.mean(
                lengths
            )
        )

        std_length = float(
            np.std(
                lengths
            )
        )

        min_length = float(
            np.min(
                lengths
            )
        )

        max_length = float(
            np.max(
                lengths
            )
        )

    else:

        mean_length = 0.0
        std_length = 0.0
        min_length = 0.0
        max_length = 0.0

    return MorphologySignature(
        source=source,
        body_nodes=body_region,
        limb_count=len(limbs),
        terminal_count=terminal_count,
        branching_complexity=(
            _calculate_branching_complexity(
                limbs
            )
        ),
        mean_branch_depth=mean_branch_depth,
        body_ratio=_calculate_body_ratio(
            graph,
            body_region,
        ),
        angular_spread=_calculate_angular_spread(
            limbs
        ),
        limbs=limbs,
        symmetry_score=_calculate_symmetry(
            limbs
        ),
        radial_distribution=(
            _calculate_radial_distribution(
                limbs
            )
        ),
        mean_limb_length=mean_length,
        limb_length_std=std_length,
        limb_length_min=min_length,
        limb_length_max=max_length,
    )
# ============================================================
# MORPHOLOGY COMPARISON
# ============================================================

def _similarity_ratio(a, b):
    """
    Similitud entre dos valores positivos.

    1.0 = idénticos
    0.0 = completamente diferentes
    """
    a = float(a)
    b = float(b)

    denominator = max(
        abs(a),
        abs(b),
        1e-8,
    )

    return float(
        np.clip(
            1.0
            - abs(a - b) / denominator,
            0.0,
            1.0,
        )
    )


def _distribution_similarity(
    values_a,
    values_b,
):
    """
    Compara dos distribuciones mediante:

    - media
    - desviación
    - mínimo
    - máximo

    No exige que tengan el mismo número de elementos.
    """

    if not values_a or not values_b:
        return 0.0

    a = np.asarray(
        values_a,
        dtype=float,
    )

    b = np.asarray(
        values_b,
        dtype=float,
    )

    mean_score = _similarity_ratio(
        np.mean(a),
        np.mean(b),
    )

    std_score = _similarity_ratio(
        np.std(a),
        np.std(b),
    )

    min_score = _similarity_ratio(
        np.min(a),
        np.min(b),
    )

    max_score = _similarity_ratio(
        np.max(a),
        np.max(b),
    )

    return float(
        np.mean(
            [
                mean_score,
                std_score,
                min_score,
                max_score,
            ]
        )
    )


def _limb_count_similarity(
    count_a,
    count_b,
):
    """
    Compara número de candidatos morfológicos.

    No exige igualdad exacta.

    Ejemplo:

        4 vs 4 -> 1.00
        4 vs 5 -> 0.80
        4 vs 6 -> 0.67
        4 vs 8 -> 0.50
    """

    a = int(count_a)
    b = int(count_b)

    if a == 0 and b == 0:
        return 1.0

    if a == 0 or b == 0:
        return 0.0

    return float(
        min(a, b)
        / max(a, b)
    )


def compare_morphology(
    signature_a,
    signature_b,
):
    """
    Compara dos MorphologySignature.

    Devuelve un score de 0.0 a 1.0
    junto con el desglose de cada componente.

    IMPORTANTE:

    No intenta hacer coincidir nodos.

    No intenta hacer coincidir hojas.

    No intenta hacer coincidir huesos.

    Compara únicamente características
    morfológicas de alto nivel.
    """

    if signature_a is None:
        raise ValueError(
            "signature_a no puede ser None."
        )

    if signature_b is None:
        raise ValueError(
            "signature_b no puede ser None."
        )

    # --------------------------------------------------------
    # 1. CANDIDATE / LIMB COUNT
    # --------------------------------------------------------

    count_score = _limb_count_similarity(
        signature_a.limb_count,
        signature_b.limb_count,
    )

    # --------------------------------------------------------
    # 2. SYMMETRY
    # --------------------------------------------------------

    symmetry_score = (
        1.0
        - abs(
            float(
                signature_a.symmetry_score
            )
            -
            float(
                signature_b.symmetry_score
            )
        )
    )

    symmetry_score = float(
        np.clip(
            symmetry_score,
            0.0,
            1.0,
        )
    )

    # --------------------------------------------------------
    # 3. RADIAL DISTRIBUTION
    # --------------------------------------------------------

    radial_score = (
        1.0
        - abs(
            float(
                signature_a.radial_distribution
            )
            -
            float(
                signature_b.radial_distribution
            )
        )
    )

    radial_score = float(
        np.clip(
            radial_score,
            0.0,
            1.0,
        )
    )

    # --------------------------------------------------------
    # 4. ANGULAR SPREAD
    #
    # Puede no existir en versiones antiguas.
    # --------------------------------------------------------

    angular_a = getattr(
        signature_a,
        "angular_spread",
        None,
    )

    angular_b = getattr(
        signature_b,
        "angular_spread",
        None,
    )

    if (
        angular_a is not None
        and angular_b is not None
    ):

        angular_score = (
            1.0
            - abs(
                float(angular_a)
                -
                float(angular_b)
            )
        )

        angular_score = float(
            np.clip(
                angular_score,
                0.0,
                1.0,
            )
        )

    else:

        angular_score = 0.0

    # --------------------------------------------------------
    # 5. LIMB LENGTH DISTRIBUTION
    # --------------------------------------------------------

    lengths_a = [
        getattr(limb, "length_normalized", limb.length)
        for limb in (
            signature_a.limbs or []
        )
    ]

    lengths_b = [
        getattr(limb, "length_normalized", limb.length)
        for limb in (
            signature_b.limbs or []
        )
    ]

    length_score = _distribution_similarity(
        lengths_a,
        lengths_b,
    )

    # --------------------------------------------------------
    # 6. BRANCHING
    # --------------------------------------------------------

    branching_a = getattr(
        signature_a,
        "branching_complexity",
        None,
    )

    branching_b = getattr(
        signature_b,
        "branching_complexity",
        None,
    )

    if (
        branching_a is not None
        and branching_b is not None
    ):

        branching_score = (
            1.0
            - abs(
                float(branching_a)
                -
                float(branching_b)
            )
        )

        branching_score = float(
            np.clip(
                branching_score,
                0.0,
                1.0,
            )
        )

    else:

        branching_score = 0.0

    # --------------------------------------------------------
    # 7. BRANCH DEPTH
    # --------------------------------------------------------

    depth_a = getattr(
        signature_a,
        "mean_branch_depth",
        None,
    )

    depth_b = getattr(
        signature_b,
        "mean_branch_depth",
        None,
    )

    if (
        depth_a is not None
        and depth_b is not None
    ):

        depth_score = _similarity_ratio(
            depth_a,
            depth_b,
        )

    else:

        depth_score = 0.0

    # --------------------------------------------------------
    # AVAILABLE COMPONENTS
    #
    # No penalizamos una métrica que todavía no exista.
    # Redistribuimos su peso entre las métricas disponibles.
    # --------------------------------------------------------

    components = {
        "limb_count": (
            count_score,
            0.25,
        ),
        "symmetry": (
            symmetry_score,
            0.15,
        ),
        "radial_distribution": (
            radial_score,
            0.15,
        ),
        "angular_spread": (
            angular_score,
            0.15,
        ),
        "limb_length": (
            length_score,
            0.15,
        ),
        "branching": (
            branching_score,
            0.10,
        ),
        "branch_depth": (
            depth_score,
            0.05,
        ),
    }

    active = {
        name: (
            score,
            weight,
        )
        for name, (
            score,
            weight,
        ) in components.items()
        if not (
            name in (
                "angular_spread",
                "branching",
                "branch_depth",
            )
            and score == 0.0
        )
    }

    total_weight = sum(
        weight
        for _, weight in active.values()
    )

    if total_weight <= 0.0:
        total_score = 0.0

    else:
        total_score = (
            sum(
                score * weight
                for score, weight
                in active.values()
            )
            / total_weight
        )

    return {
        "score": float(
            np.clip(
                total_score,
                0.0,
                1.0,
            )
        ),
        "components": {
            name: float(score)
            for name, (
                score,
                _,
            ) in components.items()
        },
        "weights": {
            name: float(weight)
            for name, (
                _,
                weight,
            ) in components.items()
        },
        "active_components": list(
            active.keys()
        ),
    }
# ============================================================
# FBX BONE TREE -> MORPHOLOGY SIGNATURE
# ============================================================

def _bone_tree_to_graph(root):
    """
    Convierte un Bone Tree en un NetworkX graph compatible
    con build_morphology_signature().

    Solo utiliza:
        - node_id
        - position
        - parent
        - children

    No utiliza nombres de huesos.
    No realiza matching.
    """

    graph = nx.Graph()

    if root is None:
        return graph

    def walk(bone):

        graph.add_node(
            bone.node_id,
            position=np.asarray(
                bone.position,
                dtype=float,
            ).copy(),
        )

        for child in bone.children:

            graph.add_node(
                child.node_id,
                position=np.asarray(
                    child.position,
                    dtype=float,
                ).copy(),
            )

            graph.add_edge(
                bone.node_id,
                child.node_id,
            )

            walk(child)

    walk(root)

    return graph


def build_morphology_signature_from_bone_tree(
    root,
    source="rig",
):
    """
    Construye una MorphologySignature desde un Bone Tree.

    El resultado utiliza exactamente la misma representación
    que el GLB:

        Bone Tree
            ↓
        NetworkX graph
            ↓
        MorphologySignature

    Esto permite comparar morfología GLB <-> FBX sin exigir
    que tengan el mismo número de nodos.
    """

    graph = _bone_tree_to_graph(
        root
    )

    return build_morphology_signature(
        graph,
        source=source,
    )