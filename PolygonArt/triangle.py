from point import Point


class Triangle:
    def __init__(self, points):
        if isinstance(points[0], tuple):
            points[0] = Point(points[0][0], points[0][1])
        if isinstance(points[1], tuple):
            points[1] = Point(points[1][0], points[1][1])
        if isinstance(points[2], tuple):
            points[2] = Point(points[2][0], points[2][1])

        self.points = points  # list of Point objects

    def __eq__(self, other):
        return other.points == self.points

    def __hash__(self):
        return hash((self.points[0], self.points[1], self.points[2]))

    def get_p(self, index):
        return self.points[index]
