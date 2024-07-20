from graph import Graph
import numpy as np
import random
import vector
import math
import threading
from PIL import Image, ImageDraw
from scipy.spatial import Voronoi, voronoi_plot_2d


splitted_lines = []
deviation_range = [-0.03, 0.03]
split_count_range = [1, 4]
width_range = [1,1]

# TODO: MOVE TO MODULE AND REWORK, AS GRAPH TRANSFORM
t_deviation = [-0.02, 0.03]
for line_index in range(0, len(lines)):
    line = lines[line_index]
    arc_index = line[2]
    a = vector.obj(x=line[0][0], y=line[0][1])
    b = vector.obj(x=line[1][0], y=line[1][1])
    split_count = random.randrange(split_count_range[0], split_count_range[1])
    line_width = int(random.random() * (width_range[1] - width_range[0]) + width_range[0])
    if split_count == 0:
        splitted_lines.append([ [line[0][0],line[0][1]], [line[1][0],line[1][1]], line_width, arc_index])
    else:
        arc = graph.get_arc(arc_index)
        index_first = arc.start
        index_second = arc.end
        graph.remove_arc(arc_index)
        unit = (b-a).unit()
        normal = unit.rotateZ(math.pi/2.0)
        t_max = (b-a).dot(unit)
        ts = [0]
        t_accumulated = 0
        for t_index in range(0, split_count):
            val = 1.0 / (split_count + 1) + random.random() * (t_deviation[1] - t_deviation[0]) + t_deviation[0]
            t_accumulated += val
            ts.append(t_accumulated)
        ts.append(1)
        last_point = [line[0][0],line[0][1]]
        last_point_graph_index = index_first
        for index in range(1, len(ts)):
            t1 = ts[index]
            pnt1 = a + unit*t1*t_max
            current_index = index_second
            if index != len(ts) -1:
                pnt1 = pnt1 + normal * (deviation_range[0] + (deviation_range[1] - deviation_range[0]) * random.random())
                current_index = graph.add_non_voronoi_point([float(pnt1.x), float(pnt1.y)])
            arc_index = graph.add_simple_arc(last_point_graph_index, current_index)
            new_local_line = [ [last_point[0],last_point[1]], [pnt1.x,pnt1.y], line_width, arc_index ]
            splitted_lines.append(new_local_line)
            last_point = [pnt1.x, pnt1.y]
            last_point_graph_index = current_index
#        splitted_lines.append([ [line[0][0],line[0][1]], [line[1][0],line[1][1]], line_width  ])
    
lines = splitted_lines
