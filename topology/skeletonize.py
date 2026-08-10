"""
skeletonize.py

Responsabilidad
---------------

Generar un curve skeleton a partir de una malla utilizando
los algoritmos de la librería Skeletor.

Entradas
--------

Objeto trimesh.Trimesh.

Salidas
-------

Objeto skeletor.Skeleton.

Dependencias
------------

skeletor

No hace
-------

- No carga archivos GLB.
- No preprocesa la malla.
- No realiza postprocesado del esqueleto.
- No exporta resultados.
"""

import skeletor


def generate_skeleton(mesh, sampling_dist):
    """
    Genera un curve skeleton a partir de una malla.

    Parameters
    ----------
    mesh : trimesh.Trimesh
        Objeto trimesh.Trimesh.

    sampling_dist : float
        Distancia de muestreo utilizada por el algoritmo.

    Returns
    -------
    skeletor.Skeleton
        Esqueleto generado.
    """

    return skeletor.skeletonize.vertex_cluster.by_vertex_clusters(
        mesh,
        sampling_dist=sampling_dist,
    )