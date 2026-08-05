# Trimesh

# Estado

Estado: Completado
Fase: 1

Dependencias:
- Ninguna

Documento siguiente:
02_skeletor.md

## Objetivo

Utilizar Trimesh como etapa de preprocesado del pipeline para cargar,
inspeccionar y reparar modelos GLB antes de aplicar algoritmos de
skeletonización.

---

# Herramienta utilizada

- trimesh

---

# Papel dentro del pipeline

```
GLB
 │
 ▼
load_mesh()
 │
 ▼
Trimesh
 │
 ▼
fix_mesh()
 │
 ▼
Mesh limpia
 │
 ▼
Skeletonización
```

---

# Funciones implementadas

## load_mesh()

Carga un modelo GLB y devuelve un objeto `trimesh.Trimesh`.

---

## fix_mesh()

Repara problemas comunes de la geometría.

Configuración utilizada:

```python
skeletor.pre.fix_mesh(
    mesh,
    remove_disconnected=5,
    inplace=False,
)
```

---

# Información obtenida

## Malla original

```
Tipo       : Trimesh
Vertices   : 19978
Caras      : 31254
Watertight : False
```

---

## Malla reparada

```
Tipo       : Trimesh
Vertices   : 15959
Caras      : 27354
Watertight : False
```

---

# Efecto de fix_mesh

Reducción de vértices

```
19978

↓

15959
```

Reducción de caras

```
31254

↓

27354
```

Eliminación de pequeños fragmentos desconectados.

---

# Comparación sobre la skeletonización

Sin fix_mesh

```
Vertex Cluster

Vertices : 2359
Aristas  : 1792
Raíces   : 567
Hojas    : 1078
```

Con fix_mesh

```
Vertex Cluster

Vertices : 1687
Aristas  : 1582
Raíces   : 105
Hojas    : 534
```

La reducción del ruido fue muy significativa.

---

# Conclusiones

- Todo modelo deberá pasar por `fix_mesh()`.
- El preprocesado mejora considerablemente la calidad del skeleton.
- El coste computacional es reducido frente al beneficio obtenido.

---

# Decisiones tomadas

- `fix_mesh()` será obligatorio antes de skeletonizar.
- Se utilizará `remove_disconnected=5`.

---

# Trabajo pendiente

- Evaluar si algunos modelos requieren remallado mediante PyMeshLab.