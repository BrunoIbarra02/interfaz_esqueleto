"""
=========================================================
Test: Skeletonize

Objetivo:
    Evaluar el proceso completo de skeletonización,
    incluyendo el preprocesado de la malla mediante
    Trimesh/fix_mesh y la comparación de los algoritmos
    disponibles en Skeletor.

Documentos asociados:
    - docs/01_trimesh.md
    - docs/02_skeletor.md

Estado:
    Completado
=========================================================
"""
from pathlib import Path
import sys
import skeletor


################################################
# CONSTANTES
################################################

TEST_GLB = Path(__file__).parent / "glb" / "oso_polar.glb"
OUTPUT_DIR = Path(__file__).parent / "output"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from topology.preprocess import load_mesh

################################################
# UTILIDADES
################################################

def get_vertex_cluster_skeleton():
    """
    Genera un Skeleton de prueba a partir del GLB de oso polar.
    """

    glb_path = TEST_GLB

    mesh = get_fixed_mesh()

    return skeletor.skeletonize.by_vertex_clusters(
        mesh,
        sampling_dist=0.05,
    )

def get_fixed_mesh():
    """
    Carga y preprocesa la mmalla de prueba
    """
    
    glb_path = TEST_GLB

    mesh = load_mesh(str(glb_path))

    return skeletor.pre.fix_mesh(
        mesh,
        remove_disconnected=5,
        inplace=False,
    )
    
def print_skeleton_stats(name, skeleton):
    """
    Muestra información básica de un Skeleton.
    """

    print("=" * 60)
    print(name)
    print("=" * 60)

    print(f"Tipo       : {type(skeleton).__name__}")
    print(f"Vértices   : {len(skeleton.vertices)}")
    print(f"Aristas    : {len(skeleton.edges)}")
    print(f"Raíces     : {len(skeleton.roots)}")
    print(f"Hojas      : {len(skeleton.leafs)}")
    
    print()
    print(skeleton)

def export_skeleton(name, skeleton):
    """
    Exporta un Skeleton a un archivo GLB.
    """

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / f"{name}.glb"
    
    scene = skeleton.scene()
    scene.export(output_file)

    print("=" * 60)
    print(f"Exportación : {name}")
    print("=" * 60)

    print(f"Archivo : {output_file}")
    print(f"Existe  : {output_file.exists()}")



################################################
# EVALUACIÓN VERTEX CLUSTER
################################################

def test_vertex_cluster():
    """
    Genera un Skeleton y muestra información básica.
    """

    skeleton = get_vertex_cluster_skeleton()

    print_skeleton_stats("Vertex Cluster", skeleton)
    export_skeleton("skeleton_vertex_cluster", skeleton)

#################################################
# EVALUACIÓN FIX MESH
#################################################

def test_fix_mesh():
    """
    Evalúa el comportamiento de fix_mesh sobre una malla.
    """

    glb_path = TEST_GLB

    mesh = load_mesh(str(glb_path))

    print_skeleton_stats("Malla original", mesh)

    fixed_mesh = get_fixed_mesh()

    print(f"Tipo        : {type(mesh).__name__}")
    print(f"Vertices    : {len(mesh.vertices)}")
    print(f"Caras       : {len(mesh.faces)}")
    print(f"Watertight  : {mesh.is_watertight}")

    fixed_mesh = get_fixed_mesh()

    print()

    print("=" * 60)
    print("Malla reparada")
    print("=" * 60)

    print(f"Tipo        : {type(fixed_mesh).__name__}")
    print(f"Vertices    : {len(fixed_mesh.vertices)}")
    print(f"Caras       : {len(fixed_mesh.faces)}")
    print(f"Watertight  : {fixed_mesh.is_watertight}")
    
def test_fix_mesh_vs_original():
    """
    Compara la skeletonización con y sin fix_mesh.
    """

    glb_path = TEST_GLB

    mesh = load_mesh(str(glb_path))

    print("=" * 60)
    print("Skeleton original")
    print("=" * 60)

    skeleton_original = skeletor.skeletonize.by_vertex_clusters(
        mesh,
        sampling_dist=0.05,
    )

    print(f"Vértices : {len(skeleton_original.vertices)}")
    print(f"Aristas  : {len(skeleton_original.edges)}")
    print(f"Raíces   : {len(skeleton_original.roots)}")
    print(f"Hojas    : {len(skeleton_original.leafs)}")

    print()

    print("=" * 60)
    print("Skeleton con fix_mesh")
    print("=" * 60)

    fixed_mesh = get_fixed_mesh()

    skeleton_fixed = skeletor.skeletonize.by_vertex_clusters(
        fixed_mesh,
        sampling_dist=0.05,
    )

    print(f"Vértices : {len(skeleton_fixed.vertices)}")
    print(f"Aristas  : {len(skeleton_fixed.edges)}")
    print(f"Raíces   : {len(skeleton_fixed.roots)}")
    print(f"Hojas    : {len(skeleton_fixed.leafs)}")

def test_fix_mesh_export():
    """
    Exporta el Skeleton generado con y sin fix_mesh para su comparación visual.
    """

    glb_path = TEST_GLB

    OUTPUT_DIR.mkdir(exist_ok=True)

    mesh = load_mesh(str(glb_path))

    # --------------------------------------------------
    # Skeleton original
    # --------------------------------------------------

    skeleton_original = skeletor.skeletonize.by_vertex_clusters(
        mesh,
        sampling_dist=0.05,
    )

    scene_original = skeleton_original.scene()

    original_file = OUTPUT_DIR / "skeleton_original.glb"

    scene_original.export(original_file)

    # --------------------------------------------------
    # Skeleton con fix_mesh
    # --------------------------------------------------

    fixed_mesh = get_fixed_mesh()

    skeleton_fixed = skeletor.skeletonize.by_vertex_clusters(
        fixed_mesh,
        sampling_dist=0.05,
    )

    scene_fixed = skeleton_fixed.scene()

    fixed_file = OUTPUT_DIR / "skeleton_fix_mesh.glb"

    scene_fixed.export(fixed_file)

    # --------------------------------------------------

    print("=" * 60)
    print("Exportación")
    print("=" * 60)

    print(f"Original : {original_file}")
    print(f"Existe   : {original_file.exists()}")

    print()

    print(f"Fix Mesh : {fixed_file}")
    print(f"Existe   : {fixed_file.exists()}")
    
    

################################################
# COMPARACIÓN DE ALGORITMOS DE SKELETOR
################################################

def test_wavefront():
    """
    Evalúa el algoritmo Wavefront de Skeletor.
    """
    mesh = get_fixed_mesh()
    
    skeleton = skeletor.skeletonize.by_wavefront(
        mesh,
        waves=1,
        step_size=1,
    )
    
    print_skeleton_stats("Wavefront", skeleton)
    export_skeleton("skeleton_wavefront", skeleton)
    
    
def test_wavefront_exact():
    """
    Evalúa el algoritmo Wavefront Exact de Skeletor.
    """
    mesh = get_fixed_mesh()

    skeleton = skeletor.skeletonize.by_wavefront_exact(
        mesh,
        step_size=1,
    )

    print_skeleton_stats("Wavefront Exact", skeleton)


def test_teasar():
    """
    Evalúa el algoritmo Teasar de Skeletor.
    """
    mesh = get_fixed_mesh()
    
    skeleton = skeletor.skeletonize.by_teasar(
        mesh,
        inv_dist=50,
    )
    
    print_skeleton_stats("Teasar", skeleton)
    export_skeleton("skeleton_teasar", skeleton)


  

def main():

    test_vertex_cluster()
    
    # test_fix_mesh_api()
    
    # test_fix_mesh()
    
    # test_fix_mesh_vs_original()
    
    # test_fix_mesh_export()
    
    #test_wavefront()
    
    # test_wavefront_exact()
    
    #test_teasar()

if __name__ == "__main__":
    main()