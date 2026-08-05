"""
preprocess.py

Responsabilidad
-------------------
Cargar la geometría de un modelo GLB y obtener una única malla
que será utilizada en las siguientes etapas del pipeline.

Entradas
-------------------
Ruta de un archivo GLB.

Salidas
-------------------
Objeto trimesh.Trimesh.

Dependencias
-------------------
trimesh

No hace
-------------------
- No skeletoniza la geometría.
- No genera huesos.
- No exporta resultados.
"""

import trimesh


def load_mesh(glb_path):
    """
    Carga la geometría de un modelo GLB.

    Parametros
    -------------------

    glb_path
        Ruta del modelo GLB.

    Retorna
    -------------------

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
        # Caso 2.1: la escena contiene una única malla.
        if len(meshes) == 1:
            return meshes[0]
        
        # Caso 2.2: la escena contiene múltiples mallas.
        return trimesh.util.concatenate(meshes)

    raise TypeError(
        f"Tipo de geometría no soportado: {type(geometry)}"
    )

def validate_mesh(mesh):
    """
    Valida la malla cargada.

    Parametros
    -------------------

    mesh
        Malla a validar.

    Retorna
    -------------------

    bool
        True si la malla es válida, de lo contrario lanza una excepción.
    """

    if len(mesh.vertices) == 0:
        raise ValueError("La malla no contiene vértices.")
    
    if len(mesh.faces) == 0:
        raise ValueError("La malla no contiene caras.")
    
    return True

def fix_mesh(mesh):
    """
    Aplica el preprocesamiento de la malla recomendado por Skeletor.
    """
    
    pass