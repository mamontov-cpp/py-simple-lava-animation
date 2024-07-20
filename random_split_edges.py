from graph import Graph
from edge import Edge
from vertex import Vertex
import random
import vector
import math


class SplitRange:
    min_val: float | int
    max_val: float | int

    def __init__(self, min_val: float | int, max_val: float | int):
        if min_val > max_val:
            self.max_val = min_val
            self.min_val = max_val
        else:
            self.min_val = min_val
            self.max_val = max_val

    def get_random_value(self) -> float | int:
        if self.max_val == self.min_val:
            return self.min_val
        else:
            if isinstance(self.max_val, int) and isinstance(self.min_val, int):
                return random.randrange(self.min_val, self.max_val)
            else:
                return random.random() * (self.max_val - self.min_val) + self.min_val


def random_split_edges(graph: Graph,
                       split_count_range: SplitRange,
                       deviation_range: SplitRange,
                       t_deviation_range: SplitRange
                       ):
    edge_count = len(graph.edges)
    for i in range(0, edge_count):
        edge = graph.edge(i)
        if edge is not None:
            split_count = split_count_range.get_random_value()
            if split_count > 0:
                index_first = edge.start
                index_second = edge.end
                graph.remove_edge(i)
                unit = edge.unit
                normal = unit.rotateZ(math.pi/2.0)
                t_max = edge.local_length
                ts = [0]
                t_accumulated = 0
                for t_index in range(0, split_count):
                    val = 1.0 / (split_count + 1) + t_deviation_range.get_random_value()
                    t_accumulated += val
                    ts.append(t_accumulated)
                ts.append(1)
                start_point = graph.vertices[index_first].point
                last_point_graph_index = index_first
                for index in range(1, len(ts)):
                    t1 = ts[index]
                    current_point = start_point + unit * (t1 * t_max)
                    current_index = index_second
                    if index != len(ts) - 1:
                        current_point = current_point + normal * deviation_range.get_random_value()
                        current_index = graph.add_point(current_point)
                    graph.add_edge(last_point_graph_index, current_index)
                    last_point_graph_index = current_index
