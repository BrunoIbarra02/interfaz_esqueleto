"""
Skeleton Comparator

Compara StructuralSignature de modelos GLB y FBX.

El score representa similitud estructural relativa.
NO representa una probabilidad ni garantiza que el rigging vaya a funcionar.

Componentes del score:

    TOPOLOGY       30%
    DEGREE         20%
    DEPTH          15%
    LENGTHS        20%
    SYMMETRY       15%
"""

import math

import numpy as np

from topology.features import (
    GeometrySignature,
    SkinSignature,
    StructuralSignature,
)

from topology.morphology import (
    MorphologySignature,
    compare_morphology,
)


# ============================================================
# GENERIC HELPERS
# ============================================================

def _similarity_difference(
    a: float,
    b: float,
    scale: float = 1.0,
) -> float:
    """
    Convierte una diferencia absoluta en una similitud [0, 1].

    1.0 = iguales
    0.0 = diferencia muy grande
    """

    denominator = max(
        abs(float(a)),
        abs(float(b)),
        scale,
        1e-9,
    )

    difference = abs(
        float(a) - float(b)
    ) / denominator

    return float(
        np.clip(
            1.0 - difference,
            0.0,
            1.0,
        )
    )


def _ratio(
    value: float,
    total: float,
) -> float:
    """
    Calcula una proporción de forma segura.
    """

    return float(value) / max(
        float(total),
        1.0,
    )


# ============================================================
# TOPOLOGY SCORE
# ============================================================

def _topology_score(
    query: StructuralSignature,
    reference: StructuralSignature,
) -> tuple[float, dict]:
    """
    Compara la estructura topológica global.

    No utiliza los valores absolutos únicamente.
    También compara proporciones para evitar penalizar
    demasiado las diferencias de resolución del skeleton.
    """

    query_nodes = max(
        query.node_count,
        1,
    )

    reference_nodes = max(
        reference.node_count,
        1,
    )

    # --------------------------------------------------------
    # NODE SCALE
    # --------------------------------------------------------

    node_similarity = _similarity_difference(
        query.node_count,
        reference.node_count,
        scale=max(
            query_nodes,
            reference_nodes,
            1,
        ) * 0.10,
    )

    # --------------------------------------------------------
    # LEAF RATIO
    # --------------------------------------------------------

    query_leaf_ratio = _ratio(
        query.leaf_count,
        query_nodes,
    )

    reference_leaf_ratio = _ratio(
        reference.leaf_count,
        reference_nodes,
    )

    leaf_ratio_similarity = _similarity_difference(
        query_leaf_ratio,
        reference_leaf_ratio,
        scale=0.10,
    )

    # --------------------------------------------------------
    # BRANCH RATIO
    # --------------------------------------------------------

    query_branch_ratio = _ratio(
        query.branch_count,
        query_nodes,
    )

    reference_branch_ratio = _ratio(
        reference.branch_count,
        reference_nodes,
    )

    branch_ratio_similarity = _similarity_difference(
        query_branch_ratio,
        reference_branch_ratio,
        scale=0.10,
    )

    # --------------------------------------------------------
    # EDGE RATIO
    # --------------------------------------------------------

    query_edge_ratio = _ratio(
        query.edge_count,
        query_nodes,
    )

    reference_edge_ratio = _ratio(
        reference.edge_count,
        reference_nodes,
    )

    edge_ratio_similarity = _similarity_difference(
        query_edge_ratio,
        reference_edge_ratio,
        scale=0.10,
    )

    # --------------------------------------------------------
    # MAX DEGREE
    # --------------------------------------------------------

    max_degree_similarity = _similarity_difference(
        query.max_degree,
        reference.max_degree,
        scale=1.0,
    )

    # --------------------------------------------------------
    # FINAL TOPOLOGY
    # --------------------------------------------------------

    score = 100.0 * (
        0.15 * node_similarity
        + 0.25 * leaf_ratio_similarity
        + 0.25 * branch_ratio_similarity
        + 0.20 * edge_ratio_similarity
        + 0.15 * max_degree_similarity
    )

    return (
        score,
        {
            "node_similarity":
                round(
                    node_similarity,
                    4,
                ),

            "leaf_ratio_similarity":
                round(
                    leaf_ratio_similarity,
                    4,
                ),

            "branch_ratio_similarity":
                round(
                    branch_ratio_similarity,
                    4,
                ),

            "edge_ratio_similarity":
                round(
                    edge_ratio_similarity,
                    4,
                ),

            "max_degree_similarity":
                round(
                    max_degree_similarity,
                    4,
                ),

            "query_leaf_ratio":
                round(
                    query_leaf_ratio,
                    4,
                ),

            "reference_leaf_ratio":
                round(
                    reference_leaf_ratio,
                    4,
                ),

            "query_branch_ratio":
                round(
                    query_branch_ratio,
                    4,
                ),

            "reference_branch_ratio":
                round(
                    reference_branch_ratio,
                    4,
                ),
        },
    )


# ============================================================
# DEGREE SCORE
# ============================================================

def _degree_score(
    query: StructuralSignature,
    reference: StructuralSignature,
) -> tuple[float, dict]:
    """
    Compara la distribución de grados del grafo.

    degree_histogram tiene la estructura:

        [degree0,
         degree1,
         degree2,
         degree3,
         degree4,
         degree5+]
    """

    query_hist = np.asarray(
        query.degree_histogram,
        dtype=float,
    )

    reference_hist = np.asarray(
        reference.degree_histogram,
        dtype=float,
    )

    # --------------------------------------------------------
    # NORMALIZE LENGTH
    # --------------------------------------------------------

    size = max(
        len(query_hist),
        len(reference_hist),
    )

    query_padded = np.zeros(
        size,
        dtype=float,
    )

    reference_padded = np.zeros(
        size,
        dtype=float,
    )

    query_padded[
        :len(query_hist)
    ] = query_hist

    reference_padded[
        :len(reference_hist)
    ] = reference_hist

    # --------------------------------------------------------
    # NORMALIZE TO DISTRIBUTIONS
    # --------------------------------------------------------

    query_total = max(
        query_padded.sum(),
        1.0,
    )

    reference_total = max(
        reference_padded.sum(),
        1.0,
    )

    query_distribution = (
        query_padded
        / query_total
    )

    reference_distribution = (
        reference_padded
        / reference_total
    )

    # --------------------------------------------------------
    # L1 DISTANCE
    # --------------------------------------------------------

    distance = float(
        np.sum(
            np.abs(
                query_distribution
                -
                reference_distribution
            )
        )
    )

    # L1 máximo = 2
    similarity = 1.0 - (
        distance / 2.0
    )

    similarity = float(
        np.clip(
            similarity,
            0.0,
            1.0,
        )
    )

    # --------------------------------------------------------
    # MAX DEGREE
    # --------------------------------------------------------

    max_degree_similarity = _similarity_difference(
        query.max_degree,
        reference.max_degree,
        scale=1.0,
    )

    score = 100.0 * (
        0.85 * similarity
        + 0.15 * max_degree_similarity
    )

    return (
        score,
        {
            "histogram_similarity":
                round(
                    similarity,
                    4,
                ),

            "max_degree_similarity":
                round(
                    max_degree_similarity,
                    4,
                ),

            "query_histogram":
                query.degree_histogram,

            "reference_histogram":
                reference.degree_histogram,
        },
    )


# ============================================================
# DEPTH SCORE
# ============================================================

def _depth_score(
    query: StructuralSignature,
    reference: StructuralSignature,
) -> tuple[float, dict]:
    """
    Compara la profundidad topológica del skeleton.
    """

    max_depth_similarity = _similarity_difference(
        query.max_depth,
        reference.max_depth,
        scale=2.0,
    )

    mean_similarity = _similarity_difference(
        query.depth_mean,
        reference.depth_mean,
        scale=1.0,
    )

    median_similarity = _similarity_difference(
        query.depth_median,
        reference.depth_median,
        scale=1.0,
    )

    score = 100.0 * (
        0.40 * max_depth_similarity
        + 0.35 * mean_similarity
        + 0.25 * median_similarity
    )

    return (
        score,
        {
            "max_depth_similarity":
                round(
                    max_depth_similarity,
                    4,
                ),

            "depth_mean_similarity":
                round(
                    mean_similarity,
                    4,
                ),

            "depth_median_similarity":
                round(
                    median_similarity,
                    4,
                ),

            "query_max_depth":
                query.max_depth,

            "reference_max_depth":
                reference.max_depth,

            "query_depth_mean":
                round(
                    query.depth_mean,
                    4,
                ),

            "reference_depth_mean":
                round(
                    reference.depth_mean,
                    4,
                ),

            "query_depth_median":
                round(
                    query.depth_median,
                    4,
                ),

            "reference_depth_median":
                round(
                    reference.depth_median,
                    4,
                ),
        },
    )


# ============================================================
# LENGTH DISTRIBUTION
# ============================================================

def _length_score(
    query: StructuralSignature,
    reference: StructuralSignature,
) -> tuple[float, dict]:
    """
    Compara la distribución de longitudes normalizadas.

    IMPORTANTE:

    NO compara las listas directamente.

    Las listas dependen del orden de las aristas de
    NetworkX, que no tiene por qué ser equivalente entre
    dos esqueletos estructuralmente iguales.

    Se utilizan percentiles de la distribución.
    """

    query_lengths = np.asarray(
        query.normalized_lengths,
        dtype=float,
    )

    reference_lengths = np.asarray(
        reference.normalized_lengths,
        dtype=float,
    )

    if (
        len(query_lengths) == 0
        or len(reference_lengths) == 0
    ):
        return (
            0.0,
            {
                "reason":
                    "No hay longitudes suficientes."
            },
        )

    # --------------------------------------------------------
    # PERCENTILES
    # --------------------------------------------------------

    percentiles = np.asarray(
        [
            0,
            10,
            25,
            50,
            75,
            90,
            100,
        ],
        dtype=float,
    )

    query_percentiles = np.percentile(
        query_lengths,
        percentiles,
    )

    reference_percentiles = np.percentile(
        reference_lengths,
        percentiles,
    )

    # --------------------------------------------------------
    # COMPARE DISTRIBUTIONS
    # --------------------------------------------------------

    similarities = []

    for query_value, reference_value in zip(
        query_percentiles,
        reference_percentiles,
    ):
        similarities.append(
            _similarity_difference(
                query_value,
                reference_value,
                scale=0.01,
            )
        )

    distribution_similarity = float(
        np.mean(
            similarities
        )
    )

    # --------------------------------------------------------
    # SUMMARY STATISTICS
    # --------------------------------------------------------

    min_similarity = _similarity_difference(
        query.normalized_length_min,
        reference.normalized_length_min,
        scale=0.01,
    )

    max_similarity = _similarity_difference(
        query.normalized_length_max,
        reference.normalized_length_max,
        scale=0.05,
    )

    mean_similarity = _similarity_difference(
        query.normalized_length_mean,
        reference.normalized_length_mean,
        scale=0.01,
    )

    std_similarity = _similarity_difference(
        query.normalized_length_std,
        reference.normalized_length_std,
        scale=0.01,
    )

    summary_similarity = (
        0.15 * min_similarity
        + 0.20 * max_similarity
        + 0.35 * mean_similarity
        + 0.30 * std_similarity
    )

    score = 100.0 * (
        0.70 * distribution_similarity
        + 0.30 * summary_similarity
    )

    return (
        score,
        {
            "distribution_similarity":
                round(
                    distribution_similarity,
                    4,
                ),

            "min_similarity":
                round(
                    min_similarity,
                    4,
                ),

            "max_similarity":
                round(
                    max_similarity,
                    4,
                ),

            "mean_similarity":
                round(
                    mean_similarity,
                    4,
                ),

            "std_similarity":
                round(
                    std_similarity,
                    4,
                ),

            "query_percentiles":
                [
                    round(
                        float(value),
                        5,
                    )
                    for value
                    in query_percentiles
                ],

            "reference_percentiles":
                [
                    round(
                        float(value),
                        5,
                    )
                    for value
                    in reference_percentiles
                ],
        },
    )


# ============================================================
# SYMMETRY SCORE
# ============================================================

def _symmetry_score(
    query: StructuralSignature,
    reference: StructuralSignature,
) -> tuple[float, dict]:
    """
    Compara la simetría bilateral estimada.
    """

    difference = abs(
        query.symmetry_score
        -
        reference.symmetry_score
    )

    similarity = float(
        np.clip(
            1.0 - difference,
            0.0,
            1.0,
        )
    )

    score = (
        similarity
        * 100.0
    )

    return (
        score,
        {
            "query_symmetry":
                round(
                    query.symmetry_score,
                    4,
                ),

            "reference_symmetry":
                round(
                    reference.symmetry_score,
                    4,
                ),

            "symmetry_similarity":
                round(
                    similarity,
                    4,
                ),
        },
    )


# ============================================================
# STRUCTURAL SCORE
# ============================================================

def structural_score(
    query: StructuralSignature,
    reference: StructuralSignature,
) -> tuple[float, dict]:
    """
    Calcula el score estructural final.

    Pesos:

        topology  = 20%
        degree    = 10%
        depth     = 15%
        lengths   = 25%
        symmetry  = 30%

    Los pesos son heurísticos y no están calibrados contra
    un dataset. Se priorizan características más robustas
    entre representaciones GLB geométrica y FBX jerárquica.
    """

    topology_score, topology_details = (
        _topology_score(
            query,
            reference,
        )
    )

    degree_score, degree_details = (
        _degree_score(
            query,
            reference,
        )
    )

    depth_score, depth_details = (
        _depth_score(
            query,
            reference,
        )
    )

    length_score, length_details = (
        _length_score(
            query,
            reference,
        )
    )

    symmetry_score, symmetry_details = (
        _symmetry_score(
            query,
            reference,
        )
    )

    # --------------------------------------------------------
    # WEIGHTED SCORE
    # --------------------------------------------------------

    topology_contribution = (
        topology_score
        * 0.20
    )

    degree_contribution = (
        degree_score
        * 0.10
    )

    depth_contribution = (
        depth_score
        * 0.15
    )

    length_contribution = (
        length_score
        * 0.25
    )

    symmetry_contribution = (
        symmetry_score
        * 0.30
    )

    total = (
        topology_contribution
        + degree_contribution
        + depth_contribution
        + length_contribution
        + symmetry_contribution
    )

    return (
        float(
            np.clip(
                total,
                0.0,
                100.0,
            )
        ),
        {
            "topology": {
                "score":
                    round(
                        topology_score,
                        3,
                    ),
                "weight":
                    0.20,
                "contribution":
                    round(
                        topology_contribution,
                        3,
                    ),
                "details":
                    topology_details,
            },

            "degree": {
                "score":
                    round(
                        degree_score,
                        3,
                    ),
                "weight":
                    0.10,
                "contribution":
                    round(
                        degree_contribution,
                        3,
                    ),
                "details":
                    degree_details,
            },

            "depth": {
                "score":
                    round(
                        depth_score,
                        3,
                    ),
                "weight":
                    0.15,
                "contribution":
                    round(
                        depth_contribution,
                        3,
                    ),
                "details":
                    depth_details,
            },

            "lengths": {
                "score":
                    round(
                        length_score,
                        3,
                    ),
                "weight":
                    0.25,
                "contribution":
                    round(
                        length_contribution,
                        3,
                    ),
                "details":
                    length_details,
            },

            "symmetry": {
                "score":
                    round(
                        symmetry_score,
                        3,
                    ),
                "weight":
                    0.30,
                "contribution":
                    round(
                        symmetry_contribution,
                        3,
                    ),
                "details":
                    symmetry_details,
            },
        },
    )


# ============================================================
# COMBINED STRUCTURAL + MORPHOLOGY SCORE
# ============================================================

def combined_score(
    structural_query: StructuralSignature,
    structural_reference: StructuralSignature,
    morphology_query: MorphologySignature,
    morphology_reference: MorphologySignature,
    structural_weight: float = 0.50,
    morphology_weight: float = 0.50,
) -> tuple[float, dict]:
    """
    Combina el score estructural y el score morfológico.

    Los pesos son provisionales y heurísticos.
    No están calibrados contra un dataset.

    Returns
    -------
    tuple[float, dict]
        Score final entre 0 y 100 y desglose de componentes.
    """

    if structural_weight < 0.0 or morphology_weight < 0.0:
        raise ValueError(
            "Los pesos no pueden ser negativos."
        )

    total_weight = (
        float(structural_weight)
        + float(morphology_weight)
    )

    if total_weight <= 0.0:
        raise ValueError(
            "La suma de pesos debe ser mayor que cero."
        )

    structural_weight = (
        float(structural_weight)
        / total_weight
    )

    morphology_weight = (
        float(morphology_weight)
        / total_weight
    )

    structural_value, structural_details = (
        structural_score(
            structural_query,
            structural_reference,
        )
    )

    morphology_result = compare_morphology(
        morphology_query,
        morphology_reference,
    )

    morphology_value = float(
        morphology_result["score"]
    ) * 100.0

    final_score = (
        structural_value * structural_weight
        + morphology_value * morphology_weight
    )

    return (
        float(
            np.clip(
                final_score,
                0.0,
                100.0,
            )
        ),
        {
            "structural": {
                "score": float(structural_value),
                "weight": structural_weight,
                "contribution": (
                    structural_value
                    * structural_weight
                ),
                "details": structural_details,
            },
            "morphology": {
                "score": float(morphology_value),
                "weight": morphology_weight,
                "contribution": (
                    morphology_value
                    * morphology_weight
                ),
                "details": morphology_result,
            },
            "weights": {
                "structural": structural_weight,
                "morphology": morphology_weight,
            },
        },
    )


# ============================================================
# COMPARATOR
# ============================================================

class SkeletonComparator:
    """
    Compara dos StructuralSignature.

    El resultado es un score de similitud estructural
    entre 0 y 100.
    """

    def compare(
        self,
        query,
        reference,
    ):
        """
        Compara query contra reference.

        Returns
        -------
        tuple[float, dict]
            Score y detalles.
        """

        # ----------------------------------------------------
        # STRUCTURAL SIGNATURE
        # ----------------------------------------------------

        if (
            isinstance(
                query,
                StructuralSignature,
            )
            and
            isinstance(
                reference,
                StructuralSignature,
            )
        ):
            return structural_score(
                query,
                reference,
            )

        # ----------------------------------------------------
        # LEGACY GEOMETRY
        # ----------------------------------------------------

        if (
            isinstance(
                query,
                GeometrySignature,
            )
            and
            isinstance(
                reference,
                GeometrySignature,
            )
        ):
            return _geometry_score(
                query,
                reference,
            )

        # ----------------------------------------------------
        # LEGACY SKIN
        # ----------------------------------------------------

        if (
            isinstance(
                query,
                SkinSignature,
            )
            and
            isinstance(
                reference,
                SkinSignature,
            )
        ):
            return self._skin_score(
                query,
                reference,
            )

        return (
            0.0,
            {
                "reason":
                    "Las firmas no son compatibles."
            },
        )

    # ========================================================
    # LEGACY SKIN SCORE
    # ========================================================

    def _skin_score(
        self,
        query: SkinSignature,
        reference: SkinSignature,
    ):
        """
        Comparador antiguo para SkinSignature.

        Se mantiene por compatibilidad.
        """

        count = math.exp(
            -abs(
                query.joint_count
                -
                reference.joint_count
            )
            / 12
        )

        leaf = math.exp(
            -abs(
                query.leaf_count
                -
                reference.leaf_count
            )
            / 5
        )

        root = math.exp(
            -abs(
                query.root_count
                -
                reference.root_count
            )
            / 2
        )

        names = name_similarity(
            query.names,
            reference.names,
        )

        score = 100.0 * (
            0.45 * count
            + 0.25 * leaf
            + 0.10 * root
            + 0.20 * names
        )

        return (
            score,
            {
                "joint_count":
                    round(
                        count,
                        3,
                    ),

                "leaf_count":
                    round(
                        leaf,
                        3,
                    ),

                "root_count":
                    round(
                        root,
                        3,
                    ),

                "joint_names":
                    round(
                        names,
                        3,
                    ),
            },
        )


# ============================================================
# NAME SIMILARITY
# ============================================================

def name_similarity(
    left: list[str],
    right: list[str],
) -> float:
    """
    Calcula similitud Jaccard entre tokens de nombres.

    Se mantiene únicamente para el comparador legacy
    de SkinSignature.

    NO forma parte del StructuralSignature score.
    """

    def tokens(values):

        return {
            token
            for value in values
            for token in (
                value
                .lower()
                .replace(
                    "_",
                    " ",
                )
                .split()
            )
            if len(token) > 2
            and not token.isdigit()
        }

    a = tokens(left)
    b = tokens(right)

    if not a and not b:
        return 0.0

    return (
        len(a & b)
        /
        len(a | b)
    )


# ============================================================
# LEGACY GEOMETRY SCORE
# ============================================================

def _geometry_score(
    query: GeometrySignature,
    reference: GeometrySignature,
) -> tuple[float, dict]:
    """
    Comparador geométrico antiguo.

    Se conserva para no romper el código existente.
    """

    if (
        not query.aspect_signature
        or not reference.aspect_signature
        or not query.shape_histogram
        or not reference.shape_histogram
    ):
        return (
            0.0,
            {
                "reason":
                    "No hay geometría suficiente "
                    "para comparar."
            },
        )

    query_aspect = np.asarray(
        query.aspect_signature,
        dtype=float,
    )

    reference_aspect = np.asarray(
        reference.aspect_signature,
        dtype=float,
    )

    aspect_distance = float(
        np.linalg.norm(
            query_aspect
            -
            reference_aspect
        )
    )

    aspect_similarity = math.exp(
        -aspect_distance
    )

    query_histogram = np.asarray(
        query.shape_histogram,
        dtype=float,
    )

    reference_histogram = np.asarray(
        reference.shape_histogram,
        dtype=float,
    )

    shape_distance = float(
        np.linalg.norm(
            query_histogram
            -
            reference_histogram
        )
    )

    shape_similarity = math.exp(
        -shape_distance
    )

    score = 100.0 * (
        0.35 * aspect_similarity
        + 0.65 * shape_similarity
    )

    return (
        score,
        {
            "shape_aspect_distance":
                round(
                    aspect_distance,
                    4,
                ),

            "surface_distance":
                round(
                    shape_distance,
                    4,
                ),

            "aspect_similarity":
                round(
                    aspect_similarity,
                    4,
                ),

            "shape_similarity":
                round(
                    shape_similarity,
                    4,
                ),
        },
    )