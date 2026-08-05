# Pipeline

## Estado

Documento vivo.

Se actualizará conforme avance el desarrollo.

---

# Arquitectura

GLB
│
▼
Loader (pygltflib)
│
▼
Trimesh
│
▼
fix_mesh
│
▼
Skeletonización (TEASAR)
│
▼
Skeleton
│
├── vertices
├── edges
└── swc
      │
      ▼
NetworkX
      │
      ▼
Análisis topológico
      │
      ▼
Selección del árbol principal
      │
      ▼
BBox
      │
      ▼
Jerarquía de huesos
      │
      ▼
Skin
      │
      ▼
Rigged GLB

---

# Fases

01 → Trimesh

02 → Skeletor

03 → GLTF

04 → NetworkX

05 → Bounding Boxes

06 → Jerarquía

07 → Skin

08 → Exportación