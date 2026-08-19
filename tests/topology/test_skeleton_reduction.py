"""
TEST - SKELETON REDUCTION
=========================

Estudia el efecto de la reducción del curve skeleton generado
para los GLB.

Pipeline analizado:

    GLB
      |
      v
    load_glb()
      |
      v
    get_mesh()
      |
      v
    fix_mesh()
      |
      v
    generate_skeleton()
      |
      v
    skeleton_to_graph()
      |
      |   RAW GRAPH
      v
    simplify_curve_graph()
      |
      v
    REDUCED GRAPH

El objetivo NO es hacer matching todavía.

Este test sirve para medir cuánto cambia la estructura del
skeleton al aplicar la reducción existente en topology.curve_graph.

IMPORTANTE
----------
No usamos generate_curve_graph(), porque esa función ya realiza
la reducción internamente.

Queremos comparar explícitamente:

    RAW -> REDUCED

para saber qué información estructural está eliminando
simplify_curve_graph().
"""

from pathlib import Path
import sys
import statistics


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


# ============================================================
# IMPORTS DEL PROYECTO
# ============================================================

from topology.loader import (
    load_glb,
    get_mesh,
)

from topology.preprocess import (
    fix_mesh,
)

from topology.skeletonize import (
    generate_skeleton,
)

from topology.curve_graph import (
    simplify_curve_graph,
    skeleton_to_graph,
)


# ============================================================
# DIRECTORIOS
# ============================================================

GLB_DIR = (
    PROJECT_ROOT
    / "tests"
    / "topology"
    / "glb"
)


# ============================================================
# MODELOS
# ============================================================

GLB_MODELS = [
    "BlackWidow.glb",
    "Crocodile.glb",
    "Deer.glb",
    "DragonFly.glb",
    "Eagle.glb",
    "GreatHornedOwl.glb",
    "GreatWhiteShark.glb",
    "HellenicHound.glb",
    "Horse.glb",
    "IndianElephant.glb",
    "Squid.glb",
    "oso_pardo.glb",
    "oso_polar.glb",
]


# ============================================================
# GRAPH METRICS
# ============================================================

def graph_metrics(graph):
    """
    Calcula métricas estructurales básicas de un graph.

    Returns
    -------
    dict
        nodes
        edges
        leaves
        branches
        degree
        depth
        len_mean
        len_median
    """

    if graph is None:
        return {
            "nodes": 0,
            "edges": 0,
            "leaves": 0,
            "branches": 0,
            "degree": 0,
            "depth": 0,
            "len_mean": 0.0,
            "len_median": 0.0,
        }

    nodes = graph.number_of_nodes()
    edges = graph.number_of_edges()

    # --------------------------------------------------------
    # DEGREES
    # --------------------------------------------------------

    degrees = [
        graph.degree(node)
        for node in graph.nodes()
    ]

    if degrees:
        max_degree = max(degrees)
    else:
        max_degree = 0

    leaves = sum(
        1
        for degree in degrees
        if degree == 1
    )

    branches = sum(
        1
        for degree in degrees
        if degree >= 3
    )

    # --------------------------------------------------------
    # EDGE LENGTHS
    # --------------------------------------------------------

    lengths = []

    for u, v, data in graph.edges(
        data=True
    ):
        length = data.get(
            "length",
            None,
        )

        if length is not None:
            try:
                lengths.append(
                    float(length)
                )
            except (
                TypeError,
                ValueError,
            ):
                pass

    if lengths:
        len_mean = statistics.mean(
            lengths
        )

        len_median = statistics.median(
            lengths
        )
    else:
        len_mean = 0.0
        len_median = 0.0

    # --------------------------------------------------------
    # DEPTH
    # --------------------------------------------------------
    #
    # El graph del skeleton debería ser un árbol.
    #
    # Para evitar asumir que el root es 0,
    # calculamos la máxima distancia entre
    # nodos mediante BFS desde cada hoja.
    #
    # Para estos tamaños de graph es suficiente
    # y nos permite mantener el diagnóstico
    # independiente de la numeración de nodos.
    # --------------------------------------------------------

    depth = 0

    if nodes > 0:

        leaves_nodes = [
            node
            for node in graph.nodes()
            if graph.degree(node) == 1
        ]

        # Si no hay hojas, usamos cualquier nodo.
        if not leaves_nodes:
            leaves_nodes = [
                next(
                    iter(
                        graph.nodes()
                    )
                )
            ]

        # En un árbol, el diámetro corresponde
        # a la distancia máxima entre hojas.
        #
        # No necesitamos recorrer todos los pares.
        # Dos BFS son suficientes para obtener
        # el diámetro de un árbol.
        start = leaves_nodes[0]

        distances = _bfs_distances(
            graph,
            start,
        )

        if distances:
            farthest = max(
                distances,
                key=distances.get,
            )

            distances = _bfs_distances(
                graph,
                farthest,
            )

            if distances:
                depth = max(
                    distances.values()
                )

    return {
        "nodes": nodes,
        "edges": edges,
        "leaves": leaves,
        "branches": branches,
        "degree": max_degree,
        "depth": depth,
        "len_mean": len_mean,
        "len_median": len_median,
    }


# ============================================================
# BFS
# ============================================================

def _bfs_distances(
    graph,
    start,
):
    """
    Distancias topológicas desde start.
    """

    distances = {
        start: 0
    }

    queue = [
        start
    ]

    index = 0

    while index < len(queue):

        node = queue[index]

        index += 1

        current_distance = (
            distances[node]
        )

        for neighbour in graph.neighbors(
            node
        ):

            if neighbour in distances:
                continue

            distances[neighbour] = (
                current_distance + 1
            )

            queue.append(
                neighbour
            )

    return distances


# ============================================================
# LOAD + BUILD RAW GRAPH
# ============================================================

def build_raw_graph(
    path,
):
    """
    Construye el graph RAW directamente desde
    generate_skeleton() + skeleton_to_graph().

    No utiliza generate_curve_graph(),
    porque esta última ya simplifica.
    """

    scene = load_glb(
        path
    )

    mesh = get_mesh(
        scene
    )

    if mesh is None:
        raise RuntimeError(
            "get_mesh() devolvió None"
        )

    mesh = fix_mesh(
        mesh
    )

    skeleton = generate_skeleton(
        mesh,
        sampling_dist=0.1,
    )

    graph = skeleton_to_graph(
        skeleton
    )

    return graph


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "=" * 100
    )
    print(
        "SKELETON REDUCTION EXPERIMENT"
    )
    print(
        "=" * 100
    )

    print()
    print(
        f"PROJECT ROOT: {PROJECT_ROOT}"
    )

    print(
        f"GLB DIR:     {GLB_DIR}"
    )

    print()
    print(
        "=" * 100
    )
    print(
        "RAW -> REDUCED"
    )
    print(
        "=" * 100
    )

    print()

    header = (
        f"{'MODEL':<25}"
        f"{'RAW N':>8}"
        f"{'RED N':>8}"
        f"{'Δ N':>8}"
        f"{'RAW E':>8}"
        f"{'RED E':>8}"
        f"{'RAW L':>8}"
        f"{'RED L':>8}"
        f"{'RAW B':>8}"
        f"{'RED B':>8}"
        f"{'RAW D':>8}"
        f"{'RED D':>8}"
    )

    print(header)

    print(
        "-" * len(header)
    )

    results = []

    for model_name in GLB_MODELS:

        path = (
            GLB_DIR
            / model_name
        )

        print(
            f"  processing {model_name}..."
        )

        if not path.exists():

            print(
                f"  [ERROR] File not found: {path}"
            )

            continue

        try:

            # ------------------------------------------------
            # RAW
            # ------------------------------------------------

            raw_graph = build_raw_graph(
                path
            )

            raw_metrics = graph_metrics(
                raw_graph
            )

            # ------------------------------------------------
            # REDUCED
            # ------------------------------------------------

            reduced_graph = (
                simplify_curve_graph(
                    raw_graph
                )
            )

            reduced_metrics = graph_metrics(
                reduced_graph
            )

            # ------------------------------------------------
            # DIFFERENCES
            # ------------------------------------------------

            delta_nodes = (
                raw_metrics["nodes"]
                - reduced_metrics["nodes"]
            )

            delta_edges = (
                raw_metrics["edges"]
                - reduced_metrics["edges"]
            )

            # ------------------------------------------------
            # PRINT
            # ------------------------------------------------

            print(
                f"{model_name:<25}"
                f"{raw_metrics['nodes']:>8}"
                f"{reduced_metrics['nodes']:>8}"
                f"{delta_nodes:>8}"
                f"{raw_metrics['edges']:>8}"
                f"{reduced_metrics['edges']:>8}"
                f"{raw_metrics['leaves']:>8}"
                f"{reduced_metrics['leaves']:>8}"
                f"{raw_metrics['branches']:>8}"
                f"{reduced_metrics['branches']:>8}"
                f"{raw_metrics['depth']:>8}"
                f"{reduced_metrics['depth']:>8}"
            )

            results.append(
                (
                    model_name,
                    raw_metrics,
                    reduced_metrics,
                )
            )

        except Exception as exc:

            print(
                f"  [ERROR] {model_name}: "
                f"{type(exc).__name__}: {exc}"
            )

    # ========================================================
    # DETAILED REDUCTION
    # ========================================================

    print()
    print(
        "=" * 100
    )
    print(
        "REDUCTION DETAILS"
    )
    print(
        "=" * 100
    )

    print()

    detail_header = (
        f"{'MODEL':<25}"
        f"{'N REDUCED':>12}"
        f"{'% N REMOVED':>14}"
        f"{'E REDUCED':>12}"
        f"{'% E REMOVED':>14}"
        f"{'LEAVES':>10}"
        f"{'BRANCH':>10}"
    )

    print(
        detail_header
    )

    print(
        "-" * len(detail_header)
    )

    for (
        model_name,
        raw,
        reduced,
    ) in results:

        raw_nodes = raw["nodes"]
        raw_edges = raw["edges"]

        reduced_nodes = reduced["nodes"]
        reduced_edges = reduced["edges"]

        if raw_nodes:
            nodes_removed_pct = (
                100.0
                * (
                    raw_nodes
                    - reduced_nodes
                )
                / raw_nodes
            )
        else:
            nodes_removed_pct = 0.0

        if raw_edges:
            edges_removed_pct = (
                100.0
                * (
                    raw_edges
                    - reduced_edges
                )
                / raw_edges
            )
        else:
            edges_removed_pct = 0.0

        print(
            f"{model_name:<25}"
            f"{reduced_nodes:>12}"
            f"{nodes_removed_pct:>13.2f}%"
            f"{reduced_edges:>12}"
            f"{edges_removed_pct:>13.2f}%"
            f"{reduced['leaves']:>10}"
            f"{reduced['branches']:>10}"
        )

    # ========================================================
    # LENGTH ANALYSIS
    # ========================================================

    print()
    print(
        "=" * 100
    )
    print(
        "EDGE LENGTH ANALYSIS"
    )
    print(
        "=" * 100
    )

    print()

    length_header = (
        f"{'MODEL':<25}"
        f"{'RAW MEAN':>14}"
        f"{'RED MEAN':>14}"
        f"{'RAW MED':>14}"
        f"{'RED MED':>14}"
    )

    print(
        length_header
    )

    print(
        "-" * len(length_header)
    )

    for (
        model_name,
        raw,
        reduced,
    ) in results:

        print(
            f"{model_name:<25}"
            f"{raw['len_mean']:>14.6f}"
            f"{reduced['len_mean']:>14.6f}"
            f"{raw['len_median']:>14.6f}"
            f"{reduced['len_median']:>14.6f}"
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print(
        "=" * 100
    )
    print(
        "SUMMARY"
    )
    print(
        "=" * 100
    )

    print()

    if not results:

        print(
            "No se han podido procesar modelos."
        )

        return

    total_raw_nodes = sum(
        raw["nodes"]
        for _, raw, _ in results
    )

    total_reduced_nodes = sum(
        reduced["nodes"]
        for _, _, reduced in results
    )

    total_raw_edges = sum(
        raw["edges"]
        for _, raw, _ in results
    )

    total_reduced_edges = sum(
        reduced["edges"]
        for _, _, reduced in results
    )

    if total_raw_nodes:

        total_nodes_removed_pct = (
            100.0
            * (
                total_raw_nodes
                - total_reduced_nodes
            )
            / total_raw_nodes
        )

    else:

        total_nodes_removed_pct = 0.0

    if total_raw_edges:

        total_edges_removed_pct = (
            100.0
            * (
                total_raw_edges
                - total_reduced_edges
            )
            / total_raw_edges
        )

    else:

        total_edges_removed_pct = 0.0

    print(
        f"MODELS PROCESSED : {len(results)}"
    )

    print(
        f"RAW NODES        : {total_raw_nodes}"
    )

    print(
        f"REDUCED NODES    : {total_reduced_nodes}"
    )

    print(
        f"NODES REMOVED    : "
        f"{total_nodes_removed_pct:.2f}%"
    )

    print(
        f"RAW EDGES        : {total_raw_edges}"
    )

    print(
        f"REDUCED EDGES    : {total_reduced_edges}"
    )

    print(
        f"EDGES REMOVED    : "
        f"{total_edges_removed_pct:.2f}%"
    )

    print()
    print(
        "NOTA:"
    )

    print(
        "  Este test no realiza matching."
    )

    print(
        "  Su objetivo es determinar cuánto"
    )

    print(
        "  reduce realmente simplify_curve_graph()"
    )

    print(
        "  y qué características estructurales"
    )

    print(
        "  permanecen después de la reducción."
    )

    print()
    print(
        "=" * 100
    )
    print(
        "DONE"
    )
    print(
        "=" * 100
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()