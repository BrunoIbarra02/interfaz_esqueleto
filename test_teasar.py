import skeletor

from topology.fbx_geometry import load_fbx_mesh


mesh = load_fbx_mesh(
    "/app/skeletons/Bear.FBX"
)

mesh.merge_vertices(
    digits_vertex=6
)

print(
    "mesh vertices:",
    len(mesh.vertices)
)

for value in [
    0.01,
    0.05,
    0.1,
    0.5,
    1.0,
    2.0,
    5.0,
]:

    skeleton = skeletor.skeletonize.by_teasar(
        mesh,
        inv_dist=value,
    )

    graph = skeleton.get_graph()

    print(
        f"inv_dist={value}: "
        f"nodes={graph.number_of_nodes()} "
        f"edges={graph.number_of_edges()}"
    )
