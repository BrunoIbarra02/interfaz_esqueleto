import bbox
import inspect
import trimesh
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import topology.common as common

TEST_GLB = "tests/topology/glb/oso_polar.glb"

#####################################
# APIS
#####################################

def test_bbox_api():


    common.print_title("BBox API")


    print(dir(bbox))
    
def test_bbox3d_api():
    
    common.print_title("BBox3D API")


    print(dir(bbox.BBox3D))
    
def test_bbox3d_constructor():
    """
    Inspecciona el constructor de BBox3D.
    """

    common.print_title("Constructor BBox3D")


    print(inspect.signature(bbox.BBox3D))

    print()

    print(bbox.BBox3D.__doc__)
    
def test_bbox3d():
    """
    Crea una caja 3D de ejemplo e inspecciona sus propiedades.
    """

    box = bbox.BBox3D(
        x=0,
        y=0,
        z=0,
        length=2,
        width=3,
        height=4,
    )

    common.print_title("BBox3D")

    print(box)
    print()

    print(f"Centro     : {box.center}")
    print(f"Length     : {box.length}")
    print(f"Width      : {box.width}")
    print(f"Height     : {box.height}")
    print(f"Quaternion : {box.quaternion}")


######################################
# VERTICES
######################################

def test_bbox3d_vertices():
    """
    Inspecciona los ocho vértices de la Bounding Box.
    """

    box = bbox.BBox3D(
        x=0,
        y=0,
        z=0,
        length=2,
        width=3,
        height=4,
    )

    common.print_title("Vertices")

    for i in range(1, 9):
        point = getattr(box, f"p{i}")
        print(f"p{i} : {point}")
        
######################################
# METHODS
######################################

def test_bbox3d_methods():
    """
    Inspecciona los métodos públicos de BBox3D.
    """


    common.print_title("Métodos BBox3D")

    for name in sorted(dir(bbox.BBox3D)):

        if name.startswith("_"):
            continue

        member = getattr(bbox.BBox3D, name)

        if callable(member):
            print(name)
            
######################################
# TRIMESH
######################################

def test_trimesh_bounding_box():
    """
    Inspeciona la Bounding Box de un modelo 3D cargado con Trimesh.
    """
    
    mesh = common.get_mesh()
    

    common.print_title("Trimesh Bounding Box")
    
    print(type(mesh.bounding_box))
    
    print()
    
    print(mesh.bounding_box)
    
def test_trimesh_bounding_box_api():
    """
    Inspecciona la API de trimesh.primitives.Box.
    """

    mesh = common.get_mesh()

    box = mesh.bounding_box


    common.print_title("API Box")


    print(dir(box))
    
def test_trimesh_bounding_box_properties():
    """
    Inspecciona las propiedades principales de la Bounding Box.
    """

    mesh = common.get_mesh()
    box = mesh.bounding_box_oriented

    common.print_title("Propiedades")

    print(f"Bounds    : {box.bounds}")
    print(f"Centroid  : {box.centroid}")
    print(f"Extents   : {box.extents}")
    print(f"Volume    : {box.volume}")
    print(f"Transform :\n{box.transform}")
    
##################################################
# PRIMITIVE
##################################################
    
def test_trimesh_box_primitive():
    """
    Inspecciona el primitive asociado a la Box.
    """

    mesh = common.get_mesh()

    box = mesh.bounding_box_oriented


    common.print_title("Primitive")


    print(type(box.primitive))
    print()
    print(dir(box.primitive))

def test_trimesh_box_primitive_values():
    """
    Compara los valores de Box y Primitive.
    """

    mesh = common.get_mesh()

    box = mesh.bounding_box_oriented
    
    common.print_title("Primitive Values")

    print("Box extents")
    print(box.extents)

    print()

    print("Primitive extents")
    print(box.primitive.extents)

    print()

    print("Box transform")
    print(box.transform)
    
    print()

    print("Vertices")
    print(box.vertices)

    print()

    print("Min")
    print(box.vertices.min(axis=0))

    print()

    print("Max")
    print(box.vertices.max(axis=0))

    print()

    print("Max - Min")
    print(box.vertices.max(axis=0) - box.vertices.min(axis=0))

    print()

    print("Primitive transform")
    print(box.primitive.transform)
    
def inspect_primitive_extents():
    
    
    mesh = common.get_mesh()

    box = mesh.bounding_box_oriented
    
    
    common.print_title("Primitive extents")
    
    print(inspect.getsource(type(box.primitive)))
    
def inspect_box_properties_extended():
    
    mesh = common.get_mesh()

    box = mesh.bounding_box_oriented
    

    common.print_title("Box extents")

    
    print(inspect.getsource(type(box).extents.fget))

def main():
    #test_bbox_api()
    #test_bbox3d_api()
    #test_bbox3d_constructor()
    #test_bbox3d()
    #test_bbox3d_vertices()
    #test_bbox3d_methods()
    #test_trimesh_bounding_box()
    #test_trimesh_bounding_box_api()
    #test_trimesh_bounding_box_properties()
    #test_trimesh_box_primitive()
    #test_trimesh_box_primitive_values()
    #inspect_primitive_extents()
    inspect_box_properties_extended()

if __name__ == "__main__":
    main()