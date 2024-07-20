import random
import numpy as np
from scipy.spatial import Voronoi
from graph import Graph
import vector


def get_point_count_for_voronoi(min_point_count: int, max_point_count: int) -> int:
    if min_point_count < 0:
        min_point_count = 1
    if max_point_count < 0:
        max_point_count = 1
    if min_point_count > max_point_count:
        min_point_count, max_point_count = max_point_count, min_point_count
    return random.randrange(min_point_count, max_point_count)


def build_random_voronoi(count_points: int) -> Voronoi:
    points = []
    escaped_count_points = count_points
    if escaped_count_points < 0:
        escaped_count_points = 1
    for i in range(0, escaped_count_points):
        points.append([random.random(),random.random()])
    very_large_coordinate_value = 10.0
    points.append([-very_large_coordinate_value, very_large_coordinate_value])
    points.append([very_large_coordinate_value, very_large_coordinate_value])
    points.append([-very_large_coordinate_value, -very_large_coordinate_value])
    points.append([very_large_coordinate_value, -very_large_coordinate_value])
    return Voronoi(np.array(points))


def dump_voronoi(vor: Voronoi):
    print("Vertices:", vor.vertices)
    print("Regions:", vor.regions)
    print("Point region", vor.point_region)
    print("Ridge points", vor.ridge_points)
    print("Ridge vertices", vor.ridge_vertices)


# We need amount of points, since we add new points to voronoi to create new ridges, so we don't count odd points in
# graph.
def voronoi_to_graph(vor: Voronoi, count_points: int) -> Graph:
    def point_in_hash(a: int, b: int, line_hash: dict[int, dict[int, bool]]):
        if a in line_hash:
            if b in line_hash[a]:
                return True
        if b in line_hash:
            if a in line_hash[b]:
                return True
        return False

    def insert_to_hash(a: int, b: int, line_hash: dict[int, dict[int, bool]]):
        if a in line_hash:
            if not (b in line_hash[a]):
                line_hash[a][b] = True
        else:
            line_hash[a] = {b: True}
        if b in line_hash:
            if not (a in line_hash[b]):
                line_hash[b][a] = True
        else:
            line_hash[b] = {a: True}

    def to_point(a) -> vector.VectorObject2D:
        return vector.obj(x=a[0], y=a[1])

    graph = Graph()
    line_by_index = {}
    for point_index in range(0, count_points):
        region_index = vor.point_region[point_index]
        region_info = vor.regions[region_index]
        last_point_index = region_info[len(region_info) - 1]
        for data_index in range(1, len(region_info)):
            index_0 = region_info[data_index - 1]
            index_1 = region_info[data_index]
            point_0 = to_point(vor.vertices[index_0])
            point_1 = to_point(vor.vertices[index_1])
            if not point_in_hash(index_0, index_1, line_by_index):
                graph.add_edge_from_voronoi_diagram(index_0, point_0, index_1, point_1)
                insert_to_hash(index_0, index_1, line_by_index)
        index_0 = region_info[0]
        index_1 = last_point_index
        point_0 = to_point(vor.vertices[index_0])
        point_1 = to_point(vor.vertices[index_1])
        if not point_in_hash(index_0, index_1, line_by_index):
            graph.add_edge_from_voronoi_diagram(index_0, point_0, index_1, point_1)
            insert_to_hash(index_0, index_1, line_by_index)
    return graph
