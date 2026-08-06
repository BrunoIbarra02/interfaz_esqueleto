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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import tests.topology.common as common

################################################
# GRAPH
################################################

def test_get_graph_api():
    """
    Inspecciona la API de Skeleton.get_graph().
    """

    skeleton = common.get_skeleton()

    common.print_title("API get_graph")

    print(inspect.signature(skeleton.get_graph))

    print()

    print(skeleton.get_graph.__doc__)


def test_graph_api():
    """
    Inspecciona el grafo generado por Skeletor.
    """

    graph = common.get_graph()

    common.print_title("Graph")

    print(type(graph))

    print()

    print(inspect.getmro(type(graph)))


def test_get_graph_source():
    """
    Muestra la implementación de get_graph().
    """

    skeleton = common.get_skeleton()

    common.print_title("Código fuente get_graph")

    print(inspect.getsource(skeleton.get_graph))


def test_swc():
    """
    Inspecciona la estructura SWC del Skeleton.
    """

    skeleton = common.get_skeleton()

    common.print_title("SWC")

    print(type(skeleton.swc))

    print()

    print(skeleton.swc.head())

    print()

    print(f"Filas : {len(skeleton.swc)}")


def test_graph_summary():
    """
    Muestra un resumen del grafo generado por Skeletor.
    """

    graph = common.get_graph()

    common.print_title("Resumen")

    print(f"Nodos        : {graph.number_of_nodes()}")
    print(f"Aristas      : {graph.number_of_edges()}")
    print(f"Dirigido     : {graph.is_directed()}")
    print(f"Multigrafo   : {graph.is_multigraph()}")


def test_swc_summary():
    """
    Resume la información del DataFrame SWC.
    """

    skeleton = common.get_skeleton()

    swc = skeleton.swc

    common.print_title("Resumen SWC")

    print(f"Filas          : {len(swc)}")
    print(f"Raíces         : {(swc.parent_id == -1).sum()}")
    print(f"Con padre      : {(swc.parent_id != -1).sum()}")
    print(f"Radius nulos   : {swc.radius.isna().sum()}")
    
########################################################
# TOPOLOGY
########################################################

def test_graph_topology():
    """
    Analiza la topología del grafo.
    """

    graph = common.get_graph()

    common.print_title("Topología")

    print(
        f"Componentes débiles : "
        f"{len(list(nx.weakly_connected_components(graph)))}"
    )

    print(
        f"Componentes fuertes : "
        f"{len(list(nx.strongly_connected_components(graph)))}"
    )

    print(
        f"Es DAG              : "
        f"{nx.is_directed_acyclic_graph(graph)}"
    )


########################################################
# NODES
########################################################

def test_nodes():
    """
    Inspecciona los nodos del grafo.
    """

    graph = common.get_graph()

    common.print_title("Nodos")

    nodes = list(graph.nodes(data=True))

    print(f"Número de nodos : {len(nodes)}")

    print()

    for node in nodes[:5]:
        print(node)


def test_node_degrees():
    """
    Analiza el grado de los nodos del grafo.
    """

    graph = common.get_graph()

    common.print_title("Grados")

    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())

    print("Primeros 10 nodos:")

    print()

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

    graph = common.get_graph()

    roots = sum(
        1
        for _, out_degree in graph.out_degree()
        if out_degree == 0
    )

    leafs = sum(
        1
        for _, in_degree in graph.in_degree()
        if in_degree == 0
    )

    common.print_title("Resumen grados")

    print(f"Raíces (out=0) : {roots}")
    print(f"Hojas (in=0)   : {leafs}")


########################################################
# BRANCHES
########################################################

def test_branch_nodes():
    """
    Localiza los nodos con más de un hijo.
    """

    graph = common.get_graph()

    common.print_title("Bifurcaciones")

    branches = [
        node
        for node, in_degree in graph.in_degree()
        if in_degree > 1
    ]

    print(f"Número de bifurcaciones : {len(branches)}")

    print()

    print("Primeras 20:")

    print()

    for node in branches[:20]:
        print(
            f"Nodo {node}: hijos={graph.in_degree(node)}"
        )


def test_branch_summary():
    """
    Resume el número de hijos de las bifurcaciones.
    """

    graph = common.get_graph()

    common.print_title("Resumen bifurcaciones")

    distribution = {}

    for _, in_degree in graph.in_degree():

        if in_degree > 1:
            distribution[in_degree] = (
                distribution.get(in_degree, 0) + 1
            )

    for degree in sorted(distribution):
        print(
            f"{degree} hijos : "
            f"{distribution[degree]} nodos"
        )########################################################
# EDGES
########################################################

def test_edges():
    """
    Inspecciona las aristas del grafo.
    """

    graph = common.get_graph()

    common.print_title("Aristas")

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

    graph = common.get_graph()

    common.print_title("Primer árbol")

    # Buscar una raíz (no tiene padre)
    root = next(
        node
        for node, out_degree in graph.out_degree()
        if out_degree == 0
    )

    print(f"Raíz : {root}")

    # Como las aristas van hijo -> padre,
    # invertimos el grafo para recorrer
    # desde la raíz hacia los hijos.
    tree = graph.reverse(copy=False)

    nodes = nx.descendants(tree, root)
    nodes.add(root)

    print(f"Nodos : {len(nodes)}")

    print()

    print("Primeros 20 nodos:")

    print()

    for node in sorted(nodes)[:20]:
        print(node)


def test_tree_sizes():
    """
    Analiza el tamaño de los árboles del bosque.
    """

    graph = common.get_graph()

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

    common.print_title("Tamaño de los árboles")

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


########################################################
# MAIN
########################################################

def main():

    # test_get_graph_api()

    # test_graph_api()

    # test_get_graph_source()

    # test_swc()

    # test_graph_summary()

    # test_swc_summary()

    # test_graph_topology()

    # test_nodes()

    # test_node_degrees()

    # test_degree_summary()

    # test_branch_nodes()

    # test_branch_summary()

    # test_edges()

    # test_first_tree()

    test_tree_sizes()

if __name__ == "__main__":
    main()