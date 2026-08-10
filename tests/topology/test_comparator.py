from pathlib import Path
import sys
import copy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import tests.topology.common as common

from topology.comparator import SkeletonComparator
from topology.features import extract_features

from test_bones import build_bone_tree

#############################################
# VARIABLES
#############################################

GLB_A = common.PROJECT_ROOT / "tests" / "topology" / "glb" / "oso_pardo.glb"
GLB_B = common.PROJECT_ROOT / "tests" / "topology" / "glb" / "Eagle.glb"

def test_comparator():
    
    mesh_a = common.get_mesh(GLB_A)
    mesh_b = common.get_mesh(GLB_B)

    root_a = build_bone_tree(GLB_A)
    root_b = build_bone_tree(GLB_B)

    features_a = extract_features(mesh_a, root_a)

    features_b = extract_features(mesh_b,root_b)

    comparator = SkeletonComparator()
    print("A:")
    print(features_a)

    print()
    print("B:")
    print(features_b)

    print()
    print("Topology :", comparator.compare_topology(features_a, features_b))
    print("Geometry :", comparator.compare_geometry(features_a, features_b))
    print("Branches :", comparator.compare_branches(features_a, features_b))
    print("BBox     :", comparator.compare_bbox(features_a, features_b))
    
    
    score = comparator.compare(
        features_a,
        features_b,
    )
    
    common.print_title("Comparator")
    
    print(score)
    
def main():
    
    test_comparator()
    
if __name__ == "__main__":
    main()