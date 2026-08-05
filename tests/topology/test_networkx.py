"""
=========================================================
Test: NetworkX

Objetivo:
    Analizar el grafo generado por Skeletor y estudiar
    su estructura para construir posteriormente una
    jerarquía de huesos.

Documento asociado:
    docs/04_networkx.md

Estado:
    En desarrollo
=========================================================
"""

from pathlib import Path
import sys
import inspect
import networkx as nx
import skeletor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from topology.preprocess import load_mesh

################################################
# CONSTANTES
################################################

TEST_GLB = Path(__file__).parent / "glb" / "oso_polar.glb"


################################################
# UTILIDADES
################################################

def test_get_graph_api():
    """
    Inspecciona la API de Skeleton.get_graph().
    """

    mesh = load_mesh(str(TEST_GLB))

    mesh = skeletor.pre.fix_mesh(
        mesh,
        remove_disconnected=5,
        inplace=False,
    )

    skeleton = skeletor.skeletonize.by_teasar(
        mesh,
        inv_dist=0.1,
    )

    print("=" * 60)
    print("API get_graph")
    print("=" * 60)

    print(inspect.signature(skeleton.get_graph))

    print()

    print(skeleton.get_graph.__doc__)


def get_graph():
    """
    Genera el grafo del Skeleton utilizado en las pruebas.
    """

    mesh = load_mesh(str(TEST_GLB))

    mesh = skeletor.pre.fix_mesh(
        mesh,
        remove_disconnected=5,
        inplace=False,
    )

    skeleton = skeletor.skeletonize.by_teasar(
        mesh,
        inv_dist=0.1,
    )

    return skeleton.get_graph()


def test_graph_api():
    """
    Inspecciona el grafo generado por Skeletor.
    """

    graph = get_graph()

    print("=" * 60)
    print("Graph")
    print("=" * 60)

    print(type(graph))

    print()

    print(inspect.getmro(type(graph)))
    
    
def test_get_graph_source():
    """
    Muestra la implementación de get_graph().
    """

    mesh = load_mesh(str(TEST_GLB))

    mesh = skeletor.pre.fix_mesh(
        mesh,
        remove_disconnected=5,
        inplace=False,
    )

    skeleton = skeletor.skeletonize.by_teasar(
        mesh,
        inv_dist=0.1,
    )

    print("=" * 60)
    print("Código fuente get_graph")
    print("=" * 60)

    print(inspect.getsource(skeleton.get_graph))
    
def test_swc():
    """
    Inspecciona la estructura SWC del Skeleton.
    """

    mesh = load_mesh(str(TEST_GLB))

    mesh = skeletor.pre.fix_mesh(
        mesh,
        remove_disconnected=5,
        inplace=False,
    )

    skeleton = skeletor.skeletonize.by_teasar(
        mesh,
        inv_dist=0.1,
    )

    print("=" * 60)
    print("SWC")
    print("=" * 60)

    print(type(skeleton.swc))

    print()

    print(skeleton.swc.head())

    print()

    print(f"Filas : {len(skeleton.swc)}")
    
def test_graph_summary():
    """
    Muestra un resumen del grafo generado por Skeletor.
    """

    graph = get_graph()

    print("=" * 60)
    print("Resumen")
    print("=" * 60)

    print(f"Nodos        : {graph.number_of_nodes()}")
    print(f"Aristas      : {graph.number_of_edges()}")
    print(f"Dirigido     : {graph.is_directed()}")
    print(f"Multigrafo   : {graph.is_multigraph()}")
    
def test_swc_summary():
    """
    Resume la información del DataFrame SWC.
    """

    mesh = load_mesh(str(TEST_GLB))

    mesh = skeletor.pre.fix_mesh(
        mesh,
        remove_disconnected=5,
        inplace=False,
    )

    skeleton = skeletor.skeletonize.by_teasar(
        mesh,
        inv_dist=0.1,
    )

    swc = skeleton.swc

    print("=" * 60)
    print("Resumen SWC")
    print("=" * 60)

    print(f"Filas          : {len(swc)}")
    print(f"Raíces         : {(swc.parent_id == -1).sum()}")
    print(f"Con padre      : {(swc.parent_id != -1).sum()}")
    print(f"Radius nulos   : {swc.radius.isna().sum()}")
    
def test_graph_topology():
    """
    Analiza la topología del grafo.
    """

    graph = get_graph()

    print("=" * 60)
    print("Topología")
    print("=" * 60)

    print(f"Componentes débiles : {len(list(nx.weakly_connected_components(graph)))}")
    print(f"Componentes fuertes : {len(list(nx.strongly_connected_components(graph)))}")
    print(f"Es DAG             : {nx.is_directed_acyclic_graph(graph)}")

    
######################################################
# NODES
######################################################

def test_nodes():
    """
    Inspecciona los nodos del grafo.
    """

    graph = get_graph()

    print("=" * 60)
    print("Nodos")
    print("=" * 60)

    nodes = list(graph.nodes(data=True))

    print(f"Número de nodos : {len(nodes)}")

    print()

    for node in nodes[:5]:
        print(node)
        
    
def test_node_degrees():
    """
    Analiza el grado de los nodos del grafo.
    """

    graph = get_graph()

    print("=" * 60)
    print("Grados")
    print("=" * 60)

    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())

    print("Primeros 10 nodos:")

    for node in list(graph.nodes())[:10]:
        print(
            f"{node}: "
            f"in={in_degrees[node]} "
            f"out={out_degrees[node]}"
        )
def test_degree_summary():
    """
    Resume la distribución de grados del grafo.
    """

    graph = get_graph()

    roots = sum(1 for _, out_deg in graph.out_degree() if out_deg == 0)
    leafs = sum(1 for _, in_deg in graph.in_degree() if in_deg == 0)

    print("=" * 60)
    print("Resumen grados")
    print("=" * 60)

    print(f"Raíces (out=0) : {roots}")
    print(f"Hojas (in=0)   : {leafs}")


########################################################
# BRANCHES
########################################################
    
def test_branch_nodes():
    """
    Localiza los nodos con más de un hijo.
    """

    graph = get_graph()

    print("=" * 60)
    print("Bifurcaciones")
    print("=" * 60)

    branches = [
        node
        for node, in_degree in graph.in_degree()
        if in_degree > 1
    ]

    print(f"Número de bifurcaciones : {len(branches)}")

    print()

    print("Primeras 20:")

    for node in branches[:20]:
        print(
            f"Nodo {node}: hijos={graph.in_degree(node)}"
        )
        
def test_branch_summary():
    """
    Resume el número de hijos de las bifurcaciones.
    """

    graph = get_graph()

    print("=" * 60)
    print("Resumen bifurcaciones")
    print("=" * 60)

    distribution = {}

    for _, in_degree in graph.in_degree():

        if in_degree > 1:
            distribution[in_degree] = distribution.get(in_degree, 0) + 1

    for degree in sorted(distribution):
        print(f"{degree} hijos : {distribution[degree]} nodos")
        
#######################################################
# EDGES
#######################################################

def test_edges():
    """
    Inspecciona las aristas del grafo.
    """

    graph = get_graph()

    print("=" * 60)
    print("Aristas")
    print("=" * 60)

    edges = list(graph.edges(data=True))

    print(f"Número de aristas : {len(edges)}")

    print()

    for edge in edges[:10]:
        print(edge)
        
########################################################
# TREES
########################################################

def test_first_tree():
    """
    Inspecciona el primer árbol del bosque.
    """

    graph = get_graph()

    print("=" * 60)
    print("Primer árbol")
    print("=" * 60)

    # Buscar una raíz (no tiene padre)
    root = next(
        node
        for node, out_degree in graph.out_degree()
        if out_degree == 0
    )

    print(f"Raíz : {root}")

    # Como las aristas van hijo -> padre, invertimos el grafo
    # para recorrer desde la raíz hacia los hijos.
    tree = graph.reverse(copy=False)

    nodes = nx.descendants(tree, root)
    nodes.add(root)

    print(f"Nodos : {len(nodes)}")

    print()

    print("Primeros 20 nodos:")

    for node in sorted(nodes)[:20]:
        print(node)
        
def test_tree_sizes():
    """
    Analiza el tamaño de los árboles del bosque.
    """

    graph = get_graph()

    # Invertimos el grafo para recorrer desde las raíces
    tree = graph.reverse(copy=False)

    roots = [
        node
        for node, out_degree in graph.out_degree()
        if out_degree == 0
    ]

    sizes = []

    for root in roots:

        nodes = nx.descendants(tree, root)
        nodes.add(root)

        sizes.append(len(nodes))

    print("=" * 60)
    print("Tamaño de los árboles")
    print("=" * 60)

    print(f"Número de árboles : {len(sizes)}")
    print(f"Mínimo            : {min(sizes)}")
    print(f"Máximo            : {max(sizes)}")
    print(f"Media             : {sum(sizes)/len(sizes):.2f}")

    print()

    print("Árboles más pequeños:")
    print(sorted(sizes)[:10])

    print()

    print("Árboles más grandes:")
    print(sorted(sizes)[-10:])
    
def main():
    #test_graph_summary()
    #test_nodes()
    #test_edges()
    #test_get_graph_api()
    #test_get_graph_source()
    #test_swc()
    #test_swc_summary()
    #test_graph_topology()
    #test_node_degrees()
    #test_degree_summary()
    #test_branch_nodes()
    #test_branch_summary()
    #test_first_tree()
    test_tree_sizes()

if __name__ == "__main__":
    main()
    