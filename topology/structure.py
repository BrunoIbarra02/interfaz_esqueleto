"""
structure.py

Representación estructural simplificada de un Bone Tree.

La estructura identifica los puntos topológicamente relevantes
(raíz, hojas y bifurcaciones) y agrupa los Bones intermedios
en segmentos.

No realiza comparación entre esqueletos.
"""

from dataclasses import dataclass, field

import numpy as np

from topology.bone import Bone


# ============================================================
# LANDMARK
# ============================================================

@dataclass
class Landmark:
    """
    Punto estructural de un esqueleto.

    Un Landmark corresponde a:

    - la raíz;
    - una hoja;
    - una bifurcación.
    """

    bone: Bone

    children: list["Landmark"] = field(
        default_factory=list
    )

    @property
    def position(self):
        """
        Posición global del Landmark.
        """

        return np.asarray(
            self.bone.position,
            dtype=float,
        )


# ============================================================
# SEGMENT
# ============================================================

@dataclass
class Segment:
    """
    Segmento entre dos Landmarks.

    Puede contener uno o varios Bones.
    """

    start: Landmark
    end: Landmark

    bones: list[Bone] = field(
        default_factory=list
    )

    @property
    def length(self):
        """
        Longitud geométrica del recorrido
        entre los dos Landmarks.
        """

        if not self.bones:
            return 0.0

        points = [
            self.start.position
        ]

        points.extend(
            np.asarray(
                bone.position,
                dtype=float,
            )
            for bone in self.bones
        )

        length = 0.0

        for point_a, point_b in zip(
            points,
            points[1:],
        ):

            length += np.linalg.norm(
                point_b - point_a
            )

        return float(length)

    @property
    def bone_count(self):
        """
        Número de Bones contenidos en el segmento.
        """

        return len(self.bones)

    @property
    def direction(self):
        """
        Dirección aproximada del segmento.

        Se calcula desde el Landmark inicial
        hasta el Landmark final.
        """

        vector = (
            self.end.position
            - self.start.position
        )

        length = np.linalg.norm(vector)

        if length == 0:
            return np.zeros(3)

        return vector / length


# ============================================================
# SKELETON STRUCTURE
# ============================================================

@dataclass
class SkeletonStructure:
    """
    Representación estructural comprimida
    de un Bone Tree.
    """

    root: Landmark

    segments: list[Segment] = field(
        default_factory=list
    )

    @property
    def landmark_count(self):
        """
        Número de Landmarks de la estructura.
        """

        landmarks = set()

        for segment in self.segments:

            landmarks.add(
                id(segment.start.bone)
            )

            landmarks.add(
                id(segment.end.bone)
            )

        landmarks.add(
            id(self.root.bone)
        )

        return len(landmarks)

    @property
    def segment_count(self):
        """
        Número de segmentos estructurales.
        """

        return len(self.segments)


# ============================================================
# FOREST STRUCTURE
# ============================================================

@dataclass
class ForestStructure:
    """
    Representación estructural de un Bone Forest.

    Cada raíz del bosque se convierte en una
    SkeletonStructure independiente.
    """

    structures: list[SkeletonStructure] = field(
        default_factory=list
    )

    @property
    def root_count(self):
        """
        Número de árboles del bosque.
        """

        return len(self.structures)

    @property
    def landmark_count(self):
        """
        Número total de Landmarks del bosque.
        """

        return sum(
            structure.landmark_count
            for structure in self.structures
        )

    @property
    def segment_count(self):
        """
        Número total de segmentos del bosque.
        """

        return sum(
            structure.segment_count
            for structure in self.structures
        )

# ============================================================
# LANDMARK TEST
# ============================================================

def is_landmark(bone):
    """
    Determina si un Bone es estructuralmente relevante.

    Son Landmarks:

    - la raíz;
    - las hojas;
    - las bifurcaciones.
    """

    return (
        bone.parent is None
        or len(bone.children) != 1
    )


# ============================================================
# BUILD STRUCTURE
# ============================================================

def build_structure(root):
    """
    Convierte un Bone Tree en una SkeletonStructure.

    Los Bones intermedios con un único hijo no se eliminan
    de la información del segmento: quedan almacenados en
    Segment.bones.
    """

    root_landmark = Landmark(
        bone=root
    )

    structure = SkeletonStructure(
        root=root_landmark
    )

    def walk(landmark):

        for child in landmark.bone.children:

            current = child

            bones = []

            while not is_landmark(current):

                bones.append(current)

                if len(current.children) != 1:
                    raise ValueError(
                        "Bone intermedio con "
                        "estructura inválida."
                    )

                current = current.children[0]

            # El Landmark final también forma parte
            # del recorrido del segmento.
            bones.append(current)

            child_landmark = Landmark(
                bone=current
            )

            landmark.children.append(
                child_landmark
            )

            segment = Segment(
                start=landmark,
                end=child_landmark,
                bones=bones,
            )

            structure.segments.append(
                segment
            )

            walk(
                child_landmark
            )

    walk(root_landmark)

    return structure

# ============================================================
# BUILD FOREST STRUCTURE
# ============================================================

def build_forest_structure(roots):
    """
    Convierte un Bone Forest en una ForestStructure.

    Cada raíz representa un árbol independiente.
    """

    structures = []

    for root in roots:

        structures.append(
            build_structure(root)
        )

    return ForestStructure(
        structures=structures
    )