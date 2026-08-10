"""
loader.py

Responsabilidad
---------------

Cargar un modelo GLB y comprobar si ya contiene
un esqueleto (skin) definido.

Entradas
--------

Ruta de un archivo GLB.

Salidas
-------

Objeto GLTF cargado y comprobación de si contiene
un skin.

Dependencias
------------

pygltflib

No hace
-------

- No preprocesa la malla.
- No skeletoniza la geometría.
- No exporta resultados.
"""

from pygltflib import GLTF2


def load_glb(glb_path):
    """
    Carga un archivo GLB.

    Parameters
    ----------
    glb_path : str
        Ruta del archivo GLB.

    Returns
    -------
    GLTF2
        Objeto GLTF cargado.
    """

    return GLTF2().load(glb_path)


def has_skin(gltf):
    """
    Comprueba si un modelo GLB contiene un skin.

    Parameters
    ----------
    gltf : GLTF2
        Objeto GLTF cargado.

    Returns
    -------
    bool
        True si el modelo contiene al menos un skin.
        False en caso contrario.
    """

    return bool(gltf.skins)