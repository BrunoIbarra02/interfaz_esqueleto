# Skeletor

# Estado

Estado: Completado
Fase: 2

Dependencias:
- 01_trimesh.md

Documento siguiente:
- 03_gltf.md

## Objetivo

Evaluar los algoritmos de skeletonización disponibles en Skeletor para
determinar cuál ofrece la mejor base para construir un esqueleto
topológico.

---

# Herramienta utilizada

- skeletor

---

# Papel dentro del pipeline

```
Mesh limpia

↓

Skeletor

↓

Curve Skeleton

↓

Graph

↓

NetworkX
```

---

# Algoritmos evaluados

- Vertex Cluster
- Wavefront
- Wavefront Exact
- TEASAR

---

# Comparativa cuantitativa

| Algoritmo | Vértices | Aristas | Raíces | Hojas |
|-----------|---------:|--------:|--------:|-------:|
| Vertex Cluster | 1687 | 1582 | 105 | 534 |
| Wavefront | 1598 | 1501 | 97 | 561 |
| Wavefront Exact | 110 | 5 | 105 | 110 |
| TEASAR | 1283 | 1178 | 105 | 271 |

---

# Comparación visual

Se exportaron los cuatro resultados a GLB para su inspección en Blender.

Archivos generados:

```
skeleton_vertex_cluster.glb

skeleton_wavefront.glb

skeleton_wavefront_exact.glb

skeleton_teasar.glb
```

---

# Observaciones

## Vertex Cluster

- Muy detallado.
- Exceso de ramas.
- Elevado ruido superficial.

---

## Wavefront

- Menos ruido.
- Mejor continuidad.
- Sigue generando muchas ramas.

---

## Wavefront Exact

- Skeleton excesivamente simplificado.
- No representa correctamente la anatomía.

Descartado.

---

## TEASAR

- Skeleton más limpio.
- Menor número de hojas.
- Mejor estructura general.

---

# Información obtenida

Un objeto `Skeleton` contiene principalmente:

```
vertices

edges

radius

segments

graph
```

También permite generar una escena (`scene()`) para su exportación.

---

# Exportación

Los Skeleton se exportaron mediante:

```
Skeleton

↓

Scene()

↓

GLB
```

para realizar comparaciones visuales en Blender.

---

# Conclusiones

Skeletor no genera un armature.

Genera un **curve skeleton** representado como un grafo.

Será necesario transformar posteriormente dicho grafo en una jerarquía de
huesos.

---

# Decisiones tomadas

- Se utilizará `fix_mesh()` antes de skeletonizar.
- Wavefront Exact queda descartado.
- TEASAR es el mejor candidato actual.
- La decisión definitiva queda supeditada al análisis con NetworkX.

---

# Trabajo pendiente

- Analizar el grafo generado.
- Detectar ramas principales.
- Identificar hojas y bifurcaciones.
- Construir una jerarquía de huesos.