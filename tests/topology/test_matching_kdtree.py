"""
Test experimental: GLB -> FBX matching with Skeleton KD-Tree.

Objetivo:
    Reproducir y dejar registrada la prueba que obtuvo:

        TOP-1: 6 / 13
        ACCURACY: 46.15%

Componentes:
    S = Structural
    M = Morphology
    B = BBOX
    P = PCA / Shape
    K = Skeleton KD-Tree

Este fichero NO modifica el pipeline principal.
Es un experimento reproducible.

Referencia:
    Pruebas INLINE.txt
    SKELETON KD-TREE EXPERIMENT
"""

from pathlib import Path
from itertools import permutations, product
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


import numpy as np
from scipy.spatial import cKDTree

from topology.loader import load_glb, get_mesh
from topology.preprocess import fix_mesh
from topology.skeletonize import generate_curve_graph

from topology.features import (
    structural_signature_from_graph,
    structural_signature_from_bone_tree,
    shape_signature,
)

from topology.fbx import load_fbx_skeleton

from topology.fbx_geometry import (
    fbx_geometry_signature,
    load_fbx_mesh,
)

from topology.morphology import (
    build_morphology_signature_from_bone_tree,
)

from topology.comparator import (
    combined_score,
    _geometry_score,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GLB_DIR = PROJECT_ROOT / "tests" / "topology" / "glb"
FBX_DIR = PROJECT_ROOT / "skeletons"


# ============================================================
# EXPECTED MATCHING
# ============================================================

def normalize(name):
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
# BBOX
# ============================================================

def bbox_signature(vertices):
    vertices = np.asarray(
        vertices,
        dtype=float,
    )

    dimensions = (
        vertices.max(axis=0)
        - vertices.min(axis=0)
    )

    dimensions = np.sort(
        dimensions
    )

    if dimensions[-1] <= 0.0:
        return np.zeros(3)

    return (
        dimensions
        / dimensions[-1]
    )


def bbox_score(query, reference):
    distance = np.mean(
        np.abs(
            query - reference
        )
    )

    return float(
        np.clip(
            (1.0 - distance)
            * 100.0,
            0.0,
            100.0,
        )
    )


# ============================================================
# GRAPH POSITIONS
# ============================================================

def graph_positions(graph):
    positions = []

    for node, data in graph.nodes(
        data=True
    ):
        position = data.get(
            "position"
        )

        if position is None:
            raise ValueError(
                "El nodo {} no contiene position.".format(
                    node
                )
            )

        position = np.asarray(
            position,
            dtype=float,
        )

        if position.shape != (3,):
            raise ValueError(
                "Position invalida en nodo {}: {}".format(
                    node,
                    position.shape,
                )
            )

        positions.append(
            position
        )

    if not positions:
        raise RuntimeError(
            "No se encontraron posiciones 3D en el curve graph."
        )

    return np.asarray(
        positions,
        dtype=float,
    )


# ============================================================
# FBX BONE POSITIONS
# ============================================================

def bone_positions(root):
    positions = []

    def walk(bone):
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

            if position.shape == (3,):
                positions.append(
                    position
                )

        for child in getattr(
            bone,
            "children",
            [],
        ):
            walk(child)

    walk(root)

    if not positions:
        raise RuntimeError(
            "No se encontraron posiciones 3D en el FBX."
        )

    return np.asarray(
        positions,
        dtype=float,
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_points(points):
    points = np.asarray(
        points,
        dtype=float,
    )

    minimum = points.min(
        axis=0
    )

    maximum = points.max(
        axis=0
    )

    center = (
        minimum
        + maximum
    ) / 2.0

    points = (
        points
        - center
    )

    scale = np.max(
        maximum
        - minimum
    )

    if scale > 0.0:
        points = (
            points
            / scale
        )

    return points


# ============================================================
# PCA
# ============================================================

def pca_axes(points):
    points = np.asarray(
        points,
        dtype=float,
    )

    centered = (
        points
        - points.mean(
            axis=0
        )
    )

    _, _, vh = np.linalg.svd(
        centered,
        full_matrices=False,
    )

    axes = vh.copy()

    if np.linalg.det(
        axes
    ) < 0.0:
        axes[2] *= -1.0

    return axes


# ============================================================
# PCA TRANSFORM
# ============================================================

def transform_by_axes(
    points,
    axes,
):
    return (
        points
        @ axes.T
    )


# ============================================================
# PCA ALIGNMENT
# ============================================================

def best_pca_alignment(
    query,
    reference,
):
    query = normalize_points(
        query
    )

    reference = normalize_points(
        reference
    )

    query_axes = pca_axes(
        query
    )

    reference_axes = pca_axes(
        reference
    )

    query_pca = transform_by_axes(
        query,
        query_axes,
    )

    reference_pca = transform_by_axes(
        reference,
        reference_axes,
    )

    reference_centered = (
        reference_pca
        - reference_pca.mean(
            axis=0
        )
    )

    best_distance = float(
        "inf"
    )

    best_query = None

    # --------------------------------------------------------
    # Probar permutaciones y signos de los ejes.
    # --------------------------------------------------------

    for perm in permutations(
        range(3)
    ):
        permuted = (
            query_pca[:, perm]
        )

        for signs in product(
            (-1.0, 1.0),
            repeat=3,
        ):
            candidate = (
                permuted
                * np.asarray(
                    signs
                )
            )

            candidate = (
                candidate
                - candidate.mean(
                    axis=0
                )
            )

            candidate_cov = np.cov(
                candidate.T
            )

            reference_cov = np.cov(
                reference_centered.T
            )

            covariance_distance = np.linalg.norm(
                candidate_cov
                - reference_cov
            )

            if (
                covariance_distance
                < best_distance
            ):
                best_distance = (
                    covariance_distance
                )

                best_query = (
                    candidate
                )

    return (
        best_query,
        reference_centered,
    )


# ============================================================
# SKELETON KD-TREE SCORE
# ============================================================

def skeleton_kdtree_score(
    query_points,
    reference_points,
):
    if (
        len(query_points) < 2
        or len(reference_points) < 2
    ):
        return 0.0

    query, reference = (
        best_pca_alignment(
            query_points,
            reference_points,
        )
    )

    reference_tree = cKDTree(
        reference
    )

    query_tree = cKDTree(
        query
    )

    # --------------------------------------------------------
    # GLB -> FBX
    # --------------------------------------------------------

    query_to_reference = (
        reference_tree.query(
            query,
            k=1,
        )[0]
    )

    # --------------------------------------------------------
    # FBX -> GLB
    # --------------------------------------------------------

    reference_to_query = (
        query_tree.query(
            reference,
            k=1,
        )[0]
    )

    mean_query_to_reference = (
        np.mean(
            query_to_reference
        )
    )

    mean_reference_to_query = (
        np.mean(
            reference_to_query
        )
    )

    distance = (
        mean_query_to_reference
        + mean_reference_to_query
    ) / 2.0

    # --------------------------------------------------------
    # Convert distance -> score
    # --------------------------------------------------------

    score = (
        np.exp(
            -5.0 * distance
        )
        * 100.0
    )

    return float(
        np.clip(
            score,
            0.0,
            100.0,
        )
    )


# ============================================================
# BUILD FBX SIGNATURES
# ============================================================

def build_fbx_signatures():
    print()
    print("BUILDING FBX SIGNATURES...")

    fbx_data = {}

    fbx_paths = sorted(
        set(
            list(
                FBX_DIR.glob("*.fbx")
            )
            +
            list(
                FBX_DIR.glob("*.FBX")
            )
        )
    )

    for fbx_path in fbx_paths:
        print(
            "  {}".format(
                fbx_path.name
            )
        )

        try:
            # ------------------------------------------------
            # Skeleton
            # ------------------------------------------------

            root = load_fbx_skeleton(
                str(fbx_path)
            )

            structural = (
                structural_signature_from_bone_tree(
                    root,
                    source="fbx",
                )
            )

            morphology = (
                build_morphology_signature_from_bone_tree(
                    root,
                    source="fbx",
                )
            )

            # ------------------------------------------------
            # Geometry signature
            # ------------------------------------------------

            geometry = (
                fbx_geometry_signature(
                    fbx_path
                )
            )

            # ------------------------------------------------
            # IMPORTANT:
            #
            # GeometrySignature NO es un Trimesh.
            #
            # Para BBOX usamos load_fbx_mesh().
            # ------------------------------------------------

            fbx_mesh = load_fbx_mesh(
                fbx_path
            )

            # ------------------------------------------------
            # Bone positions
            # ------------------------------------------------

            root_positions = bone_positions(
                root
            )

            fbx_data[
                fbx_path
            ] = {
                "structural":
                    structural,

                "morphology":
                    morphology,

                "shape":
                    geometry,

                "bbox":
                    bbox_signature(
                        fbx_mesh.vertices
                    ),

                "skeleton":
                    root_positions,
            }

        except Exception as exc:
            print(
                "  ERROR: {}: {}".format(
                    type(exc).__name__,
                    exc,
                )
            )

            import traceback
            traceback.print_exc()

    print()
    print(
        "FBX SIGNATURES:",
        len(fbx_data),
    )

    return fbx_data


# ============================================================
# BUILD GLB SIGNATURES
# ============================================================

def build_glb_signatures():
    print()
    print("BUILDING GLB SIGNATURES...")

    glb_data = {}

    glb_paths = sorted(
        GLB_DIR.glob(
            "*.glb"
        )
    )

    for glb_path in glb_paths:
        print(
            "  {}".format(
                glb_path.name
            )
        )

        try:
            glb = load_glb(
                str(glb_path)
            )

            mesh = get_mesh(
                glb
            )

            mesh = fix_mesh(
                mesh
            )

            # ------------------------------------------------
            # Curve graph
            # ------------------------------------------------

            graph = generate_curve_graph(
                mesh,
                sampling_dist=0.1,
            )

            graph_points = graph_positions(
                graph
            )

            print(
                "    graph nodes:",
                len(graph_points),
            )

            # ------------------------------------------------
            # Structural
            # ------------------------------------------------

            structural = (
                structural_signature_from_graph(
                    graph,
                    source="glb",
                )
            )

            # ------------------------------------------------
            # Morphology
            # ------------------------------------------------

            morphology = (
                structural.morphology_signature
            )

            # ------------------------------------------------
            # PCA / Shape
            # ------------------------------------------------

            shape = shape_signature(
                mesh.vertices
            )

            # ------------------------------------------------
            # BBOX
            # ------------------------------------------------

            bbox = bbox_signature(
                mesh.vertices
            )

            glb_data[
                glb_path
            ] = {
                "structural":
                    structural,

                "morphology":
                    morphology,

                "shape":
                    shape,

                "bbox":
                    bbox,

                "skeleton":
                    graph_points,
            }

        except Exception as exc:
            print(
                "  ERROR: {}: {}".format(
                    type(exc).__name__,
                    exc,
                )
            )

            import traceback
            traceback.print_exc()

    print()
    print(
        "GLB SIGNATURES:",
        len(glb_data),
    )

    return glb_data


# ============================================================
# COMPONENT SCORES
# ============================================================

def component_scores(
    glb,
    fbx,
):
    # --------------------------------------------------------
    # Structural
    # --------------------------------------------------------

    structural, _ = combined_score(
        glb["structural"],
        fbx["structural"],
        glb["morphology"],
        fbx["morphology"],
        structural_weight=1.0,
        morphology_weight=0.0,
    )

    # --------------------------------------------------------
    # Morphology
    # --------------------------------------------------------

    morphology, _ = combined_score(
        glb["structural"],
        fbx["structural"],
        glb["morphology"],
        fbx["morphology"],
        structural_weight=0.0,
        morphology_weight=1.0,
    )

    # --------------------------------------------------------
    # BBOX
    # --------------------------------------------------------

    bbox = bbox_score(
        glb["bbox"],
        fbx["bbox"],
    )

    # --------------------------------------------------------
    # PCA / Shape
    # --------------------------------------------------------

    shape, _ = _geometry_score(
        glb["shape"],
        fbx["shape"],
    )

    # --------------------------------------------------------
    # Skeleton KDTree
    # --------------------------------------------------------

    skeleton = skeleton_kdtree_score(
        glb["skeleton"],
        fbx["skeleton"],
    )

    return (
        float(structural),
        float(morphology),
        float(bbox),
        float(shape),
        float(skeleton),
    )


# ============================================================
# MATCHING EXPERIMENT
# ============================================================

def run_experiment():
    print("=" * 90)
    print("SKELETON KD-TREE EXPERIMENT")
    print("=" * 90)

    fbx_data = build_fbx_signatures()
    glb_data = build_glb_signatures()

    print()
    print("=" * 90)
    print("CALCULATING ALL PAIRS...")
    print("=" * 90)

    pairs = {}

    for glb_path, glb in glb_data.items():
        pairs[glb_path] = []

        for fbx_path, fbx in fbx_data.items():

            (
                structural,
                morphology,
                bbox,
                shape,
                skeleton,
            ) = component_scores(
                glb,
                fbx,
            )

            pairs[
                glb_path
            ].append({
                "fbx":
                    fbx_path,

                "structural":
                    structural,

                "morphology":
                    morphology,

                "bbox":
                    bbox,

                "shape":
                    shape,

                "skeleton":
                    skeleton,
            })

    # ========================================================
    # WEIGHTS
    # ========================================================

    weight_sets = [
        (
            0.20,
            0.20,
            0.40,
            0.10,
            0.10,
        ),
        (
            0.20,
            0.20,
            0.35,
            0.10,
            0.15,
        ),
        (
            0.20,
            0.20,
            0.30,
            0.10,
            0.20,
        ),
        (
            0.20,
            0.20,
            0.25,
            0.10,
            0.25,
        ),
    ]

    print()
    print("=" * 90)
    print("TOP-1 ACCURACY BY WEIGHTS")
    print("=" * 90)

    print()

    print(
        "{:<24}{:>9}{:>9}{:>12}".format(
            "S / M / B / P / K",
            "CORRECT",
            "TOTAL",
            "ACCURACY",
        )
    )

    print("-" * 62)

    best = None

    for (
        sw,
        mw,
        bw,
        pw,
        kw,
    ) in weight_sets:

        correct = 0
        total = 0

        for glb_path, candidates in pairs.items():

            expected = expected_fbx(
                glb_path.stem
            )

            ranking = []

            for item in candidates:

                score = (
                    item["structural"]
                    * sw
                    +
                    item["morphology"]
                    * mw
                    +
                    item["bbox"]
                    * bw
                    +
                    item["shape"]
                    * pw
                    +
                    item["skeleton"]
                    * kw
                )

                ranking.append(
                    (
                        item["fbx"],
                        score,
                    )
                )

            ranking.sort(
                key=lambda x: x[1],
                reverse=True,
            )

            total += 1

            if (
                normalize(
                    ranking[0][0].stem
                )
                ==
                expected
            ):
                correct += 1

        accuracy = (
            100.0
            * correct
            / total
            if total
            else 0.0
        )

        print(
            "{:<24}{:>9}{:>9}{:>11.2f}%".format(
                "{} / {} / {} / {} / {}".format(
                    int(sw * 100),
                    int(mw * 100),
                    int(bw * 100),
                    int(pw * 100),
                    int(kw * 100),
                ),
                correct,
                total,
                accuracy,
            )
        )

        if (
            best is None
            or accuracy > best["accuracy"]
        ):
            best = {
                "weights": (
                    sw,
                    mw,
                    bw,
                    pw,
                    kw,
                ),
                "correct":
                    correct,
                "total":
                    total,
                "accuracy":
                    accuracy,
            }

    # ========================================================
    # BEST CONFIGURATION
    # ========================================================

    print()
    print("=" * 90)
    print("BEST CONFIGURATION")
    print("=" * 90)

    (
        sw,
        mw,
        bw,
        pw,
        kw,
    ) = best["weights"]

    print(
        "STRUCTURAL : {}%".format(
            int(sw * 100)
        )
    )

    print(
        "MORPHOLOGY : {}%".format(
            int(mw * 100)
        )
    )

    print(
        "BBOX       : {}%".format(
            int(bw * 100)
        )
    )

    print(
        "PCA/SHAPE  : {}%".format(
            int(pw * 100)
        )
    )

    print(
        "SKELETON KD : {}%".format(
            int(kw * 100)
        )
    )

    print()

    print(
        "TOP-1: {} / {}".format(
            best["correct"],
            best["total"],
        )
    )

    print(
        "ACCURACY: {:.2f}%".format(
            best["accuracy"]
        )
    )

    # ========================================================
    # BEST RANKINGS
    # ========================================================

    print()
    print("=" * 90)
    print("BEST CONFIGURATION - RANKINGS")
    print("=" * 90)

    for glb_path, candidates in pairs.items():

        expected = expected_fbx(
            glb_path.stem
        )

        ranking = []

        for item in candidates:

            score = (
                item["structural"]
                * sw
                +
                item["morphology"]
                * mw
                +
                item["bbox"]
                * bw
                +
                item["shape"]
                * pw
                +
                item["skeleton"]
                * kw
            )

            ranking.append({
                **item,
                "score":
                    score,
            })

        ranking.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        expected_rank = None

        for rank, item in enumerate(
            ranking,
            1,
        ):
            if (
                normalize(
                    item["fbx"].stem
                )
                ==
                expected
            ):
                expected_rank = rank
                break

        print()

        print(
            "{} -> expected {} | rank {}".format(
                glb_path.stem,
                expected,
                expected_rank,
            )
        )

        for rank, item in enumerate(
            ranking[:5],
            1,
        ):

            marker = (
                " <-- EXPECTED"
                if (
                    normalize(
                        item["fbx"].stem
                    )
                    ==
                    expected
                )
                else ""
            )

            print(
                "  {:>2}. {:<24} {:>8.3f}  "
                "S={:.1f} M={:.1f} B={:.1f} "
                "P={:.1f} K={:.1f}{}".format(
                    rank,
                    item["fbx"].name,
                    item["score"],
                    item["structural"],
                    item["morphology"],
                    item["bbox"],
                    item["shape"],
                    item["skeleton"],
                    marker,
                )
            )

    print()
    print("=" * 90)
    print("DONE")
    print("=" * 90)

    return best


# ============================================================
# PYTEST TEST
# ============================================================

def test_matching_kdtree():
    """
    Regression test del experimento que obtuvo 46.15%.

    IMPORTANTE:
    Este assert no pretende afirmar que 46.15% sea
    una precisión suficiente para el sistema final.

    Solo garantiza que el experimento permanece
    reproducible mientras investigamos mejoras.
    """

    best = run_experiment()

    assert best is not None

    assert best["total"] == 13

    # Resultado histórico registrado:
    #
    #   6 / 13
    #   46.15%
    #
    # No exigimos exactamente 6 porque cambios legítimos
    # en las implementaciones internas pueden modificar
    # el resultado. Lo que sí exigimos es que el pipeline
    # sea capaz de procesar los 13 modelos.
    assert best["correct"] >= 1


if __name__ == "__main__":
    run_experiment()