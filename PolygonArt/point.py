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
    # returns an array with four points, one in each direction
    def get_test_coords(self, shift_size):
        if shift_size <= 0 or shift_size >= 1:
            print("Error: shift_size is not within the interval (0.0, 1.0)")
            return None

        output = []
        num_adj = len(self.adjacent)

        up_y = None
        down_y = None
        left_x = None
        right_x = None

        for i in range(num_adj):
            p1 = self.adjacent[i]
            p2 = self.adjacent[(i + 1) % num_adj]

            v_crossing = vertical_crossing(p1, p2, self.x)
            h_crossing = horizontal_crossing(p1, p2, self.y)

            if h_crossing is not None:
                if (left_x is None or left_x <= h_crossing) and h_crossing < self.x:
                    left_x = h_crossing
                elif (right_x is None or right_x >= h_crossing) and h_crossing > self.x:
                    right_x = h_crossing
                # else:
                    # print("Error: point is directly on a line")

            if v_crossing is not None:
                if (up_y is None or up_y <= v_crossing) and v_crossing < self.y:
                    up_y = v_crossing
                elif (down_y is None or down_y >= v_crossing) and v_crossing > self.y:
                    down_y = v_crossing
                # else:
                    # print("Error: point is directly on a line")

        # UP, RIGHT, DOWN, LEFT
        output.append((self.x, self.y + (up_y - self.y) * shift_size))
        output.append((self.x + (right_x - self.x) * shift_size, self.y))
        output.append((self.x, self.y + (down_y - self.y) * shift_size))
        output.append((self.x + (left_x - self.x) * shift_size, self.y))

        return output

    # make sure adjacent points are sorted before calling this!
    # negative h_push pushes the point left, positive h_push pushes it right
    # negative v_push pushes the point up, positive v_push pushes it down
    def get_final_coords(self, v_push, h_push, shift_percent):

        # for some reason when h_push is zero it makes intersection return None (regardless of y?) so
        if h_push == 0:
            return self.x, self.y

        num_adj = len(self.adjacent)

        closest_intersect = None

        for i in range(num_adj):
            p1 = self.adjacent[i]
            p2 = self.adjacent[(i + 1) % num_adj]

            intersect = intersection((p1.x, p1.y), (p2.x, p2.y), (self.x, self.y), (self.x + h_push, self.y + v_push))

            if intersect is not None:
                if (h_push < 0 and intersect[0] < self.x and
                   (closest_intersect is None or intersect[0] > closest_intersect[0])) or\
                   (h_push > 0 and intersect[0] > self.x and
                   (closest_intersect is None or intersect[0] < closest_intersect[0])):
                    closest_intersect = intersect

        if closest_intersect is None:
            print("ERROR: None intersect:", "\n", h_push, v_push, "\n", self.x, self.y)
            for a in self.adjacent:
                print(a)

        return vector_interpolate(
            (self.x, self.y), closest_intersect, shift_percent
        )

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


# basic algorithm found online, uses determinants
def intersection(l1p1, l1p2, l2p1, l2p2):
    a1 = l1p2[1] - l1p1[1]
    b1 = l1p1[0] - l1p2[0]
    c1 = a1 * l1p1[0] + b1 * l1p1[1]

    a2 = l2p2[1] - l2p1[1]
    b2 = l2p1[0] - l2p2[0]
    c2 = a2 * l2p1[0] + b2 * l2p1[1]

    determinant = a1 * b2 - a2 * b1

    if determinant == 0:
        return None
    else:
        x = (b2 * c1 - b1 * c2) / determinant
        y = (a1 * c2 - a2 * c1) / determinant
        return x, y


def segment_intersection(s1p1, s1p2, s2p1, s2p2):
    intersect = intersection(s1p1, s1p2, s2p1, s2p2)

    lower = max(min(s1p1[0], s1p2[0]), min(s2p1[0], s2p2[0]))
    upper = min(max(s1p1[0], s1p2[0]), max(s2p1[0], s2p2[0]))

    return intersect if lower <= intersect[0] <= upper else None


def vector_interpolate(start_point, end_point, percent):
    return start_point[0] + (end_point[0] - start_point[0]) * percent,\
        start_point[1] + (end_point[1] - start_point[1]) * percent
