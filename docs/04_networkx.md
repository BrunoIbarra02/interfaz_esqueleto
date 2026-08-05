# NetworkX

# Estado

Estado: Completado

Fase: 4 (Representación del Skeleton como grafo)

Dependencias:
- 01_trimesh.md
- 02_skeletor.md
- 03_gltf.md

Documento siguiente:
- 05_bbox.md

## Objetivo

Comprender cómo Skeletor representa internamente un Skeleton como un
grafo dirigido utilizando NetworkX y evaluar si dicha estructura puede
utilizarse como base para construir una jerarquía de huesos.

---

# Herramientas utilizadas

- networkx
- pandas

---

# Grafo generado

El método:

```python
Skeleton.get_graph()
```

genera un objeto:

```python
networkx.DiGraph
```

No recibe parámetros.

---

# Implementación de get_graph()

La implementación interna de Skeletor es:

```python
def get_graph(self):

    not_root = self.swc.parent_id >= 0

    nodes = self.swc.loc[not_root]

    parents = self.swc.set_index("node_id").loc[
        self.swc.loc[not_root, "parent_id"].values
    ]

    dists = nodes[["x","y","z"]].values - parents[["x","y","z"]].values
    dists = np.sqrt((dists**2).sum(axis=1))

    G = nx.DiGraph()

    G.add_nodes_from(self.swc.node_id.values)

    G.add_weighted_edges_from(
        zip(
            nodes.node_id.values,
            nodes.parent_id.values,
            dists
        )
    )

    return G
```

## Conclusiones

El grafo no se construye utilizando:

```
Skeleton.vertices
```

Sino utilizando:

```
Skeleton.swc
```

Cada fila del DataFrame SWC se convierte en un nodo del grafo.

---

# Arquitectura interna

```
Skeleton
│
├── vertices
├── edges
├── radius
└── swc (DataFrame)
         │
         ▼
     get_graph()
         │
         ▼
NetworkX DiGraph
```

---

# SWC

La estructura interna utilizada por Skeletor es un DataFrame de pandas.

## Columnas

| Campo | Descripción |
|--------|-------------|
| node_id | Identificador del nodo |
| parent_id | Nodo padre |
| x | Coordenada X |
| y | Coordenada Y |
| z | Coordenada Z |
| radius | Radio del nodo |

---

# Resumen SWC

| Campo | Valor |
|--------|------:|
| Filas | 2936 |
| Raíces | 105 |
| Con padre | 2831 |
| Radius nulos | 2936 |

## Conclusiones

- Cada fila representa un nodo.
- Los nodos raíz poseen `parent_id = -1`.
- TEASAR no calcula radios.

---

# Construcción del grafo

El método genera una arista por cada nodo con padre.

```
Nodo hijo

↓

Nodo padre

↓

Distancia euclídea

↓

Arista ponderada
```

Las aristas siempre apuntan:

```
Hijo

────►

Padre
```

---

# Edge Weight

Cada arista almacena:

```
weight = distancia euclídea
```

entre el nodo hijo y su nodo padre.

No representa un coste arbitrario.

---

# Resumen del grafo

| Propiedad | Valor |
|------------|------:|
| Tipo | DiGraph |
| Nodos | 2936 |
| Aristas | 2831 |
| Dirigido | Sí |
| Multigrafo | No |

---

# Topología

| Propiedad | Valor |
|------------|------:|
| Componentes débiles | 105 |
| Componentes fuertes | 2936 |
| DAG | Sí |

## Conclusiones

El resultado no es un único árbol.

Skeletor genera un bosque compuesto por 105 árboles independientes.

No existen ciclos.

---

# Grados

## Raíces

```
out_degree = 0
```

105 nodos.

---

## Hojas

```
in_degree = 0
```

302 nodos.

---

## Bifurcaciones

193 nodos.

Distribución:

| Hijos | Nodos |
|------:|------:|
| 2 | 189 |
| 3 | 4 |

La inmensa mayoría de bifurcaciones son binarias.

---

# Tamaño de los árboles

| Métrica | Valor |
|---------|------:|
| Árboles | 105 |
| Mínimo | 2 |
| Máximo | 478 |
| Media | 27.96 |

Árboles más grandes:

```
186
251
274
438
478
```

Árboles más pequeños:

```
2
2
2
2
...
```

---

# Flujo completo

```
Mesh

↓

TEASAR

↓

Skeleton

↓

SWC

↓

NetworkX DiGraph

↓

Bosque (105 árboles)
```

---

# Información descubierta

## 2026-08-05

✓ `get_graph()` devuelve un `networkx.DiGraph`.

✓ El grafo se construye utilizando `Skeleton.swc`.

✓ SWC es un `pandas.DataFrame`.

✓ Cada fila representa un nodo.

✓ Los nodos raíz poseen `parent_id = -1`.

✓ Las aristas apuntan del hijo hacia el padre.

✓ El peso de cada arista corresponde a la distancia euclídea.

✓ El resultado es un DAG.

✓ TEASAR genera un bosque compuesto por 105 árboles.

✓ La mayoría de bifurcaciones tienen exactamente dos hijos.

✓ Existen unos pocos árboles grandes y numerosos árboles muy pequeños.

---

# Objetivo final

Transformar el bosque generado por Skeletor en una única jerarquía de
huesos que posteriormente pueda convertirse en un Skin compatible con
glTF.