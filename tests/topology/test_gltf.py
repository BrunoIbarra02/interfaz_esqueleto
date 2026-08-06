"""
=========================================================
Nombre: test_gltf.py

Objetivo:
    Comprender la estructura interna de un archivo GLB
    utilizando pygltflib.

Documento asociado:
    docs/03_gltf.md

Estado:
    Completado
=========================================================
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import tests.topology.common as common

from pygltflib import GLTF2

TEST_GLTF = Path(__file__).parent / "glb" / "oso_polar.glb"

################################################
# UTILIDADES
################################################

def get_gltf():
    """
    Carga un archivo GLTF de prueba.
    """
    return GLTF2().load(str(TEST_GLTF))
################################################
# RESUMEN
################################################

def test_summary():
    """
    Muestra un resumen de la estructura del GLB.
    """

    gltf = get_gltf()

    common.print_title("Resumen")

    print(f"Scenes       : {len(gltf.scenes)}")
    print(f"Nodes        : {len(gltf.nodes)}")
    print(f"Meshes       : {len(gltf.meshes)}")
    print(f"Skins        : {len(gltf.skins)}")
    print(f"Animations   : {len(gltf.animations)}")
    print(f"Materials    : {len(gltf.materials)}")
    print(f"Textures     : {len(gltf.textures)}")
    print(f"Images       : {len(gltf.images)}")
    print(f"Accessors    : {len(gltf.accessors)}")
    print(f"BufferViews  : {len(gltf.bufferViews)}")
    print(f"Buffers      : {len(gltf.buffers)}")



################################################
# NODES
################################################

def test_nodes():
    gltf = get_gltf()

    common.print_title("Nodes")

    for i, node in enumerate(gltf.nodes):
        print(f"Node {i}")
        print(node)
        print()

################################################
# MESHES
################################################

def test_meshes():
    gltf = get_gltf()

    common.print_title("Meshes")

    for i, mesh in enumerate(gltf.meshes):
        print(f"Mesh {i}")
        print(mesh)
        print()

################################################
# ACCESSORS
################################################

def test_accessors():
    """
    Inspecciona los accessors del GLB.
    """

    gltf = get_gltf()

    common.print_title("ACCESSORS")

    for i, accessor in enumerate(gltf.accessors):

        print(f"Accessor {i}")
        print(f"Type         : {accessor.type}")
        print(f"Component    : {accessor.componentType}")
        print(f"Count        : {accessor.count}")
        print(f"Buffer View  : {accessor.bufferView}")
        print(f"Byte Offset  : {accessor.byteOffset}")
        print(f"Normalized   : {accessor.normalized}")

        if accessor.min is not None:
            print(f"Min          : {accessor.min}")

        if accessor.max is not None:
            print(f"Max          : {accessor.max}")

        print()

################################################
# BUFFERS
################################################

def test_buffer_views():
    """
    Inspecciona los BufferViews del GLB.
    """

    gltf = get_gltf()

    common.print_title("Buffer Views")

    for i, view in enumerate(gltf.bufferViews):

        print(f"BufferView {i}")
        print(f"Buffer      : {view.buffer}")
        print(f"Byte Offset : {view.byteOffset}")
        print(f"Byte Length : {view.byteLength}")
        print(f"Byte Stride : {view.byteStride}")
        print(f"Target      : {view.target}")

        print()
        
def test_buffers():
    """
    Inspecciona los buffers del GLB.
    """

    gltf = get_gltf()

    common.print_title("Buffers")

    for i, buffer in enumerate(gltf.buffers):

        print(f"Buffer {i}")
        print(f"Byte Length : {buffer.byteLength}")
        print(f"URI         : {buffer.uri}")

        print()
        
################################################
# IMAGES
################################################

def test_images():
    """
    Inspecciona las imágenes del GLB.
    """

    gltf = get_gltf()

    common.print_title("Images")

    for i, image in enumerate(gltf.images):

        print(f"Image {i}")
        print(image)
        print()

################################################
# TEXTURES
################################################

def test_textures():
    """
    Inspecciona las texturas del GLB.
    """

    gltf = get_gltf()

    common.print_title("Textures")

    for i, texture in enumerate(gltf.textures):

        print(f"Texture {i}")
        print(texture)
        print()

################################################
# SCENES
################################################

def test_scenes():
    """
    Inspecciona las escenas del GLB.
    """

    gltf = get_gltf()

    common.print_title("Scenes")

    for i, scene in enumerate(gltf.scenes):

        print(f"Scene {i}")
        print(scene)
        print()

################################################
# MATERIALS
################################################

def test_materials():
    """
    Inspecciona los materiales del GLB.
    """

    gltf = get_gltf()

    common.print_title("Materials")

    for i, material in enumerate(gltf.materials):

        print(f"Material {i}")
        print(material)
        print()

def main():
    
    # test_summary()
    # test_nodes()
    # test_meshes()
    # test_accessors()
    # test_buffer_views()
    # test_buffers()
    # test_images()
    # test_textures()
    # test_scenes()
    # test_materials()
    pass


if __name__ == "__main__":
    main()