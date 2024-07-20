from graph import Graph
from vertex import Vertex
from distance_attentuation import get_attentuated_max_distance
from collision import *
from edge import Edge
import math


# A bucket defines cell, which is influenced by vertices  or edges of graph
class Bucket:
    vertices: list[Vertex] = []
    edges: list[Edge] = []

    def __init__(self):
        self.vertices = []
        self.edges = []

    def add_vertex(self, vertex: Vertex):
        self.vertices.append(vertex)

    def add_edge(self, edge: Edge):
        self.edges.append(edge)


class SpatialHashRange:
    min_val: int = 0
    max_val: int = 0

    def __init__(self, min_val: int, max_val: int):
        self.min_val = min_val
        self.max_val = max_val

    def __str__(self):
        return "[" + str(self.min_val) + ", " + str(self.max_val) + "]"

    def __repr__(self):
        return self.__str__()


class SpatialHashBoundingBox:
    x_range: SpatialHashRange = None
    y_range: SpatialHashRange = None

    def __init__(self, x_range: SpatialHashRange, y_range: SpatialHashRange):
        self.x_range = x_range
        self.y_range = y_range

    def __str__(self):
        return "[" + str(self.x_range) + ", " + str(self.y_range) + "]"

    def __repr__(self):
        return self.__str__()


class SpatialHash:
    line_width: float = 0.0
    cell_size: float = 10.0
    buckets: list[list[Bucket]] = []
    max_cell_count: int = 0

    def __init__(self, line_width: float, cell_size: float, use_weight: bool, graph: Graph):
        self.line_width = line_width
        if self.line_width == 0:
            self.line_width = self.line_width + 0.01

        self.cell_size = cell_size
        if self.cell_size == 0:
            self.cell_size = self.cell_size + 0.1

        self.max_cell_count = int(math.ceil(1.0 / self.cell_size) + 1)

        self.buckets = []
        for line in graph.edges:
            if line is not None:
                self._process_edge(line, use_weight, graph)

        if use_weight:
            for vertex in graph.vertices:
                self._process_vertex(vertex)

    def _process_edge(self, edge: Edge, use_weight: bool, graph: Graph):
        precision = 0.0001
        vertex_start = graph.vertices[edge.start]
        vertex_end = graph.vertices[edge.end]
        vertex_max_weight = max(vertex_start.weight, vertex_end.weight)
        if (not use_weight) or vertex_max_weight > precision:
            distance = self.line_width
            if use_weight:
                distance = get_attentuated_max_distance(vertex_max_weight, self.line_width, 0.0)
            normal = edge.unit.rotateZ(math.pi/2.0)
            p0 = vertex_start.point + normal * distance
            p1 = vertex_start.point - normal * distance
            p2 = vertex_end.point + normal * distance
            p3 = vertex_end.point - normal * distance
            bounding_points = [p0, p1, p2, p3]
#            print(bounding_points)
            # noinspection PyTypeChecker
            bbox = self._get_bounding_box_range(bounding_points)
#            print(bbox)
            for i in range(bbox.x_range.min_val, bbox.x_range.max_val + 1):
                for j in range(bbox.y_range.min_val, bbox.y_range.max_val + 1):
                    min_x = i * self.cell_size
                    min_y = j * self.cell_size
                    max_x = min_x + self.cell_size
                    max_y = min_y + self.cell_size
                    box_points = [vector.obj(x=min_x, y=min_y), vector.obj(x=max_x, y=min_y),
                                  vector.obj(x=min_x, y=max_y), vector.obj(x=max_x, y=max_y)]
                    is_in_bucket = True
                    axles = [
                        (edge.unit, p0),
                        (normal, p0),
                        (vector.obj(x=1.0, y=0.0), box_points[0]),
                        (vector.obj(x=0.0, y=1.0), box_points[0])
                    ]
                    for axle in axles:
                        # noinspection PyTypeChecker
                        box_projection_1 = project_points(bounding_points, axle[0], axle[1])
                        box_projection_2 = project_points(box_points, axle[0], axle[1])
                        if not collides(box_projection_1, box_projection_2):
                            is_in_bucket = False
                            break
                    if is_in_bucket:
                        self.insert_edge_into_bucket(i, j, edge)

    def _process_vertex(self, vertex: Vertex):
        precision = 0.0001
        if vertex.weight > precision:
            # Influenced part is radial, so in test we should also exclude bucket parts out of circle
            # with distance ratio
            distance = get_attentuated_max_distance(vertex.weight, self.line_width, 0.0)
            distance_vector = vector.obj(x=distance, y=distance)
            # noinspection PyTypeChecker
            bbox = self._get_bounding_box_range([vertex.point - distance_vector, vertex.point + distance_vector])
            for i in range(bbox.x_range.min_val, bbox.x_range.max_val + 1):
                for j in range(bbox.y_range.min_val, bbox.y_range.max_val + 1):
                    min_x = i * self.cell_size
                    min_y = j * self.cell_size
                    center_x = min_x + self.cell_size / 2.0
                    center_y = min_y + self.cell_size / 2.0
                    max_x = min_x + self.cell_size
                    max_y = min_y + self.cell_size
                    axle_vector = (vector.obj(x=center_x, y=center_y) - vertex.point)
                    if axle_vector.rho < precision:
                        is_in_bucket = True
                    else:
                        axle = axle_vector.unit()
                        # noinspection PyTypeChecker
                        circle_projection = project_circle(vertex.point, distance, axle, vertex.point)
                        box_points = [vector.obj(x=min_x, y=min_y), vector.obj(x=max_x, y=min_y),
                                      vector.obj(x=min_x, y=max_y), vector.obj(x=max_x, y=max_y)]
                        # noinspection PyTypeChecker
                        box_projection = project_points(box_points, axle, vertex.point)
                        is_in_bucket = collides(circle_projection, box_projection)
                    if is_in_bucket:
                        self.insert_vertex_into_bucket(i, j, vertex)

    def _get_bounding_box_range(self, points: list[vector.VectorObject2D]) -> SpatialHashBoundingBox:
        min_x = 0
        max_x = 0
        min_y = 0
        max_y = 0
        is_set = False
        for point in points:
            if not is_set:
                min_x = point.x
                max_x = point.x
                min_y = point.y
                max_y = point.y
                is_set = True
            else:
                min_x = min(point.x, min_x)
                max_x = max(point.x, max_x)
                min_y = min(point.y, min_y)
                max_y = max(point.y, max_y)

        min_x_index = max(0, int(math.floor(min_x / self.cell_size)))
        max_x_index = max(0, int(math.floor(max_x / self.cell_size)))
        min_y_index = max(0, int(math.floor(min_y / self.cell_size)))
        max_y_index = max(0, int(math.floor(max_y / self.cell_size)))

        i_min_range = self._clamp(min_x_index - 1, 0)
        i_max_range = self._clamp(max_x_index + 1, 1)
        j_min_range = self._clamp(min_y_index - 1, 0)
        j_max_range = self._clamp(max_y_index + 1, 1)

        x_range = SpatialHashRange(i_min_range, i_max_range)
        y_range = SpatialHashRange(j_min_range, j_max_range)
        return SpatialHashBoundingBox(x_range, y_range)

    def _clamp(self, x: int, clamp_min: int) -> int:
        return min(max(clamp_min, x), self.max_cell_count)

    def insert_edge_into_bucket(self, x: int, y: int, line: Edge):
        self.try_create_bucket(x, y)
        self.buckets[x][y].add_edge(line)

    def insert_vertex_into_bucket(self, x: int, y: int, vertex: Vertex):
        self.try_create_bucket(x, y)
        self.buckets[x][y].add_vertex(vertex)

    def get_bucket(self, x_coord: float, y_coord: float) -> Bucket:
        x = int(x_coord / self.cell_size)
        y = int(y_coord / self.cell_size)
        if x < len(self.buckets):
            if y < len(self.buckets[x]):
                #   if (len(self.buckets[x][y]) != 0):
                #       print("Buckets: ", x, " ", y)
                return self.buckets[x][y]
        return Bucket()

    def try_create_bucket(self, x: int, y: int):
        while len(self.buckets) <= x:
            self.buckets.append([])
            # print("=================")
            # print(x, "   ", self.buckets)
        while len(self.buckets[x]) <= y:
            self.buckets[x].append(Bucket())
            # print("===++++++++++====")
            # print(y, "   ", self.buckets)

    def dump(self):
        for x in range(0, len(self.buckets)):
            for y in range(0, len(self.buckets[x])):
                lines = []
                bucket = self.buckets[x][y]
                for edge in bucket.edges:
                    lines.append("E(" + str(edge.start) + "->" + str(edge.end) + ")")
                for vertex in bucket.vertices:
                    lines.append("V(" + str(vertex.point.x) + "," + str(vertex.point.y) + ")")
                print(x, " ", y, ": ", ",".join(lines))
