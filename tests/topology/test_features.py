from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import tests.topology.common as common
from topology.features import extract_features

from test_bones import build_bone_tree


def test_topology():
    
    mesh = common.get_mesh()

    root = build_bone_tree()

    features = extract_features(mesh,root)

    common.print_title("Topology Features")

    print(features)

    print("Bone Length Std")
    print(features.bone_length_std)
    


def main():
    test_topology()
    
if __name__ == "__main__":
    main()