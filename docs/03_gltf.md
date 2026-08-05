# GLTF / GLB

# Estado

Estado: Completado

Fase: 3 (Lectura del GLB)

Dependencias:

- 01_trimesh.md
- 02_skeletor.md

Documento siguiente:

- 04_networkx.md

---

## Objetivo

Comprender la estructura interna de un GLB para poder añadir un Skin,
una jerarquía de huesos y las Inverse Bind Matrices sin modificar la
geometría original.

---

# Herramienta utilizada

- pygltflib

---

# Modelo analizado

oso_polar.glb

---

# Resumen del GLB

| Campo | Valor |
|--------|------:|
| Scenes | 1 |
| Nodes | 1 |
| Meshes | 1 |
| Skins | 0 |
| Animations | 0 |
| Materials | 1 |
| Textures | 2 |
| Images | 2 |
| Accessors | 4 |
| BufferViews | 6 |
| Buffers | 1 |

## Conclusiones

- Existe una única escena.
- Existe un único nodo.
- Existe una única malla.
- El GLB no contiene Skin.
- El GLB no contiene animaciones.
- El pipeline deberá generar toda la estructura de rigging.

---

# Scene

```
Scene 0

name = Scene

nodes = [0]
```

## Interpretación

La escena contiene un único nodo.

---

# Node

```
Node 0

mesh = 0

skin = None

children = []

name = Mesh_0
```

## Interpretación

El único nodo de la escena referencia la única malla existente.

No existe jerarquía.

No existe Skin asociado.

---

# Mesh

```
Mesh_0
│
└── Primitive
    │
    ├── POSITION
    ├── NORMAL
    ├── TEXCOORD_0
    └── INDICES
```

---

# Primitive

```
POSITION   -> Accessor 0

NORMAL     -> Accessor 1

TEXCOORD_0 -> Accessor 2

INDICES    -> Accessor 3
```

---

# Relación completa

```
Scene
│
└── Node 0 (Mesh_0)
    │
    └── Mesh 0
        │
        └── Primitive
            │
            ├── POSITION ─────► Accessor 0 ─────► BufferView 0 ─────► Buffer 0
            │
            ├── NORMAL ───────► Accessor 1 ─────► BufferView 1 ─────► Buffer 0
            │
            ├── TEXCOORD_0 ───► Accessor 2 ─────► BufferView 2 ─────► Buffer 0
            │
            ├── INDICES ──────► Accessor 3 ─────► BufferView 3 ─────► Buffer 0
            │
            └── Material 0
                    │
                    ├── Normal Texture
                    │       │
                    │       ▼
                    │   Texture 0
                    │       │
                    │       ▼
                    │   Image 0 (PNG)
                    │       │
                    │       ▼
                    │   BufferView 4
                    │       │
                    │       ▼
                    │   Buffer 0
                    │
                    └── Base Color Texture
                            │
                            ▼
                        Texture 1
                            │
                            ▼
                        Image 1 (JPEG)
                            │
                            ▼
                        BufferView 5
                            │
                            ▼
                        Buffer 0
```

---

# Accessors

| Accessor | Tipo | Component | Count | Uso |
|----------|------|-----------|------:|-----|
| 0 | VEC3 | FLOAT | 19978 | POSITION |
| 1 | VEC3 | FLOAT | 19978 | NORMAL |
| 2 | VEC2 | FLOAT | 19978 | TEXCOORD_0 |
| 3 | SCALAR | UINT16 | 93762 | INDICES |

## Relaciones

```
Accessor 0

↓

19978 vértices

↓

Trimesh.vertices
```

```
Accessor 3

↓

93762 índices

↓

31254 triángulos

↓

Trimesh.faces
```

---

# BufferViews

| BufferView | Target | ByteLength | Contenido |
|------------|--------|-----------:|-----------|
| 0 | ARRAY_BUFFER | 239736 | POSITION |
| 1 | ARRAY_BUFFER | 239736 | NORMAL |
| 2 | ARRAY_BUFFER | 159824 | TEXCOORD_0 |
| 3 | ELEMENT_ARRAY_BUFFER | 187524 | INDICES |
| 4 | None | 2281711 | Image 0 (PNG) |
| 5 | None | 2457471 | Image 1 (JPEG) |

---

# Buffers

| Buffer | ByteLength | URI |
|---------|-----------:|-----|
| 0 | 5566004 | None |

## Conclusiones

- El GLB contiene un único Buffer.
- El Buffer está embebido en el propio archivo.
- No existe un archivo `.bin` externo.
- Todos los datos geométricos y las texturas se almacenan dentro del mismo Buffer.

---

# Materials

Existe un único material denominado `Material_0`.

## Propiedades

| Campo | Valor |
|-------|-------|
| Alpha Mode | OPAQUE |
| Double Sided | True |
| Base Color | [1,1,1,1] |
| Metallic | 0.0 |
| Roughness | 0.8 |

## Texturas utilizadas

Base Color → Texture 1

Normal Map → Texture 0

No existen:

- Metallic/Roughness Texture
- Occlusion Texture
- Emissive Texture

---

# Textures

El GLB contiene dos texturas.

| Texture | Sampler | Image |
|---------:|--------:|------:|
| 0 | 0 | 0 |
| 1 | 0 | 1 |

## Relaciones

Material_0

- Normal Texture → Texture 0
- Base Color Texture → Texture 1

Las texturas actúan únicamente como enlace entre el material y las imágenes.

---

# Images

El GLB contiene dos imágenes embebidas.

| Image | Nombre | MIME | BufferView |
|------:|---------|------|-----------:|
| 0 | normal | image/png | 4 |
| 1 | Image_0 | image/jpeg | 5 |

## Relaciones

Texture 0

↓

Image 0

↓

BufferView 4

↓

Buffer 0

Texture 1

↓

Image 1

↓

BufferView 5

↓

Buffer 0

---

# Información que NO existe

Actualmente el GLB no contiene:

- Skin
- JOINTS_0
- WEIGHTS_0
- Inverse Bind Matrices
- Animaciones

Todo ello deberá ser generado por el pipeline.

---

# Objetivo final

El pipeline deberá transformar:

```
Mesh

↓

Curve Skeleton

↓

Graph

↓

Hierarchy

↓

Skin

↓

Rigged GLB
```

---

# Descubrimientos

## 2026-08-05

✓ Rodin genera una única Scene.

✓ Rodin genera un único Node.

✓ Rodin genera una única Mesh.

✓ El GLB no contiene Skin.

✓ El GLB no contiene Animaciones.

✓ POSITION coincide exactamente con Trimesh.vertices.

✓ INDICES coincide exactamente con Trimesh.faces.

✓ Los BufferViews siguen exactamente la especificación glTF.

✓ El GLB contiene un único Buffer embebido.

✓ Las imágenes se almacenan mediante BufferViews dentro del Buffer principal.

✓ El material y las texturas son independientes del futuro sistema de rigging.