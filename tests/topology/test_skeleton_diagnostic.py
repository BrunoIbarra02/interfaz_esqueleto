"""
test_skeleton_diagnostic.py

Diagnóstico comparativo de los esqueletos generados desde GLB
frente a los esqueletos FBX de referencia.

NO modifica el pipeline.
NO modifica topology/.
Solo analiza y muestra características estructurales.

Flujo GLB:

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
    generate_curve_graph()
      |
      v
    Graph

Flujo FBX:

    FBX
      |
      v
    load_fbx_skeleton()
      |
      v
    Bone Tree

El objetivo es detectar diferencias estructurales entre ambos
representantes antes de seguir modificando el comparador.
"""

from pathlib import Path
import sys
import traceback

import numpy as np


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


# ============================================================
# TOPOLOGY IMPORTS
# ============================================================

from topology.loader import (
    load_glb,
    get_mesh,
)

from topology.preprocess import (
    fix_mesh,
)

from topology.skeletonize import (
    generate_curve_graph,
)

from topology.fbx import (
    load_fbx_skeleton,
)


# ============================================================
# PATHS
# ============================================================

GLB_DIR = (
    PROJECT_ROOT
    / "tests"
    / "topology"
    / "glb"
)

FBX_DIR = (
    PROJECT_ROOT
    / "skeletons"
)


# ============================================================
# MODEL HELPERS
# ============================================================

def normalize(name):
    """
    Normaliza nombres para poder comparar GLB y FBX.
    """

    return (
        name.lower()
        .replace("_rigged", "")
        .replace("_rig", "")
        .replace("-rigged", "")
        .replace("-rig", "")
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )


def expected_fbx(name):
    """
    Devuelve el nombre lógico del FBX esperado.
    """

    key = normalize(name)

    aliases = {
        "osopardo": "bear",
        "osopolar": "bear",
        "greatwhiteshark": "whiteshark",
    }

    return aliases.get(
        key,
        key,
    )


# ============================================================
# GRAPH DIAGNOSTICS
# ============================================================

def graph_depth(graph):
    """
    Calcula la profundidad máxima del graph.

    El curve graph puede no tener root explícito, por lo que
    probamos todos los nodos como posibles orígenes.

    Para un árbol:

        profundidad = máxima distancia topológica
    """

    if graph.number_of_nodes() == 0:
        return 0

    maximum = 0

    for source in graph.nodes:
        try:
            lengths = __import__(
                "networkx"
            ).single_source_shortest_path_length(
                graph,
                source,
            )

            if lengths:
                maximum = max(
                    maximum,
                    max(lengths.values()),
                )

        except Exception:
            continue

    return int(maximum)


def graph_root_candidates(graph):
    """
    Devuelve nodos candidatos a root.

    En un árbol no dirigido no existe un root formal,
    por lo que usamos nodos de grado 1 como candidatos.
    """

    return [
        node
        for node in graph.nodes
        if graph.degree(node) == 1
    ]


def graph_leaf_count(graph):
    """
    Número de hojas.
    """

    return sum(
        1
        for node in graph.nodes
        if graph.degree(node) == 1
    )


def graph_branch_count(graph):
    """
    Número de nodos de ramificación.

    Consideramos branch cualquier nodo con grado >= 3.
    """

    return sum(
        1
        for node in graph.nodes
        if graph.degree(node) >= 3
    )


def graph_max_degree(graph):
    """
    Máximo grado del graph.
    """

    if graph.number_of_nodes() == 0:
        return 0

    return max(
        graph.degree(node)
        for node in graph.nodes
    )


def graph_edge_lengths(graph):
    """
    Extrae las longitudes de las aristas.

    curve_graph ya almacena normalmente:

        edge["length"]

    pero mantenemos fallback geométrico.
    """

    lengths = []

    for a, b, data in graph.edges(
        data=True
    ):
        length = data.get(
            "length"
        )

        if length is not None:
            try:
                lengths.append(
                    float(length)
                )
                continue
            except (
                TypeError,
                ValueError,
            ):
                pass

        pa = graph.nodes[a].get(
            "position"
        )

        pb = graph.nodes[b].get(
            "position"
        )

        if pa is None or pb is None:
            continue

        pa = np.asarray(
            pa,
            dtype=float,
        )

        pb = np.asarray(
            pb,
            dtype=float,
        )

        lengths.append(
            float(
                np.linalg.norm(
                    pb - pa
                )
            )
        )

    return np.asarray(
        lengths,
        dtype=float,
    )


def graph_position_scale(graph):
    """
    Diagonal de la bounding box de las posiciones del graph.
    """

    positions = []

    for node, data in graph.nodes(
        data=True
    ):
        position = data.get(
            "position"
        )

        if position is None:
            continue

        position = np.asarray(
            position,
            dtype=float,
        )

        if position.shape != (3,):
            continue

        positions.append(
            position
        )

    if not positions:
        return 0.0

    positions = np.asarray(
        positions,
        dtype=float,
    )

    dimensions = (
        positions.max(axis=0)
        - positions.min(axis=0)
    )

    return float(
        np.linalg.norm(
            dimensions
        )
    )


# ============================================================
# FBX TREE DIAGNOSTICS
# ============================================================

def bone_children(bone):
    """
    Obtiene children de forma segura.
    """

    return list(
        getattr(
            bone,
            "children",
            [],
        )
        or []
    )


def fbx_tree_stats(root):
    """
    Calcula estadísticas del Bone Tree FBX.
    """

    nodes = 0
    leaves = 0
    branches = 0
    max_children = 0
    max_depth = 0
    lengths = []

    def walk(
        bone,
        depth,
    ):
        nonlocal nodes
        nonlocal leaves
        nonlocal branches
        nonlocal max_children
        nonlocal max_depth

        nodes += 1

        max_depth = max(
            max_depth,
            depth,
        )

        children = bone_children(
            bone
        )

        child_count = len(
            children
        )

        max_children = max(
            max_children,
            child_count,
        )

        if child_count == 0:
            leaves += 1

        if child_count >= 2:
            branches += 1

        position = getattr(
            bone,
            "global_position",
            None,
        )

        if position is None:
            position = getattr(
                bone,
                "position",
                None,
            )

        if position is not None:
            position = np.asarray(
                position,
                dtype=float,
            )

        for child in children:

            child_position = getattr(
                child,
                "global_position",
                None,
            )

            if child_position is None:
                child_position = getattr(
                    child,
                    "position",
                    None,
                )

            if (
                position is not None
                and child_position is not None
            ):
                child_position = np.asarray(
                    child_position,
                    dtype=float,
                )

                if (
                    position.shape == (3,)
                    and child_position.shape == (3,)
                ):
                    lengths.append(
                        float(
                            np.linalg.norm(
                                child_position
                                - position
                            )
                        )
                    )

            walk(
                child,
                depth + 1,
            )

    walk(
        root,
        0,
    )

    return {
        "nodes": nodes,
        "leaves": leaves,
        "branches": branches,
        "max_children": max_children,
        "depth": max_depth,
        "lengths": np.asarray(
            lengths,
            dtype=float,
        ),
    }


# ============================================================
# GLB DIAGNOSTIC
# ============================================================

def diagnose_glb(path):
    """
    Ejecuta el pipeline REAL utilizado por las pruebas:

        load_glb
        get_mesh
        fix_mesh
        generate_curve_graph
    """

    glb = load_glb(
        str(path)
    )

    mesh = get_mesh(
        glb
    )

    mesh = fix_mesh(
        mesh
    )

    graph = generate_curve_graph(
        mesh,
        sampling_dist=0.1,
    )

    edge_lengths = graph_edge_lengths(
        graph
    )

    stats = {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "leaves": graph_leaf_count(
            graph
        ),
        "branches": graph_branch_count(
            graph
        ),
        "max_degree": graph_max_degree(
            graph
        ),
        "depth": graph_depth(
            graph
        ),
        "scale": graph_position_scale(
            graph
        ),
        "lengths": edge_lengths,
    }

    return (
        mesh,
        graph,
        stats,
    )


# ============================================================
# FBX DIAGNOSTIC
# ============================================================

def diagnose_fbx(path):
    """
    Carga el Bone Tree FBX y calcula estadísticas.
    """

    root = load_fbx_skeleton(
        str(path)
    )

    stats = fbx_tree_stats(
        root
    )

    return (
        root,
        stats,
    )


# ============================================================
# PRINT GLB
# ============================================================

def print_glb_diagnostic(
    filename,
    stats,
):
    lengths = stats[
        "lengths"
    ]

    if len(lengths):
        length_mean = float(
            np.mean(lengths)
        )

        length_median = float(
            np.median(lengths)
        )

        length_min = float(
            np.min(lengths)
        )

        length_max = float(
            np.max(lengths)
        )

    else:
        length_mean = 0.0
        length_median = 0.0
        length_min = 0.0
        length_max = 0.0

    print(
        f"{filename:22}"
        f"{stats['nodes']:7d}"
        f"{stats['edges']:7d}"
        f"{stats['leaves']:8d}"
        f"{stats['branches']:8d}"
        f"{stats['max_degree']:8d}"
        f"{stats['depth']:8d}"
        f"{length_mean:11.4f}"
        f"{length_median:11.4f}"
    )


# ============================================================
# PRINT FBX
# ============================================================

def print_fbx_diagnostic(
    filename,
    stats,
):
    lengths = stats[
        "lengths"
    ]

    if len(lengths):
        length_mean = float(
            np.mean(lengths)
        )

        length_median = float(
            np.median(lengths)
        )

    else:
        length_mean = 0.0
        length_median = 0.0

    print(
        f"{filename:22}"
        f"{stats['nodes']:7d}"
        f"{stats['leaves']:8d}"
        f"{stats['branches']:8d}"
        f"{stats['max_children']:8d}"
        f"{stats['depth']:8d}"
        f"{length_mean:11.4f}"
        f"{length_median:11.4f}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 100)
    print("SKELETON DIAGNOSTIC")
    print("=" * 100)

    print()
    print(
        "PROJECT ROOT:",
        PROJECT_ROOT,
    )

    print(
        "GLB DIR:",
        GLB_DIR,
    )

    print(
        "FBX DIR:",
        FBX_DIR,
    )

    # ========================================================
    # GLB
    # ========================================================

    print()
    print("=" * 100)
    print("GLB SKELETON DIAGNOSTIC")
    print("=" * 100)

    print()

    print(
        f"{'MODEL':22}"
        f"{'NODES':>7}"
        f"{'EDGES':>7}"
        f"{'LEAVES':>8}"
        f"{'BRANCH':>8}"
        f"{'DEGREE':>8}"
        f"{'DEPTH':>8}"
        f"{'LEN_MEAN':>11}"
        f"{'LEN_MED':>11}"
    )

    print(
        "-" * 100
    )

    glb_results = {}

    glb_paths = sorted(
        GLB_DIR.glob("*.glb")
    )

    for path in glb_paths:

        print(
            f"  processing {path.name}...",
            flush=True,
        )

        try:

            (
                mesh,
                graph,
                stats,
            ) = diagnose_glb(
                path
            )

            glb_results[
                path
            ] = {
                "mesh": mesh,
                "graph": graph,
                "stats": stats,
            }

            print_glb_diagnostic(
                path.name,
                stats,
            )

        except Exception as exc:

            print(
                f"[ERROR] "
                f"{path.name}: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            traceback.print_exc()

    print()
    print(
        "GLB SIGNATURES:",
        len(glb_results),
    )

    # ========================================================
    # FBX
    # ========================================================

    print()
    print("=" * 100)
    print("FBX SKELETON DIAGNOSTIC")
    print("=" * 100)

    print()

    print(
        f"{'MODEL':22}"
        f"{'NODES':>7}"
        f"{'LEAVES':>8}"
        f"{'BRANCH':>8}"
        f"{'CHILD':>8}"
        f"{'DEPTH':>8}"
        f"{'LEN_MEAN':>11}"
        f"{'LEN_MED':>11}"
    )

    print(
        "-" * 100
    )

    fbx_results = {}

    fbx_paths = sorted(
        list(
            FBX_DIR.glob("*.fbx")
        )
        + list(
            FBX_DIR.glob("*.FBX")
        )
    )

    for path in fbx_paths:

        print(
            f"  processing {path.name}...",
            flush=True,
        )

        try:

            (
                root,
                stats,
            ) = diagnose_fbx(
                path
            )

            fbx_results[
                path
            ] = {
                "root": root,
                "stats": stats,
            }

            print_fbx_diagnostic(
                path.name,
                stats,
            )

        except Exception as exc:

            print(
                f"[ERROR] "
                f"{path.name}: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            traceback.print_exc()

    print()
    print(
        "FBX SIGNATURES:",
        len(fbx_results),
    )

    # ========================================================
    # EXPECTED PAIRS
    # ========================================================

    print()
    print("=" * 100)
    print("EXPECTED GLB -> FBX PAIRS")
    print("=" * 100)

    for glb_path in sorted(
        glb_results
    ):

        expected = expected_fbx(
            glb_path.stem
        )

        candidates = [
            path
            for path in fbx_results
            if normalize(
                path.stem
            ) == expected
        ]

        print()
        print(
            f"{glb_path.name:25}"
            f"-> expected {expected:20}"
            f"matches={len(candidates)}"
        )

        for candidate in candidates:

            glb_stats = glb_results[
                glb_path
            ][
                "stats"
            ]

            fbx_stats = fbx_results[
                candidate
            ][
                "stats"
            ]

            print(
                "   GLB:"
                f" nodes={glb_stats['nodes']}"
                f" leaves={glb_stats['leaves']}"
                f" branches={glb_stats['branches']}"
                f" degree={glb_stats['max_degree']}"
                f" depth={glb_stats['depth']}"
            )

            print(
                "   FBX:"
                f" nodes={fbx_stats['nodes']}"
                f" leaves={fbx_stats['leaves']}"
                f" branches={fbx_stats['branches']}"
                f" children={fbx_stats['max_children']}"
                f" depth={fbx_stats['depth']}"
            )

    # ========================================================
    # DIAGNOSTIC
    # ========================================================

    print()
    print("=" * 100)
    print("DIAGNOSTIC")
    print("=" * 100)

    print()
    print(
        "IMPORTANTE:"
    )

    print(
        "  GLB utiliza curve graph generado por TEASAR."
    )

    print(
        "  FBX utiliza Bone Tree."
    )

    print(
        "  Por tanto, NODE/LEAF/BRANCH no son todavía"
    )

    print(
        "  magnitudes estrictamente equivalentes."
    )

    print()
    print(
        "La finalidad de esta prueba es detectar"
    )

    print(
        "qué diferencias sistemáticas existen antes"
    )

    print(
        "de modificar el algoritmo de matching."
    )

    print()
    print("=" * 100)
    print("DONE")
    print("=" * 100)


if __name__ == "__main__":
    main()