"""
skeletonize.py

## Responsabilidad

Generar un curve skeleton a partir de una malla utilizando
los algoritmos de la librería Skeletor.

## Entradas

Objeto trimesh.Trimesh.

## Salidas

Objeto skeletor.Skeleton.

## Dependencias

skeletor

## No hace

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

    return skeletor.skeletonize.by_teasar(
        mesh,
        inv_dist=sampling_dist,
    )


def generate_curve_graph(
    mesh,
    sampling_dist,
    degenerate_threshold=1e-3,
):
    """
    Genera un curve graph simplificado a partir de una malla.

    Flujo:

        mesh
          ↓
        TEASAR
          ↓
        Skeletor Skeleton
          ↓
        NetworkX Graph
          ↓
        simplificación

    Parameters
    ----------
    mesh : trimesh.Trimesh
        Malla a skeletonizar.

    sampling_dist : float
        Distancia de muestreo utilizada por TEASAR.

    degenerate_threshold : float, optional
        Umbral utilizado para eliminar componentes degeneradas.

    Returns
    -------
    networkx.Graph
        Curve graph simplificado.
    """

    from topology.curve_graph import (
        skeleton_to_graph,
        simplify_curve_graph,
    )

    skeleton = generate_skeleton(
        mesh,
        sampling_dist,
    )

    graph = skeleton_to_graph(
        skeleton,
    )

    return simplify_curve_graph(
        graph,
        degenerate_threshold=degenerate_threshold,
    )