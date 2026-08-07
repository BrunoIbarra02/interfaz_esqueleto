from pathlib import Path
import sys
import copy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import tests.topology.common as common

from topology.comparator import SkeletonComparator
from topology.features import extract_features

from test_bones import build_bone_tree

def test_comparator():
    
      
    mesh = common.get_mesh()

    root = build_bone_tree()

    features_a = extract_features(mesh, root)

    features_b = copy.deepcopy(features_a)

    features_b.branch_length_mean *= 1.10

    comparator = SkeletonComparator()
    
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