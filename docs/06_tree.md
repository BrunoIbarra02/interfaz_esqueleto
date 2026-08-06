# Tree

# Estado

Estado: Completado

Fase: 6 (Tree)

Dependencias:

- 04_networkx.md
- 05_bbox.md

Documento siguiente:

- 07_bones.md

---

# Objetivo

Comprender cómo transformar el grafo generado por Skeletor en una estructura
de árbol orientada desde la raíz hacia las hojas para preparar la generación
de la jerarquía de huesos.

---

# Grafo original

El método `Skeleton.get_graph()` devuelve un `networkx.DiGraph`.

Durante la inspección del código fuente se comprobó que las aristas se crean
mediante:

```python
G.add_weighted_edges_from(
    zip(
        nodes.node_id.values,
        nodes.parent_id.values,
        dists,
    )
)
```

Esto implica que las aristas tienen la orientación:

```
Hijo
 │
 ▼
Padre
```

No la orientación habitual de un árbol.

---

# Successors

En el grafo original:

```python
graph.successors(node)
```

devuelve los nodos alcanzables mediante aristas salientes.

Para una raíz:

```
[]
```

ya que las raíces no apuntan a ningún nodo.

---

# Predecessors

En el grafo original:

```python
graph.predecessors(node)
```

devuelve los hijos del nodo.

Ejemplo:

```
4233 -> 0
```

donde:

```
SWC

node_id    parent_id

0          -1
4233        0
```

confirma que el hijo apunta hacia su padre.

---

# Neighbors

En un `DiGraph`, `neighbors()` devuelve el mismo resultado que
`successors()`.

Durante las pruebas ambos métodos devolvieron exactamente los mismos nodos.

---

# Reverse

Para obtener una jerarquía clásica es necesario invertir las aristas del
grafo.

```python
tree = graph.reverse(copy=False)
```

Tras invertir el grafo, las aristas pasan a tener la orientación:

```
Padre
 │
 ▼
Hijo
```

Esta orientación resulta adecuada para recorrer el árbol desde la raíz.

---

# DFS

Una vez invertido el grafo puede recorrerse mediante:

```python
nx.dfs_preorder_nodes(tree, root)
```

El recorrido devuelve todos los nodos alcanzables desde la raíz en orden de
profundidad.

Durante las pruebas:

```
Nodos recorridos : 11
```

---

# Descendants

También se estudió:

```python
nx.descendants(tree, root)
```

Comparando ambos métodos se comprobó que:

- Ambos contienen exactamente los mismos nodos.
- La única diferencia es que `dfs_preorder_nodes()` devuelve un recorrido
  ordenado mientras que `descendants()` devuelve un conjunto sin orden.

---

# Relaciones padre → hijo

Una vez invertido el grafo, las relaciones pueden obtenerse mediante:

```python
for parent in nx.dfs_preorder_nodes(tree, root):

    for child in tree.successors(parent):
        ...
```

Durante las pruebas se obtuvo:

```
0 -> 2934
0 -> 2935
2934 -> 2932
2935 -> 2933
2933 -> 2931
2931 -> 2929
2929 -> 2924
2924 -> 2920
2920 -> 2914
2914 -> 2911
```

Estas relaciones representan directamente las aristas del árbol.

---

# Flujo

```
Skeleton

↓

SWC

↓

NetworkX DiGraph

↓

Hijo -> Padre

↓

reverse()

↓

Padre -> Hijo

↓

DFS

↓

Relaciones Padre -> Hijo
```

---

# Conclusiones

- `Skeleton.get_graph()` devuelve un `networkx.DiGraph`.
- Las aristas originales están orientadas desde el hijo hacia el padre.
- `reverse()` invierte completamente la orientación del árbol.
- `successors()` permite obtener los hijos en el grafo invertido.
- `dfs_preorder_nodes()` recorre el árbol completo desde una raíz.
- `dfs_preorder_nodes()` y `descendants()` contienen exactamente los mismos nodos.
- Las relaciones padre → hijo obtenidas durante el recorrido serán utilizadas en la siguiente fase para construir la jerarquía de huesos.

---

# Descubrimientos

## 2026-08-06

✓ El grafo de Skeletor está orientado hijo → padre.

✓ El grafo invertido representa correctamente la jerarquía padre → hijo.

✓ DFS recorre todos los nodos del árbol.

✓ DFS y descendants contienen el mismo conjunto de nodos.

✓ Las aristas padre → hijo pueden obtenerse directamente mediante `successors()` durante el recorrido DFS.