"""
preprocess.py

Responsabilidad:

- Validar una malla trimesh.
- Realizar una limpieza geométrica conservadora.

No hace:

- No carga GLB.
- No decide qué componentes anatómicos conservar.
- No elimina componentes por tamaño.
- No skeletoniza.
- No construye grafos.
- No realiza matching.
- No calcula scores.
"""

import trimesh


# ============================================================
# VALIDATION
# ============================================================

def validate_mesh(mesh):
    """
    Valida que la malla contiene geometría utilizable.

    Parameters
    ----------
    mesh : trimesh.Trimesh
        Malla a validar.

    Returns
    -------
    bool
        True si la malla es válida.
    """

    if not isinstance(
        mesh,
        trimesh.Trimesh,
    ):
        raise TypeError(
            "Se esperaba un objeto trimesh.Trimesh."
        )

    if len(mesh.vertices) == 0:
        raise ValueError(
            "La malla no contiene vértices."
        )

    if len(mesh.faces) == 0:
        raise ValueError(
            "La malla no contiene caras."
        )

    return True


# ============================================================
# CLEAN
# ============================================================

def clean_mesh(mesh):
    """
    Realiza una limpieza geométrica conservadora.

    No elimina componentes desconectados.

    Parameters
    ----------
    mesh : trimesh.Trimesh
        Malla a limpiar.

    Returns
    -------
    trimesh.Trimesh
        Malla limpiada.
    """

    validate_mesh(mesh)

    cleaned = mesh.copy()

    # --------------------------------------------------------
    # Eliminar valores infinitos o NaN.
    # --------------------------------------------------------

    cleaned.remove_infinite_values()

    # --------------------------------------------------------
    # Unificar vértices coincidentes.
    #
    # No aplicamos redondeo ni tolerancia artificial.
    # --------------------------------------------------------

    cleaned.merge_vertices()

    # --------------------------------------------------------
    # Eliminar vértices que hayan quedado sin referencia.
    # --------------------------------------------------------

    cleaned.remove_unreferenced_vertices()

    validate_mesh(cleaned)

    return cleaned


# ============================================================
# PREPROCESS
# ============================================================

def fix_mesh(mesh):
    """
    Prepara una malla para las etapas posteriores.

    Mantiene todos los componentes desconectados.

    Parameters
    ----------
    mesh : trimesh.Trimesh
        Malla obtenida desde topology.loader.

    Returns
    -------
    trimesh.Trimesh
        Malla preparada.
    """

    return clean_mesh(mesh)