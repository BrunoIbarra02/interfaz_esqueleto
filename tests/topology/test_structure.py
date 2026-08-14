"""
test_structure.py

Prueba la representación estructural de esqueletos GLB y FBX.

GLB:
    load_mesh()
        ->
    fix_mesh()
        ->
    generate_skeleton()
        ->
    build_bone_forest()
        ->
    build_forest_structure()

FBX:
    load_fbx_skeleton()
        ->
    build_bone_tree()
        ->
    build_structure()
"""

from pathlib import Path
import sys
import trimesh

import networkx as nx


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from topology.preprocess import (
    load_mesh,
    validate_mesh,
    fix_mesh,
)

from topology.skeletonize import (
    generate_skeleton,
)

from topology.bone import (
    build_bone_tree,
    build_bone_forest,
)

from topology.structure import (
    build_structure,
    build_forest_structure,
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
# STRUCTURE INSPECTION
# ============================================================

def inspect_structure(
    name,
    structure,
):
    """
    Muestra una SkeletonStructure.
    """

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    print(
        f"Landmarks : "
        f"{structure.landmark_count}"
    )

    print(
        f"Segments  : "
        f"{structure.segment_count}"
    )

    for index, segment in enumerate(
        structure.segments,
        start=1,
    ):

        print()

        print(
            f"Segment {index}"
        )

        print(
            f"  Start     : "
            f"{segment.start.bone}"
        )

        print(
            f"  End       : "
            f"{segment.end.bone}"
        )

        print(
            f"  Bones     : "
            f"{segment.bone_count}"
        )

        print(
            f"  Length    : "
            f"{segment.length:.6f}"
        )

        print(
            f"  Direction : "
            f"{segment.direction}"
        )


# ============================================================
# SKELETON COMPONENTS
# ============================================================

def inspect_skeleton_components(
    skeleton,
):
    """
    Muestra las componentes conectadas del Skeleton.
    """

    graph = skeleton.get_graph()

    components = list(
        nx.connected_components(
            graph.to_undirected()
        )
    )

    component_sizes = sorted(
        (
            len(component)
            for component in components
        ),
        reverse=True,
    )

    print()
    print("=" * 60)
    print("GLB Skeleton Components")
    print("=" * 60)

    print(
        f"Components : "
        f"{len(component_sizes)}"
    )

    print(
        f"Largest    : "
        f"{component_sizes[:20]}"
    )


# ============================================================
# GLB
# ============================================================

def test_glb_structure():

    glb_path = (
        GLB_DIR
        / "oso_polar.glb"
    )

    # --------------------------------------------------------
    # Load mesh
    # --------------------------------------------------------

    mesh = load_mesh(
        str(glb_path)
    )

    validate_mesh(
        mesh
    )

    print()
    print("=" * 60)
    print("GLB Mesh")
    print("=" * 60)

    print(
        f"Vertices : "
        f"{len(mesh.vertices)}"
    )

    print(
        f"Faces    : "
        f"{len(mesh.faces)}"
    )

    print(
        f"Watertight : "
        f"{mesh.is_watertight}"
    )

    print(
        f"Winding consistent : "
        f"{mesh.is_winding_consistent}"
    )

    print(
        f"Empty : "
        f"{mesh.is_empty}"
    )

    # --------------------------------------------------------
    # Historical Skeletor preprocessing
    # --------------------------------------------------------

    mesh = fix_mesh(
        mesh
    )
    
    export_fixed_mesh(
        mesh,
        PROJECT_ROOT
        / "tests"
        / "topology"
        / "outputs"
        / "oso_polar_fixed.glb",
    )

    print()
    print("=" * 60)
    print("GLB Mesh After fix_mesh")
    print("=" * 60)

    print(
        f"Vertices : "
        f"{len(mesh.vertices)}"
    )

    print(
        f"Faces    : "
        f"{len(mesh.faces)}"
    )

    print(
        f"Watertight : "
        f"{mesh.is_watertight}"
    )

    print(
        f"Winding consistent : "
        f"{mesh.is_winding_consistent}"
    )

    print(
        f"Empty : "
        f"{mesh.is_empty}"
    )

    # --------------------------------------------------------
    # TEASAR
    # Historical configuration:
    # inv_dist = 0.1
    # --------------------------------------------------------

    skeleton = generate_skeleton(
        mesh,
        sampling_dist=0.1,
    )
    
    export_largest_components(
        skeleton,
        PROJECT_ROOT / "tests" / "topology" / "outputs",
    )

    print()
    print("=" * 60)
    print("GLB Skeleton")
    print("=" * 60)

    print(
        f"Type    : "
        f"{type(skeleton)}"
    )

    print(
        f"Vertices: "
        f"{len(skeleton.vertices)}"
    )

    print(
        f"Edges   : "
        f"{len(skeleton.edges)}"
    )

    print(
        f"Roots   : "
        f"{len(skeleton.roots)}"
    )

    print(
        f"Leafs   : "
        f"{len(skeleton.leafs)}"
    )

    # --------------------------------------------------------
    # Components
    # --------------------------------------------------------

    inspect_skeleton_components(
        skeleton
    )

    # --------------------------------------------------------
    # Bone Forest
    # --------------------------------------------------------

    forest = build_bone_forest(
        skeleton
    )

    print()
    print("=" * 60)
    print("GLB Bone Forest")
    print("=" * 60)

    print(
        f"Roots : "
        f"{len(forest)}"
    )

    print(
        f"First roots : "
        f"{forest[:10]}"
    )

    assert len(forest) == len(
        skeleton.roots
    )

    # --------------------------------------------------------
    # Forest Structure
    # --------------------------------------------------------

    forest_structure = (
        build_forest_structure(
            forest
        )
    )
    
    inspect_forest(
        forest
    )

    print()
    print("=" * 60)
    print("GLB Forest Structure")
    print("=" * 60)

    print(
        f"Trees     : "
        f"{forest_structure.root_count}"
    )

    print(
        f"Landmarks : "
        f"{forest_structure.landmark_count}"
    )

    print(
        f"Segments  : "
        f"{forest_structure.segment_count}"
    )

    assert (
        forest_structure.root_count
        == len(forest)
    )


# ============================================================
# FBX
# ============================================================

def test_fbx_structure():

    fbx_path = (
        FBX_DIR
        / "Bear.FBX"
    )

    # --------------------------------------------------------
    # Load FBX skeleton
    # --------------------------------------------------------

    root = load_fbx_skeleton(
        str(fbx_path)
    )

    assert root is not None
    assert root.parent is None

    # --------------------------------------------------------
    # Structure
    # --------------------------------------------------------

    structure = build_structure(
        root
    )

    print()
    print("=" * 60)
    print("FBX Structure")
    print("=" * 60)

    print(
        f"Landmarks : "
        f"{structure.landmark_count}"
    )

    print(
        f"Segments  : "
        f"{structure.segment_count}"
    )

    assert (
        structure.landmark_count > 0
    )

    assert (
        structure.segment_count > 0
    )

    for index, segment in enumerate(
        structure.segments,
        start=1,
    ):

        print()

        print(
            f"Segment {index}"
        )

        print(
            f"  Start     : "
            f"{segment.start.bone}"
        )

        print(
            f"  End       : "
            f"{segment.end.bone}"
        )

        print(
            f"  Bones     : "
            f"{segment.bone_count}"
        )

        print(
            f"  Length    : "
            f"{segment.length:.6f}"
        )

        print(
            f"  Direction : "
            f"{segment.direction}"
        )

def inspect_forest(
    forest,
):
    """
    Muestra estadísticas de cada árbol del bosque.
    """

    rows = []

    for index, root in enumerate(forest):

        bone_count = 0

        def count_bones(bone):
            nonlocal bone_count

            bone_count += 1

            for child in bone.children:
                count_bones(child)

        count_bones(root)

        structure = build_structure(root)

        rows.append(
            (
                index,
                root.node_id,
                bone_count,
                structure.landmark_count,
                structure.segment_count,
                sum(
                    segment.length
                    for segment in structure.segments
                ),
                root.position,
            )
        )

    rows.sort(
        key=lambda row: row[2],
        reverse=True,
    )

    print()
    print("=" * 60)
    print("GLB Forest Statistics")
    print("=" * 60)

    print(
        f"{'Tree':>5} "
        f"{'Root':>6} "
        f"{'Bones':>7} "
        f"{'Landmarks':>10} "
        f"{'Segments':>9} "
        f"{'Length':>12} "
        f"{'Root Position'}"
    )

    for (
        index,
        root_id,
        bones,
        landmarks,
        segments,
        length,
        position,
    ) in rows:

        print(
            f"{index:>5} "
            f"{root_id:>6} "
            f"{bones:>7} "
            f"{landmarks:>10} "
            f"{segments:>9} "
            f"{length:>12.6f} "
            f"{position}"
        )
        
def export_largest_components(
    skeleton,
    output_dir,
    count=5,
):
    """
    Exporta los componentes más grandes del Skeleton
    como nubes de puntos PLY.
    """

    graph = skeleton.get_graph()

    components = list(
        nx.connected_components(
            graph.to_undirected()
        )
    )

    components.sort(
        key=len,
        reverse=True,
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("=" * 60)
    print("Export Largest Skeleton Components")
    print("=" * 60)

    for index, component in enumerate(
        components[:count],
        start=1,
    ):

        node_ids = list(component)

        points = skeleton.vertices[
            node_ids
        ]

        cloud = trimesh.points.PointCloud(
            points
        )

        output_path = (
            output_dir
            / f"skeleton_component_{index}.ply"
        )

        cloud.export(
            output_path
        )

        print(
            f"Component {index}: "
            f"{len(node_ids)} nodes -> "
            f"{output_path}"
        )

def export_fixed_mesh(
    mesh,
    output_path,
):
    """
    Exporta la malla resultante de fix_mesh()
    para inspección visual.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    mesh.export(
        output_path
    )

    print()
    print("=" * 60)
    print("Fixed Mesh Export")
    print("=" * 60)

    print(
        f"Output : {output_path}"
    )

# ============================================================
# MAIN
# ============================================================

def main():

    test_glb_structure()

    test_fbx_structure()


if __name__ == "__main__":
    main()