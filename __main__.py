from voronoi_local import *
from graph import Graph
from spatial_hash import SpatialHash
from graph_render import render_graph
from lava_render import render_lava_frame
from random_split_edges import random_split_edges, SplitRange
import random
import sys


def test_graph() -> Graph:
    local_graph = Graph()
    p1 = vector.obj(x=0.25, y=0.5)
    p2 = vector.obj(x=0.75, y=0.5)
    p3 = vector.obj(x=0.75, y=0.25)
    i0 = local_graph.add_point(p1)
    i1 = local_graph.add_point(p2)
    i2 = local_graph.add_point(p3)
    local_graph.add_edge(i0, i1)
    local_graph.add_edge(i1, i2)
    local_graph.source_pivot = [0]
    return local_graph


def make_random_graph() -> Graph:
    points_count = get_point_count_for_voronoi(20, 45)
    print("Point count", points_count)
    voronoi = build_random_voronoi(points_count)
    dump_voronoi(voronoi)
    local_graph = voronoi_to_graph(voronoi, points_count)
    local_graph.set_source_pivot(vector.obj(x=0.5, y=0.5), random.randint(1, 3))
    random_split_edges(local_graph, SplitRange(1, 4), SplitRange(-0.02, 0.02), SplitRange(-0.02, 0.03))
    return local_graph


if __name__ == '__main__':
    if len(sys.argv) > 1:
        random.seed(int(sys.argv[1]))
    graph = make_random_graph()

    cell_size = 0.025
    render_graph(100, 100, graph, 0.01,  cell_size, "test_info.png")
    line_width = 0.03
#    graph.propagate_increment(4.2)
#    render_lava_frame(100, 100, graph, 0.03, cell_size, "test_frame_me_42.png")
    for i in range(0, 60):
        graph.propagate_increment(0.3)
        render_lava_frame(100, 100, graph, 0.03, cell_size, "test_frame_" + str(i) + ".png")
