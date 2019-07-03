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
        self.sorted = False  # marks whether points have been sorted by id (sorting is not always necessary)

    def __eq__(self, other):
        if not self.sorted:
            self.sort_by_id()
        return other.points == self.points

    def __hash__(self):
        if not self.sorted:
            self.sort_by_id()
        return hash((self.points[0], self.points[1], self.points[2]))

    def sort_by_id(self):
        if self.points[1].id > self.points[2].id:
            self.swap(1, 2)
        if self.points[0].id > self.points[1].id:
            self.swap(0, 1)
        if self.points[1].id > self.points[2].id:
            self.swap(1, 2)
        self.sorted = True

    def swap(self, i1, i2):
        temp = self.points[i1]
        self.points[i1] = self.points[i2]
        self.points[i2] = temp

    def get_points(self):
        return self.points.copy()  # is copying actually necessary? I'm not sure.
