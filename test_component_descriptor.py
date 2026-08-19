from topology.fbx_geometry import load_fbx_mesh
import numpy as np


def component_descriptor(mesh):
    mesh = mesh.copy()
    mesh.merge_vertices(digits_vertex=6)

    components = mesh.split(
        only_watertight=False
    )

    # PCA GLOBAL

    vertices = np.asarray(
        mesh.vertices,
        dtype=float,
    )

    centered = (
        vertices
        - vertices.mean(axis=0)
    )

    _, _, basis = np.linalg.svd(
        centered,
        full_matrices=False,
    )

    # COMPONENTES

    data = []

    for component in components:

        points = np.asarray(
            component.vertices,
            dtype=float,
        )

        center = (
            points.mean(axis=0)
            - vertices.mean(axis=0)
        )

        center = center @ basis.T

        data.append(
            (
                len(points),
                center,
            )
        )

    # Normalización global

    all_centers = np.asarray(
        [center for _, center in data]
    )

    spans = np.ptp(
        centered @ basis.T,
        axis=0,
    )

    all_centers /= np.maximum(
        spans,
        1e-9,
    )

    data = [
        (
            size,
            center,
        )
        for (size, _), center
        in zip(data, all_centers)
    ]

    return sorted(
        data,
        key=lambda x: x[0],
        reverse=True,
    )


mesh = load_fbx_mesh(
    "/app/skeletons/Bear.FBX"
)

data = component_descriptor(mesh)

for i, (size, center) in enumerate(data[:20]):

    print(
        f"{i:02d} "
        f"size={size:4d} "
        f"center={np.round(center, 4)}"
    )
