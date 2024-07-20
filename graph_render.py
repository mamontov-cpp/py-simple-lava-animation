import vector
from spatial_hash import SpatialHash
from graph import Graph
from renderer import Renderer, AntialiasingType


def get_color_sample(x_normal: float, y_normal: float, graph: Graph, spatial_hash: SpatialHash, line_width: float) \
        -> tuple[int, int, int, int]:
    v = vector.obj(x=x_normal, y=y_normal)
    bucket = spatial_hash.get_bucket(x_normal, y_normal)
    for line in bucket.edges:
        vertex_point = graph.vertices[line.start].point
        projection_t = (v-vertex_point).dot(line.unit)
        if (projection_t >= 0) and (projection_t <= line.local_length):
            v_local = vertex_point + line.unit * projection_t
            dist = (v - v_local).rho
            if dist < line_width:
                return 0, 0, 255, 255
    return 0xff, 0xff, 0xff, 0x0


def render_graph(width: int, height: int, graph: Graph, line_width: float, cell_size: float,
                 filename: str):
    print("Building spatial hash")
    spatial_hash = SpatialHash(line_width, cell_size, False, graph)
#    spatial_hash.dump()
    print("Done building spatial hash")
    renderer = Renderer(6, AntialiasingType.SAMPLE_9)
    renderer.set_color_sample_implementation(get_color_sample)
    renderer.render(width, height, graph, spatial_hash, line_width, filename)
