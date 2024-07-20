import vector


class Cutter1D:
    x_min: float = 0.0
    x_max: float = 0.0

    def __init__(self, x_min: float, x_max: float):
        self.x_min = min(x_min, x_max)
        self.x_max = max(x_min, x_max)

    def merge(self, point: float):
        self.x_min = min(self.x_min, point)
        self.x_max = max(self.x_max, point)


def collides_1d(x11: float, x12: float, x21: float, x22: float) -> bool:
    x1_min = min(x11, x12)
    x1_max = max(x11, x12)
    x2_min = min(x21, x22)
    x2_max = max(x21, x22)
    return x2_min <= x1_max and x2_max >= x1_min


def collides(c1: Cutter1D, c2: Cutter1D) -> bool:
    return collides_1d(c1.x_min, c1.x_max, c2.x_min, c2.x_max)


def project_circle(center: vector.VectorObject2D,
                   radius: float,
                   axle_unit: vector.VectorObject2D,
                   axle_pivot: vector.VectorObject2D) -> Cutter1D:
    point_data = (center - axle_pivot).dot(axle_unit)
    return Cutter1D(point_data - radius, point_data + radius)


def project_points(points: list[vector.VectorObject2D],
                   axle_unit: vector.VectorObject2D,
                   axle_pivot: vector.VectorObject2D) -> Cutter1D:
    if len(points) == 0:
        return Cutter1D(0.0, 0.0)
    point_data = (points[0] - axle_pivot).dot(axle_unit)
    result = Cutter1D(point_data, point_data)
    if len(points) > 1:
        for point in points[1:]:
            point_data = (point - axle_pivot).dot(axle_unit)
            result.merge(point_data)
    return result
