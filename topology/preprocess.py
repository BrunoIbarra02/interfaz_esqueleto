"""
preprocess.py

Responsabilidad
---------------

Cargar y preparar la geometría de un modelo GLB para
las etapas posteriores de la Vía 2.

Entradas
--------

Ruta de un archivo GLB.

Salidas
-------

Objeto trimesh.Trimesh.

Dependencias
------------

trimesh
"""

import trimesh


def load_mesh(glb_path):
    """
    Carga la geometría de un modelo GLB.

    Parameters
    ----------
    glb_path : str
        Ruta del modelo GLB.

    Returns
    -------
    trimesh.Trimesh
        Malla cargada.
    """

    geometry = trimesh.load(glb_path)

    # Caso 1: el GLB ya contiene una única malla.
    if isinstance(geometry, trimesh.Trimesh):
        return geometry

    # Caso 2: el GLB contiene una escena.
    if isinstance(geometry, trimesh.Scene):

        if len(geometry.geometry) == 0:
            raise ValueError(
                "El GLB no contiene ninguna geometría."
            )

        meshes = []

        for mesh in geometry.geometry.values():

            if isinstance(mesh, trimesh.Trimesh):
                meshes.append(mesh)

        if len(meshes) == 0:
            raise ValueError(
                "La escena no contiene ninguna malla válida."
            )

        # Una única malla.
        if len(meshes) == 1:
            return meshes[0]

        # Múltiples mallas.
        return trimesh.util.concatenate(meshes)

    raise TypeError(
        f"Tipo de geometría no soportado: {type(geometry)}"
    )


def validate_mesh(mesh):
    """
    Valida la malla cargada.

    Parameters
    ----------
    mesh : trimesh.Trimesh
        Malla a validar.

    Returns
    -------
    bool
        True si la malla es válida.
    """

    if len(mesh.vertices) == 0:
        raise ValueError(
            "La malla no contiene vértices."
        )

    if len(mesh.faces) == 0:
        raise ValueError(
            "La malla no contiene caras."
        )

    return True


def fix_mesh(mesh):
    """
    Preprocesa la malla para su uso posterior
    en la skeletonización.

    La configuración concreta se definirá
    posteriormente.
    """

    raise NotImplementedError(
        "Mesh preprocessing not implemented yet."
    )