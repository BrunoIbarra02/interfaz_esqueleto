# Bounding Boxes

# Estado

Estado: Completado

Fase: 5 (Bounding Boxes)

Dependencias:
- 01_trimesh.md
- 02_skeletor.md
- 03_gltf.md
- 04_networkx.md

Documento siguiente:
- 06_hierarchy.md

---

# Objetivo

Comprender cómo generar una Bounding Box a partir de una malla y qué
información proporciona para las siguientes etapas del pipeline.

---

# Herramientas utilizadas

- bbox
- trimesh

---

# Investigación

Durante esta fase se estudiaron dos librerías distintas.

## bbox

La librería `bbox` proporciona la clase `BBox3D`, utilizada para representar
Bounding Boxes tridimensionales.

Durante las pruebas se comprobó que la librería no genera Bounding Boxes a
partir de una malla, sino que únicamente representa una caja ya definida.

---

## Trimesh

La librería `trimesh` genera automáticamente Bounding Boxes a partir de una
malla.

Existen dos variantes principales:

- Axis Aligned Bounding Box (AABB)
- Oriented Bounding Box (OBB)

Estas cajas contienen toda la información geométrica necesaria para las
siguientes fases del pipeline.

---

# BBox3D

## Constructor

```python
BBox3D(
    x,
    y,
    z,
    length=1,
    width=1,
    height=1,
    rw=1,
    rx=0,
    ry=0,
    rz=0,
    q=None,
    euler_angles=None,
    is_center=True,
)
```

---

## Propiedades

```
center

length
width
height

quaternion

p1
p2
p3
p4
p5
p6
p7
p8
```

---

## Funcionalidad

BBox3D calcula automáticamente:

- Centro
- Dimensiones
- Cuaternión
- Ocho vértices de la caja

No dispone de métodos para calcular una Bounding Box a partir de una nube de
puntos o una malla.

---

# Trimesh

## Axis Aligned Bounding Box

```
Mesh

↓

bounding_box

↓

Box
```

La Bounding Box alineada a ejes proporciona:

- Bounds
- Centroid
- Extents
- Volume
- Transform

---

## Oriented Bounding Box

```
Mesh

↓

bounding_box_oriented

↓

Box
```

La Bounding Box orientada calcula automáticamente la orientación que mejor se
ajusta a la geometría del modelo.

---

# Box

Durante las pruebas se inspeccionaron las principales propiedades del objeto
`Box`.

## Bounds

```
Bounds

↓

[xmin, ymin, zmin]

[xmax, ymax, zmax]
```

Representan los límites espaciales de la caja.

---

## Centroid

Centro geométrico de la Bounding Box.

---

## Extents

Representan las dimensiones de la caja.

Durante las pruebas se comprobó que `Box.extents` se calcula mediante:

```
max(bounds) - min(bounds)
```

Coincidiendo exactamente con las dimensiones obtenidas a partir de los ocho
vértices de la caja.

---

## Volume

Volumen de la Bounding Box.

---

## Transform

Matriz de transformación homogénea de 4×4 que describe la posición y
orientación de la Bounding Box.

En una AABB la matriz coincide prácticamente con la identidad.

En una OBB la matriz contiene la rotación necesaria para ajustar la caja a la
geometría del modelo.

---

## Vertices

La Bounding Box se representa mediante ocho vértices.

Las dimensiones de la caja pueden recuperarse mediante:

```
max(vertices) - min(vertices)
```

---

# PrimitiveAttributes

Cada `Box` contiene un objeto interno denominado `PrimitiveAttributes`.

```
Box

↓

PrimitiveAttributes
```

Este objeto almacena únicamente los parámetros que definen el primitivo.

## Propiedades

```
extents

transform
```

Durante las pruebas se comprobó que:

- `Primitive.transform` coincide exactamente con `Box.transform`.
- `Primitive.extents` no coincide con `Box.extents`.

El código fuente muestra que `PrimitiveAttributes` no calcula estos valores,
sino que devuelve los parámetros previamente almacenados por el primitivo.

---

# Flujo de generación

```
GLB

↓

Trimesh

↓

Mesh

↓

Bounding Box

↓

Box

├── Bounds
├── Centroid
├── Extents
├── Volume
├── Transform
└── Vertices

↓

BBox3D
```

---

# Conclusiones

- `BBox3D` representa una Bounding Box tridimensional.
- `BBox3D` no calcula Bounding Boxes a partir de una malla.
- `Trimesh` genera automáticamente Bounding Boxes a partir de una geometría.
- `bounding_box` genera una Axis Aligned Bounding Box (AABB).
- `bounding_box_oriented` genera una Oriented Bounding Box (OBB).
- `Box.extents` se calcula a partir de los límites espaciales (`bounds`).
- `PrimitiveAttributes` almacena los parámetros internos del primitivo.
- La orientación de una OBB queda descrita mediante la matriz `transform`.

---

# Descubrimientos

## 2026-08-06

✓ BBox3D representa Bounding Boxes.

✓ BBox3D calcula automáticamente los ocho vértices.

✓ BBox3D no genera Bounding Boxes a partir de una malla.

✓ Trimesh genera Bounding Boxes alineadas y orientadas.

✓ Box.extents coincide con las dimensiones obtenidas a partir de los vértices.

✓ Primitive.transform coincide con Box.transform.

✓ Primitive.extents corresponde al valor almacenado por el primitivo y no al cálculo realizado sobre la geometría.