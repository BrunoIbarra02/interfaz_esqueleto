from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import tests.topology.common as common
import networkx as nx


def test_tree_api():
    """
    Inspecciona la API utilizada para recorrer el árbol.
    """

    graph = common.get_graph()

    common.print_title("Tree API")

    print(type(graph))
    print()
    print(dir(graph))

################################################
# SUCCESSORS
################################################

def test_successors():
    """
    Obtiene los hijos de un nodo.
    """

    graph = common.get_graph()

    node = 0

    common.print_title("Successors")

    print(f"Nodo: {node}")
    print()

    print(list(graph.successors(node)))
    
################################################
# PREDECESSORS
################################################    
    
def test_predecessors():
    """
    Obtiene los padres de un nodo.
    """

    graph = common.get_graph()

    node = 0

    common.print_title("Predecessors")

    print(f"Nodo: {node}")
    print()

    print(list(graph.predecessors(node)))
    
    print()

    print("4233 -> 0")
    print(graph.has_edge(4233, 0))

    print()

    print("0 -> 4233")
    print(graph.has_edge(0, 4233))

    print()

    print("Edge 4233 -> 0")
    print(graph.get_edge_data(4233, 0))

    print()

    print("Edge 0 -> 4233")
    print(graph.get_edge_data(0, 4233))
    
########################################################
# NODES
########################################################

def test_swc_nodes():
    """
    Inspecciona dos nodos del SWC.
    """

    skeleton = common.get_skeleton()

    common.print_title("SWC Nodes")

    print(
        skeleton.swc.loc[
            skeleton.swc.node_id.isin([0, 4233])
        ]
    )  
    
########################################################
# NEIGHBORS
########################################################

def test_neighbors():
    """
    Obtiene los vecinos de un nodo.
    """

    graph = common.get_graph()

    node = 0

    common.print_title("Neighbors")

    print(f"Nodo: {node}")

    print()

    print(list(graph.neighbors(node)))

#########################################################
# REVERSE
#########################################################

def test_reverse():
    """
    Invierte la dirección de las aristas del grafo.
    """

    graph = common.get_graph()

    reverse = graph.reverse()

    node = 0

    common.print_title("Reverse")

    print(f"Nodo: {node}")

    print()

    print("Successors")
    print(list(reverse.successors(node)))

    print()

    print("Predecessors")
    print(list(reverse.predecessors(node)))
    
    
def test_reverse_successors():
    """
    Inspecciona los hijos en el grafo invertido.
    """

    graph = common.get_graph().reverse()

    node = 0

    common.print_title("Reverse Successors")

    print(f"Nodo: {node}")
    print()

    children = list(graph.successors(node))

    print(f"Hijos ({len(children)}):")
    print(children)
    
#######################################################
# DFS
#######################################################

def test_dfs():
    """
    Recorre el árbol en profundidad.
    """

    import networkx as nx

    graph = common.get_graph().reverse()

    root = 0

    common.print_title("DFS")

    dfs = set(nx.dfs_preorder_nodes(graph, root))

    print(f"Nodos recorridos : {len(dfs)}")

    print()

    print("Primeros 20:")

    for node in sorted(dfs)[:20]:
        print(node)

    print()

    descendants = nx.descendants(graph, root)
    descendants.add(root)

    print(f"Descendants : {len(descendants)}")
    print(f"DFS         : {len(dfs)}")

    print()

    print("Solo en descendants:")
    print(sorted(descendants - dfs))

    print()

    print("Solo en DFS:")
    print(sorted(dfs - descendants))
    
################
# EDGES
################
def test_tree_edges():
    """
    Recorre las aristas del árbol.
    """

    graph = common.get_graph().reverse()

    root = 0

    common.print_title("Tree Edges")

    print(f"Raíz : {root}")

    print()

    for parent in nx.dfs_preorder_nodes(graph, root):

        children = list(graph.successors(parent))

        for child in children:
            print(f"{parent} -> {child}")

def main():
    #test_tree_api()
    #test_predecessors()
    #test_swc_nodes()
    #test_neighbors()
    #test_reverse()
    #test_dfs()
    #test_reverse_successors()
    test_tree_edges()


if __name__ == "__main__":
    main()