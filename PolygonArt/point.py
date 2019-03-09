import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.adjacent = list()

    def __lt__(self, other):
        if self.x == other.x:
            return self.y < other.y
        return self.x < other.x

    def __gt__(self, other):
        if self.x == other.x:
            return self.y > other.y
        return self.x > other.x

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    # hopefully, this method will become obsolete later on,
    # when we can just insert new points in the correct position.
    # implement a linked list containing adjacent points?
    def sort_adjacent(self):
        # sort by angle relative to self in clockwise order
        self.adjacent.sort(key=lambda other: math.atan2(other.y - self.y, other.x - self.x))

    # make sure adjacent points are sorted before calling this!
    def adjacent_tris(self):
        num_adj = len(self.adjacent)
        output = []
        for i in range(num_adj):
            p1 = self.adjacent[i]
            p2 = self.adjacent[(i + 1) % num_adj]

            # make sure points are not a straight vertical or horizontal line
            # i.e. on the edge of the image
            if not (p1.x == p2.x == self.x or p1.y == p2.y == self.y):
                output.append([self, p1, p2])

        return output

    # make sure adjacent points are sorted before calling this!
    def get_test_coords(self, shift_size):
        if shift_size <= 0 or shift_size >= 1:
            print("Error: shift_size is not within the interval (0.0, 1.0)")
            return None

        i_coords = (self.x, self.y)

        # output[0] is just the original coordinates, the rest are new
        output = [i_coords]
        num_adj = len(self.adjacent)

        up_y = None
        down_y = None
        left_x = None
        right_x = None

        for i in range(num_adj):
            p1 = self.adjacent[i]
            p2 = self.adjacent[(i + 1) % num_adj]

            v_crossing = vertical_crossing(p1, p2, i_coords[0])
            h_crossing = horizontal_crossing(p1, p2, i_coords[1])

            if left_x < h_crossing < i_coords[0]:
                left_x = h_crossing
            elif i_coords[0] < h_crossing < right_x:
                right_x = h_crossing

            if up_y < v_crossing < i_coords[1]:
                left_x = h_crossing
            elif i_coords[1] < v_crossing < down_y:
                left_x = h_crossing


        return output

    def on_edge(self, image_w, image_h):
        return self.x_locked(image_w) or self.y_locked(image_h)

    def x_locked(self, image_w):
        return self.x == image_w or self.x == 0

    def y_locked(self, image_h):
            return self.y == image_h or self.y == 0


# from the perspective of the image,
# this looks like the normal slope, but flipped over a horizontal axis
def slope(p1, p2):
    if p1.x == p2.x:
        return math.inf
    return (p1.y - p2.y) / (p1.x - p2.x)


# given the vertical line x = "x",
# at what y-value will the line of p1 and p2 cross it?
def vertical_crossing(p1, p2, x):
    s = slope(p1, p2)
    if s == math.inf:
        return None
    return p1.y + s * (x - p1.x)


# given the horizontal line y = "y",
# at what x-value will the line of p1 and p2 cross it?
def horizontal_crossing(p1, p2, y):
    s = slope(p1, p2)
    if s == 0:
        return None
    return p1.x + 1/s * (y - p1.y)
