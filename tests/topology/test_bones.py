from pathlib import Path
import sys
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import tests.topology.common as common
from topology.bone import Bone,get_root_to_leaf_paths

####################################
# FUNCTIONS
####################################

def walk_lengths(bone,lengths):
    """
    Recorre la jerarquia y calcula la longitud de cada hueso.
    """
    
    for child in bone.children:
        
        length = np.linalg.norm(
            child.position - bone.position
        )
        
        lengths.append(length)

        print(f"{bone} -> {child} = {length:.6f}")

        walk_lengths(child, lengths)
    
    

def walk_bones(bone):
    
    count = 1
    
    
    for child in bone.children:
        count += walk_bones(child)
        
    return count
        
    print(f"Bones recorridos: {count}")
        
def build_bone_tree():
    """
    Construye una jerarquía de Bone a partir del árbol de NetworkX.

    Returns
    -------
    Bone
        Hueso raíz del árbol.
    """
    
    skeleton = common.get_skeleton()
    
    graph = skeleton.get_graph().reverse(copy=False)

    swc = skeleton.swc
    
    #Creamos diccionario de posiciones
    positions = {}
    
    for _, row in swc.iterrows():
        
        positions[row.node_id] = np.array(
            [
                row.x,
                row.y,
                row.z,
            ],
            dtype=float,
        )
    

    # Crear todos los Bone
    bones = {}

    for node in graph.nodes():
        bones[node] = Bone(
            node,
            positions[node]
            )

    # Conectar padres e hijos
    for parent_id, child_id in graph.edges():

        parent = bones[parent_id]
        child = bones[child_id]

        parent.children.append(child)
        child.parent = parent

    # Buscar la raíz
    root = next(
        node
        for node, indegree in graph.in_degree()
        if indegree == 0
    )

    return bones[root]

#####################################
# TESTS
#####################################

def test_bone():
    """
    Crea un bone e inspecciona su estructura
    """
    
    bone = Bone(0)
    
    common.print_title("Bone")
    
    print(type(bone))
    
    print()
    
    print(bone)
    
    print()
    
    print(bone.__dict__)
    
def test_bone_tree():
    
    root = Bone(0)
    
    child1 = Bone(1)
    child2 = Bone(2)
    
    root.children.append(child1)
    root.children.append(child2)
    
    child1.parent = root
    child2.parent = root
    
    common.print_title("Bone Tree")
    
    print(root)
    
    print()
    
    print("Children:")
    print(root.children)
    
    print()
    
    print(f"{child1} -> parent = {child1.parent}")
    print(f"{child2} -> parent = {child2.parent}")
    
def test_build_bone_tree():
    """
    Convierte el árbol de NetworkX en jerarquia de Bone
    """
    root_bone = build_bone_tree()    

    common.print_title("Bone Tree")
    print(f"Root: {root_bone}")
    
    print()
    print("Children:")
    print(root_bone.children)
    
def test_walk_bones():
    
    root_bone = build_bone_tree()
    
    common.print_title("Bone DFS")
    
    count = walk_bones(root_bone)
    
    print(f"Huesos recorridos: {count}")
    
def test_bone_positions():
    
    root = build_bone_tree()
    
    common.print_title("Bone Position")
    
    print(root)
    
    print(root.position)
    
    print()
    
    for child in root.children:
        print(child)
        print(child.position)
        
def test_bone_lengths():
    """
    Calcula estadísticas de la longitud de los huesos.
    """

    root = build_bone_tree()

    lengths = []

    common.print_title("Bone Lengths")

    walk_lengths(root, lengths)

    print()

    print(f"Número de huesos : {len(lengths)}")
    print(f"Mínimo           : {min(lengths):.6f}")
    print(f"Máximo           : {max(lengths):.6f}")
    print(f"Media            : {np.mean(lengths):.6f}")
    
    print()

    print("5 más cortos:")
    print(sorted(lengths)[:5])

    print()

    print("5 más largos:")
    print(sorted(lengths)[-5:])
    
def test_root_to_leaf_paths():

    common.print_title("Root To Leaf Paths")

    root = build_bone_tree()

    paths = get_root_to_leaf_paths(root)

    for i, path in enumerate(paths):

        print(f"Path {i + 1}")

        for bone in path:
            print(bone)

        print()
    
    
def main():
    
    #test_bone()
    #test_bone_tree()
    #test_build_bone_tree()
    #test_walk_bones()
    #test_bone_positions()
    #test_bone_lengths()
    test_root_to_leaf_paths()
    
if __name__ == "__main__":
    main()