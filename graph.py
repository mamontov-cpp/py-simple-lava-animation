from edge import Edge
from vertex import Vertex
import vector
import math


def precision_equal(a: float, b: float) -> bool:
    precision = 0.001
    return abs(a - b) < precision


class Graph:
    vertices: list[Vertex] = []
    voronoi_vertex_index_to_current_vertex_index: dict[int, int] = {}
    vertex_to_edge_start: dict[int, list[int]] = {}  # Maps vertex index to index of edge start
    vertex_to_edge_end: dict[int, list[int]] = {}  # Maps vertex index to index of edge end
    edges: list[Edge|None] = []  # List of edge data for graph
    source_pivot: list[int] = []  # A pivot for propagating changes to arc data

    def __init__(self):
        self.vertices = []
        self.voronoi_vertex_index_to_current_vertex_index = {}
        self.vertex_to_edge_start = {}
        self.vertex_to_edge_end = {}
        self.edges = []
        self.source_pivot = []

    def add_point_from_voronoi_diagram(self, index: int, point: vector.VectorObject2D) -> int:
        if index in self.voronoi_vertex_index_to_current_vertex_index:
            my_index = self.voronoi_vertex_index_to_current_vertex_index[index]
        else:
            my_index = len(self.vertices)
            self.voronoi_vertex_index_to_current_vertex_index[index] = my_index
            self.vertices.append(Vertex(point))
        return my_index

    def add_point(self, point: vector.VectorObject2D) -> int:
        my_index = len(self.vertices)
        self.vertices.append(Vertex(point))
        return my_index

    def add_edge_from_voronoi_diagram(self, index_0: int, point_0: vector.VectorObject2D, index_1: int, point_1: vector.VectorObject2D) -> int:
        i0 = self.add_point_from_voronoi_diagram(index_0, point_0)
        i1 = self.add_point_from_voronoi_diagram(index_1, point_1)
        return self.add_edge(i0, i1)

    def add_edge(self, graph_vertex_index_0: int, graph_vertex_index_1: int) -> int:
        edge_index = len(self.edges)
        if graph_vertex_index_0 not in self.vertex_to_edge_start:
            self.vertex_to_edge_start[graph_vertex_index_0] = []
        if graph_vertex_index_1 not in self.vertex_to_edge_end:
            self.vertex_to_edge_end[graph_vertex_index_1] = []
        self.vertex_to_edge_start[graph_vertex_index_0].append(edge_index)
        self.vertex_to_edge_end[graph_vertex_index_1].append(edge_index)

        start_vertex = self.vertices[graph_vertex_index_0]
        end_vertex = self.vertices[graph_vertex_index_1]

        edge = Edge(start_vertex.point, end_vertex.point)
        edge.start = graph_vertex_index_0
        edge.end = graph_vertex_index_1

        self.edges.append(edge)
        return edge_index

    def dump(self):
        print("Graph")
        print("Vertices: ", self.vertices)
        print("VertexToEdgeStart: ", self.vertex_to_edge_start)
        print("VertexToEdgeEnd: ", self.vertex_to_edge_end)
        print("Edges: ", self.edges)
        print("Pivot: ", self.source_pivot)

    def edge(self, index: int) -> Edge|None:
        return self.edges[index]

    def remove_edge(self, index: int):
        edge = self.edge(index)
        self.edges[index] = None
        self.vertex_to_edge_start[edge.start].remove(index)
        self.vertex_to_edge_end[edge.end].remove(index)

    # Set source pivot to count nearest points to specified point
    def set_source_pivot(self, center: vector.VectorObject2D, count: int):
        array_to_sort = []
        if count <= 0:
            count = 1
        for i in range(0, len(self.vertices)):
            # noinspection PyUnresolvedReferences
            dst = (self.vertices[i].point - center).rho
            array_to_sort.append((i, dst))
        array_to_sort.sort(key=lambda x: x[1])
        cnt = min(len(array_to_sort), count)
        self.source_pivot = []
        for i in range(0, cnt):
            self.source_pivot.append(array_to_sort[i][0])

    def propagate_increment(self, increment: float):
        current_queue: list[tuple[int, float]] = []

        for vertex_index in self.source_pivot:
            weight = self.vertices[vertex_index].weight + increment
            current_queue.append((vertex_index, weight))

        while len(current_queue) != 0:
            next_queue = []
            while len(current_queue) != 0:
                vertex_index, weight = current_queue.pop(0)
                vertex = self.vertices[vertex_index]
                if not precision_equal(vertex.weight, weight) and weight > vertex.weight:
                    vertex.weight = weight
                    if vertex_index in self.vertex_to_edge_start:
                        for edge_index in self.vertex_to_edge_start[vertex_index]:
                            edge = self.edges[edge_index]
                            if weight >= edge.resistance:
                                next_queue.append((edge.end, weight - edge.resistance))
                    if vertex_index in self.vertex_to_edge_end:
                        for edge_index in self.vertex_to_edge_end[vertex_index]:
                            edge = self.edges[edge_index]
                            if weight >= edge.resistance:
                                next_queue.append((edge.start, weight - edge.resistance))
            current_queue = next_queue.copy()