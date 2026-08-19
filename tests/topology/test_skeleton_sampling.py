"""
TEST - SKELETON SAMPLING
========================

Estudia el efecto de distintos valores de sampling_dist sobre
el curve skeleton generado mediante TEASAR.

Pipeline:

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
    generate_skeleton(
        sampling_dist=X
    )
      |
      v
    skeleton_to_graph()
      |
      v
    RAW GRAPH

IMPORTANTE
----------

Este test NO realiza:

    - simplify_curve_graph()
    - matching
    - scoring
    - KD-Tree
    - PCA
    - comparación GLB <-> FBX

El objetivo es aislar exclusivamente el efecto de
sampling_dist sobre el skeleton generado por TEASAR.

Los valores probados son:

    0.02
    0.05
    0.10
    0.15
    0.20
    0.30
    0.50
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
# SAMPLING VALUES
# ============================================================

SAMPLING_VALUES = [
    0.02,
    0.05,
    0.10,
    0.15,
    0.20,
    0.30,
    0.50,
]


# ============================================================
# GRAPH METRICS
# ============================================================

def graph_metrics(graph):
    """
    Calcula métricas estructurales básicas del graph.

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
        for node in graph.nodes
    ]

    max_degree = (
        max(degrees)
        if degrees
        else 0
    )

    # --------------------------------------------------------
    # LEAVES
    # --------------------------------------------------------

    leaves = [
        node
        for node in graph.nodes
        if graph.degree(node) == 1
    ]

    leaf_count = len(leaves)

    # --------------------------------------------------------
    # BRANCHES
    # --------------------------------------------------------

    branches = [
        node
        for node in graph.nodes
        if graph.degree(node) >= 3
    ]

    branch_count = len(branches)

    # --------------------------------------------------------
    # EDGE LENGTHS
    # --------------------------------------------------------

    edge_lengths = []

    for u, v, data in graph.edges(
        data=True
    ):

        length = data.get(
            "length",
            None,
        )

        if length is not None:
            try:
                length = float(length)
            except (
                TypeError,
                ValueError,
            ):
                length = None

        if length is not None:
            edge_lengths.append(
                length
            )

    if edge_lengths:

        len_mean = statistics.mean(
            edge_lengths
        )

        len_median = statistics.median(
            edge_lengths
        )

    else:

        len_mean = 0.0
        len_median = 0.0

    # --------------------------------------------------------
    # DEPTH
    # --------------------------------------------------------
    #
    # El graph generado por TEASAR es un Graph no dirigido.
    #
    # Para evitar asumir un root concreto, calculamos la
    # excentricidad máxima dentro del componente principal.
    #
    # Si el graph no es conexo, utilizamos el componente
    # conexo de mayor tamaño.
    # --------------------------------------------------------

    depth = 0

    try:

        import networkx as nx

        if nodes > 0:

            components = list(
                nx.connected_components(
                    graph
                )
            )

            if components:

                largest_component = max(
                    components,
                    key=len,
                )

                subgraph = graph.subgraph(
                    largest_component
                )

                if subgraph.number_of_nodes() > 1:

                    eccentricities = (
                        nx.eccentricity(
                            subgraph
                        )
                    )

                    if eccentricities:
                        depth = max(
                            eccentricities.values()
                        )

    except Exception:

        depth = 0

    return {
        "nodes": nodes,
        "edges": edges,
        "leaves": leaf_count,
        "branches": branch_count,
        "degree": max_degree,
        "depth": depth,
        "len_mean": len_mean,
        "len_median": len_median,
    }


# ============================================================
# BUILD GRAPH
# ============================================================

def build_graph(
    glb_path,
    sampling_dist,
):
    """
    Construye el RAW graph para un GLB utilizando
    el sampling_dist indicado.

    IMPORTANTE:

    No llama a simplify_curve_graph().
    """

    glb = load_glb(
        str(glb_path)
    )

    mesh = get_mesh(
        glb
    )

    mesh = fix_mesh(
        mesh
    )

    skeleton = generate_skeleton(
        mesh,
        sampling_dist=sampling_dist,
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
    print("=" * 100)
    print("SKELETON SAMPLING EXPERIMENT")
    print("=" * 100)

    print()
    print(
        f"PROJECT ROOT: {PROJECT_ROOT}"
    )

    print(
        f"GLB DIR:     {GLB_DIR}"
    )

    print()
    print("=" * 100)
    print("SAMPLING VALUES")
    print("=" * 100)

    print()

    for value in SAMPLING_VALUES:
        print(
            f"  {value:.2f}"
        )

    print()
    print("=" * 100)
    print("BUILDING GRAPHS")
    print("=" * 100)

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    results = {}

    # --------------------------------------------------------
    # PROCESS MODELS
    # --------------------------------------------------------

    for model_name in GLB_MODELS:

        glb_path = (
            GLB_DIR
            / model_name
        )

        if not glb_path.exists():

            print()
            print(
                f"[WARNING] Missing: "
                f"{model_name}"
            )

            continue

        print()
        print(
            f"  processing {model_name}..."
        )

        results[model_name] = {}

        for sampling_dist in SAMPLING_VALUES:

            try:

                graph = build_graph(
                    glb_path,
                    sampling_dist,
                )

                metrics = graph_metrics(
                    graph
                )

                results[
                    model_name
                ][
                    sampling_dist
                ] = metrics

            except Exception as exc:

                print(
                    f"    [ERROR] "
                    f"sampling={sampling_dist:.2f}: "
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

                results[
                    model_name
                ][
                    sampling_dist
                ] = None

    # ========================================================
    # RESULTS BY SAMPLING
    # ========================================================

    print()
    print("=" * 100)
    print("RESULTS BY SAMPLING DIST")
    print("=" * 100)

    for sampling_dist in SAMPLING_VALUES:

        print()
        print(
            f"SAMPLING_DIST = "
            f"{sampling_dist:.2f}"
        )

        print()

        print(
            f"{'MODEL':22s} "
            f"{'NODES':>7s} "
            f"{'EDGES':>7s} "
            f"{'LEAVES':>7s} "
            f"{'BRANCH':>7s} "
            f"{'DEGREE':>7s} "
            f"{'DEPTH':>7s} "
            f"{'LEN_MEAN':>11s} "
            f"{'LEN_MED':>11s}"
        )

        print(
            "-" * 100
        )

        for model_name in GLB_MODELS:

            metrics = (
                results
                .get(model_name, {})
                .get(
                    sampling_dist
                )
            )

            if metrics is None:
                continue

            print(
                f"{model_name:22s} "
                f"{metrics['nodes']:7d} "
                f"{metrics['edges']:7d} "
                f"{metrics['leaves']:7d} "
                f"{metrics['branches']:7d} "
                f"{metrics['degree']:7d} "
                f"{metrics['depth']:7d} "
                f"{metrics['len_mean']:11.6f} "
                f"{metrics['len_median']:11.6f}"
            )

    # ========================================================
    # SUMMARY PER MODEL
    # ========================================================

    print()
    print("=" * 100)
    print("NODE COUNT BY SAMPLING")
    print("=" * 100)

    print()

    header = (
        f"{'MODEL':22s}"
        + "".join(
            f"{value:>10.2f}"
            for value in SAMPLING_VALUES
        )
    )

    print(header)

    print(
        "-" * len(header)
    )

    for model_name in GLB_MODELS:

        row = f"{model_name:22s}"

        for sampling_dist in SAMPLING_VALUES:

            metrics = (
                results
                .get(model_name, {})
                .get(
                    sampling_dist
                )
            )

            if metrics is None:
                row += (
                    f"{'ERROR':>10s}"
                )
            else:
                row += (
                    f"{metrics['nodes']:10d}"
                )

        print(row)

    # ========================================================
    # LEAF COUNT BY SAMPLING
    # ========================================================

    print()
    print("=" * 100)
    print("LEAF COUNT BY SAMPLING")
    print("=" * 100)

    print()

    header = (
        f"{'MODEL':22s}"
        + "".join(
            f"{value:>10.2f}"
            for value in SAMPLING_VALUES
        )
    )

    print(header)

    print(
        "-" * len(header)
    )

    for model_name in GLB_MODELS:

        row = f"{model_name:22s}"

        for sampling_dist in SAMPLING_VALUES:

            metrics = (
                results
                .get(model_name, {})
                .get(
                    sampling_dist
                )
            )

            if metrics is None:
                row += (
                    f"{'ERROR':>10s}"
                )
            else:
                row += (
                    f"{metrics['leaves']:10d}"
                )

        print(row)

    # ========================================================
    # BRANCH COUNT BY SAMPLING
    # ========================================================

    print()
    print("=" * 100)
    print("BRANCH COUNT BY SAMPLING")
    print("=" * 100)

    print()

    header = (
        f"{'MODEL':22s}"
        + "".join(
            f"{value:>10.2f}"
            for value in SAMPLING_VALUES
        )
    )

    print(header)

    print(
        "-" * len(header)
    )

    for model_name in GLB_MODELS:

        row = f"{model_name:22s}"

        for sampling_dist in SAMPLING_VALUES:

            metrics = (
                results
                .get(model_name, {})
                .get(
                    sampling_dist
                )
            )

            if metrics is None:
                row += (
                    f"{'ERROR':>10s}"
                )
            else:
                row += (
                    f"{metrics['branches']:10d}"
                )

        print(row)

    # ========================================================
    # COMPARISON WITH CURRENT VALUE
    # ========================================================

    baseline = 0.10

    print()
    print("=" * 100)
    print(
        f"COMPARISON AGAINST CURRENT "
        f"sampling_dist = {baseline:.2f}"
    )
    print("=" * 100)

    print()

    print(
        f"{'MODEL':22s} "
        f"{'BASE N':>8s} "
        f"{'MIN N':>8s} "
        f"{'MAX N':>8s} "
        f"{'BASE L':>8s} "
        f"{'MIN L':>8s} "
        f"{'MAX L':>8s}"
    )

    print(
        "-" * 75
    )

    for model_name in GLB_MODELS:

        model_results = (
            results.get(
                model_name,
                {}
            )
        )

        valid = [
            (
                sampling,
                metrics
            )
            for sampling, metrics
            in model_results.items()
            if metrics is not None
        ]

        if not valid:
            continue

        baseline_metrics = model_results.get(
            baseline
        )

        if baseline_metrics is None:
            continue

        node_values = [
            metrics["nodes"]
            for _, metrics in valid
        ]

        leaf_values = [
            metrics["leaves"]
            for _, metrics in valid
        ]

        print(
            f"{model_name:22s} "
            f"{baseline_metrics['nodes']:8d} "
            f"{min(node_values):8d} "
            f"{max(node_values):8d} "
            f"{baseline_metrics['leaves']:8d} "
            f"{min(leaf_values):8d} "
            f"{max(leaf_values):8d}"
        )

    # ========================================================
    # END
    # ========================================================

    print()
    print("=" * 100)
    print("DONE")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()