#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
from itertools import permutations, product
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

import assimp_py


def load_asset(path: Path) -> dict:
    flags = (
        assimp_py.Process_Triangulate
        | assimp_py.Process_JoinIdenticalVertices
    )

    scene = assimp_py.import_file(
        str(path),
        flags,
    )

    clouds = []

    for mesh in scene.meshes:
        if not len(mesh.vertices):
            continue

        vertices = (
            np.asarray(
                mesh.vertices,
                dtype=np.float32,
            )
            .reshape(-1, 3)
            .astype(float)
        )

        clouds.append(vertices)

    if not clouds:
        raise ValueError(
            f"{path.name}: Assimp found no mesh vertices"
        )

    bones = [
        bone.name
        for mesh in scene.meshes
        for bone in (
            getattr(
                mesh,
                "bones",
                None,
            )
            or []
        )
    ]

    return {
        "vertices": np.vstack(clouds),
        "bone_names": sorted(set(bones)),
    }


def canonical_variants(
    vertices: np.ndarray,
    samples: int,
) -> list[np.ndarray]:
    """
    PCA-normaliza una nube y genera las 48 posibles
    orientaciones derivadas de permutaciones y signos
    de los ejes PCA.
    """

    centered = (
        vertices
        - vertices.mean(axis=0)
    )

    _, _, basis = np.linalg.svd(
        centered,
        full_matrices=False,
    )

    points = (
        centered
        @ basis.T
    )

    points /= max(
        np.linalg.norm(
            np.ptp(
                points,
                axis=0,
            )
        ),
        1e-9,
    )

    if len(points) > samples:
        step = max(
            1,
            len(points) // samples,
        )

        points = points[
            ::step
        ][:samples]

    return [
        points[:, axes]
        * np.asarray(
            signs,
            dtype=float,
        )
        for axes in permutations(range(3))
        for signs in product(
            (-1, 1),
            repeat=3,
        )
    ]


def chamfer(
    a: np.ndarray,
    b: np.ndarray,
) -> float:

    distance_ab = cKDTree(a).query(
        b,
        workers=-1,
    )[0].mean()

    distance_ba = cKDTree(b).query(
        a,
        workers=-1,
    )[0].mean()

    return float(
        (
            distance_ab
            + distance_ba
        )
        / 2
    )


def mesh_score(
    query_variants: list[np.ndarray],
    reference_variants: list[np.ndarray],
) -> tuple[float, float]:

    reference = reference_variants[0]

    distance = min(
        chamfer(
            query,
            reference,
        )
        for query in query_variants
    )

    score = (
        100
        * math.exp(
            -35 * distance
        )
    )

    return score, distance


def token_similarity(
    a: list[str],
    b: list[str],
) -> float:

    def words(values):

        return {
            word
            for value in values
            for word in (
                value
                .lower()
                .replace("_", " ")
                .split()
            )
            if len(word) > 2
            and not word.isdigit()
        }

    left = words(a)
    right = words(b)

    if not left and not right:
        return 0.0

    return len(
        left & right
    ) / len(
        left | right
    )


def main() -> int:

    parser = argparse.ArgumentParser(
        description=__doc__,
    )

    parser.add_argument(
        "glb",
        type=Path,
    )

    parser.add_argument(
        "--reference-dir",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "assimp_match.json"
        ),
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=2500,
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # QUERY
    # --------------------------------------------------------

    print(
        f"Loading GLB: {args.glb}"
    )

    query = load_asset(
        args.glb
    )

    print(
        "GLB vertices:",
        len(
            query["vertices"]
        ),
    )

    print(
        "GLB bones:",
        len(
            query["bone_names"]
        ),
    )

    query_variants = canonical_variants(
        query["vertices"],
        args.samples,
    )

    # --------------------------------------------------------
    # REFERENCES
    # --------------------------------------------------------

    references = {
        path.resolve()
        for path in args.reference_dir.glob(
            "*.FBX"
        )
    }

    references.update(
        path.resolve()
        for path in args.reference_dir.glob(
            "*.fbx"
        )
    )

    ranked = []

    for fbx in sorted(
        references
    ):

        print(
            f"Comparing: {fbx.name}"
        )

        reference = load_asset(
            fbx
        )

        reference_variants = canonical_variants(
            reference["vertices"],
            args.samples,
        )

        mesh, distance = mesh_score(
            query_variants,
            reference_variants,
        )

        bones = token_similarity(
            query["bone_names"],
            reference["bone_names"],
        )

        if query["bone_names"]:
            score = (
                0.8 * mesh
                + 20 * bones
            )
        else:
            score = mesh

        ranked.append(
            {
                "skeleton": fbx.name,
                "score": round(
                    score,
                    2,
                ),
                "mesh_distance": round(
                    distance,
                    7,
                ),
                "bone_name_similarity": round(
                    bones,
                    4,
                ),
            }
        )

    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    if not ranked:
        raise ValueError(
            "No se encontraron FBX de referencia."
        )

    result = {
        "input": str(
            args.glb
        ),
        "input_has_skin": bool(
            query["bone_names"]
        ),
        "selection": ranked[0][
            "skeleton"
        ],
        "confidence": ranked[0][
            "score"
        ],
        "ranked_matches": ranked,
    }

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "========================================"
    )
    print(
        "RANKING"
    )
    print(
        "========================================"
    )

    for index, item in enumerate(
        ranked,
        start=1,
    ):

        print(
            f"{index:2}. "
            f"{item['skeleton']:24} "
            f"score={item['score']:6.2f} "
            f"distance={item['mesh_distance']:.7f}"
        )

    print()
    print(
        f"SELECTION: {result['selection']}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
