# Bone

## Descripción

La clase `Bone` representa un nodo del árbol esquelético generado a partir del modelo 3D.

Cada hueso almacena su posición en el espacio, la relación jerárquica con el resto del esqueleto y las características geométricas necesarias para el proceso de comparación.

---

## Responsabilidades

- Representar un hueso del esqueleto.
- Mantener la estructura jerárquica del árbol.
- Almacenar información geométrica del hueso.
- Servir como unidad básica para la extracción de características.

---

## Atributos

### node_id

Identificador único del nodo.

Tipo:

```python
int
```

---

### position

Posición del hueso en coordenadas 3D.

Tipo:

```python
tuple[float, float, float]
```

---

### parent

Referencia al hueso padre.

Tipo:

```python
Bone | None
```

---

### children

Lista de huesos hijos.

Tipo:

```python
list[Bone]
```

---

### length

Longitud del hueso respecto a su padre.

Tipo:

```python
float
```

---

### depth

Profundidad del hueso dentro del árbol.

Tipo:

```python
int
```

---

## Funciones

### get_root_to_leaf_paths()

Obtiene todos los caminos desde la raíz del árbol hasta cada hoja.

Cada camino se representa como una lista de objetos `Bone`.

Devuelve:

```python
list[list[Bone]]
```

---

## Uso

Los objetos `Bone` se generan durante la construcción del árbol esquelético y posteriormente son utilizados por el extractor de características para calcular información topológica y geométrica del modelo.
