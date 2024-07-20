from intensity import avg_color, intensity_to_color, intensity
import vector
import math
from distance_attentuation import *
from spatial_hash import SpatialHash
from graph import Graph
from renderer import Renderer


def get_color_sample(x_normal: float, y_normal: float, graph: Graph, spatial_hash: SpatialHash, line_width: float) \
        -> tuple[int, int, int, int]:
    v = vector.obj(x=x_normal, y=y_normal)
    max_intensity = 0.0
    max_saturation_intensity = 3.0
    precision = 0.001
    bucket = spatial_hash.get_bucket(x_normal, y_normal)
    for vertex in bucket.vertices:
        #  Short-circuit if overly saturated already
        if max_intensity >= max_saturation_intensity:
            break
        line_width_normalized = get_attentuated_max_distance(vertex.weight, line_width, 0.0)
        distance = (v - vertex.point).rho
        intensity_from_start = intensity(vertex.weight, distance, line_width_normalized)
        if intensity_from_start > max_intensity:
            max_intensity = intensity_from_start

    for line in bucket.edges:
        #  Short-circuit if overly saturated already
        if max_intensity >= max_saturation_intensity:
            break
        start_vertex = graph.vertices[line.start]
        end_vertex = graph.vertices[line.end]

        projection_t = (v-start_vertex.point).dot(line.unit)
        if (projection_t >= 0) and (projection_t <= line.local_length):
            distance_ratio = projection_t / line.local_length
            v_local = start_vertex.point + line.unit * projection_t
            dist = (v - v_local).rho
            if start_vertex.weight > precision:
                start_max_line_width = get_attentuated_max_distance(start_vertex.weight, line_width, distance_ratio)
                line_intensity_from_start = intensity(start_vertex.weight, dist, start_max_line_width)
                if line_intensity_from_start > max_intensity:
                    max_intensity = line_intensity_from_start
            if end_vertex.weight > precision:
                end_max_line_width = get_attentuated_max_distance(end_vertex.weight, line_width, 1.0 - distance_ratio)
                line_intensity_from_end = intensity(end_vertex.weight, dist, end_max_line_width)
                if line_intensity_from_end > max_intensity:
                    max_intensity = line_intensity_from_end
    return intensity_to_color(max_intensity)


def render_lava_frame(width: int, height: int, graph: Graph, line_width: float, cell_size: float,
                      filename: str):
    print("Building spatial hash")
    spatial_hash = SpatialHash(line_width, cell_size, True, graph)
    #    spatial_hash.dump()
    print("Done building spatial hash")
    renderer = Renderer()
    renderer.set_color_sample_implementation(get_color_sample)
    renderer.render(width, height, graph, spatial_hash, line_width, filename)
