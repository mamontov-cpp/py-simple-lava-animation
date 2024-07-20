import vector


class Vertex:
    point: vector.VectorObject2D = None
    weight: float = 0.0

    def __init__(self, point: vector.VectorObject2D):
        self.point = point
        self.weight = 0.0

    def __str__(self):
        return str((self.point.x, self.point.y, self.weight))

    def __repr__(self):
        return self.__str__()

    def dump(self):
        print("Point x:", self.point.x, " y: ", self.point.y, "  weight:", self.weight)
