import vector


class Edge:
    start: int = 0
    end: int = 0

    unit: vector.VectorObject2D = None
    local_length: float = 0.0

    resistance: float = 0.0

    def __init__(self, start: vector.VectorObject2D, end: vector.VectorObject2D):
        dst = (end - start)
        # noinspection PyTypeChecker
        self.unit = dst.unit()
        self.local_length = dst.dot(self.unit)

        self.start = 0
        self.end = 0
        length_meter = 0.25  # it's arbitrary value, to define edge resistance by value 1
        self.resistance = self.local_length / length_meter

    def __str__(self):
        return str((self.start, self.end, self.unit, self.local_length, self.resistance))

    def __repr__(self):
        return self.__str__()

    def dump(self):
        print("Edge start:", self.start, " end: ", self.end, "  direction:", self.unit, " length_max:",
              self.local_length)
