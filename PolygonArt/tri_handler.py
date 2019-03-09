from point import Point, slope
import math
import statistics as stat
from enum import Enum


class Direction(Enum):
    NEUTRAL = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class TriHandler:

    def __init__(self, pixels):
        # pixels is a list with dimensions [height][width*3]
        # the second dimension stores the RGB for each pixel in the row
        self.pixels = pixels
        self.width = int(len(pixels[0])/3)
        self.height = len(pixels)
        # points is a list of points (with references to other points)
        self.points = list()
        # tris is a list of 3-lists of points
        self.tris = list()

    def get_tris(self, shift_size, adjust_iterations):
        self.initialize()
        self.adjust_points(shift_size, adjust_iterations)
        return list(self.tris)

    def initialize(self):
        side = 25

        true_sx = self.width / (self.width // side)
        true_sy = self.height / (self.height // side)

        # find the width and height in units of one "side," or "square" if you prefer
        s_width = self.width // side
        s_height = self.height // side

        # 640x958

        # adding one to x and y ranges to account for the points on the edge
        t_points = [[Point(x * true_sx, y * true_sy) for x in range(s_width + 1)]
                    for y in range(s_height + 1)]

        for y in range(s_height):
            for x in range(s_width):
                o = t_points[y][x]
                r = t_points[y][x + 1]
                d = t_points[y + 1][x]
                dr = t_points[y + 1][x + 1]

                self.add_tri(o, r, dr)
                self.add_tri(o, d, dr)
                add_edge(o, r)
                add_edge(o, dr)
                add_edge(o, d)

        for y in range(s_height):
            add_edge(t_points[y][s_width], t_points[y + 1][s_width])
        for x in range(s_width):
            add_edge(t_points[s_height][x], t_points[s_height][x + 1])

        for r in t_points:
            for p in r:
                self.points.append(p)

    # takes three x,y tuples representing points
    # make sure to add points to self.points and call addEdge before or after calling this
    def add_tri(self, p1, p2, p3):
        if p1 == p2 or p2 == p3 or p3 == p1:
            print("Error: two or more points in tri were identical")
            return
        self.tris.append([p1, p2, p3])

    def adjust_points(self, shift_size, num_iter):
        for iteration in range(num_iter):
            print("Iteration", (iteration + 1))
            for point in self.points:
                if not point.on_edge(self.width, self.height):
                    a_tris = point.adjacent_tris()
                    m_colors = []  # parallel array for triangle colors
                    # we simplify by assuming initial median colors, calculating them one time rather than five
                    for i in range(len(a_tris)):
                        pix = pixels_in_tri(a_tris[i])
                        m_colors.append(self.median_color(pix))

                    test_coords = point.cardinal_coords(shift_size)

                    least_v = self.net_variance(a_tris, m_colors)
                    best_d = Direction.NEUTRAL
                    for d in Direction:
                        if d is not Direction.NEUTRAL:
                            vector = d.value
                            point.x = old_coords[0] + shift_size * vector[0]
                            point.y = old_coords[1] + shift_size * vector[1]
                            variance = self.net_variance(a_tris, m_colors)
                            if variance < least_v:
                                least_v = variance
                                best_d = d

                    vector = best_d.value
                    point.x = old_coords[0] + shift_size * vector[0]
                    point.y = old_coords[1] + shift_size * vector[1]

    def net_variance(self, tris, colors):
        output = 0

        for i in range(len(tris)):
            med = colors[i]
            if med:
                this_var = 0
                pix = pixels_in_tri(tris[i])
                if len(pix) != 0:
                    for p in pix:
                        color = self.get_color(p)
                        if color:
                            this_var += math.pow(color[0] - med[0], 2)
                            this_var += math.pow(color[1] - med[1], 2)
                            this_var += math.pow(color[2] - med[2], 2)
                    output += this_var / len(pix)
        return output

    def median_color(self, pix):
        if len(pix) == 0:
            return None
        r = []
        g = []
        b = []
        for p in pix:
            color = self.get_color(p)
            if color:
                r.append(color[0])
                g.append(color[1])
                b.append(color[2])
        return int(stat.median(r)), int(stat.median(g)), int(stat.median(b))

    def get_color(self, point):
        try:
            s = point[0] * 3
            r = self.pixels[point[1]]
            return r[s], r[s+1], r[s+2]
        except IndexError:
            print("Error: point %d, %d out of range" % (point[0], point[1]))
            return None


def add_edge(p1, p2):
    p1.adjacent.append(p2)
    p2.adjacent.append(p1)


def pixels_in_tri(tri):
    tri.sort()
    x_cutoff = tri[1].x
    common_slope = slope(tri[0], tri[2])
    slope1 = slope(tri[0], tri[1])
    slope2 = slope(tri[1], tri[2])
    return \
        pixels_in_half_tri(tri[0], common_slope, slope1, x_cutoff) + \
        pixels_in_half_tri(tri[2], common_slope, slope2, x_cutoff)


def pixels_in_half_tri(offset_origin, unordered_slope1, unordered_slope2, offset_x_cutoff):
    # takes the initial coordinates and translates them to a space
    # in which (0, 0) is the center of the top left pixel
    origin_x = offset_origin.x - .5
    origin_y = offset_origin.y - .5
    x_cutoff = offset_x_cutoff - .5

    # sorts by more positive and less positive slopes
    if unordered_slope1 > unordered_slope2:
        more_p_slope = unordered_slope1
        less_p_slope = unordered_slope2
    else:
        more_p_slope = unordered_slope2
        less_p_slope = unordered_slope1

    out = list()

    # if x_cutoff == origin_x, it will return no points
    if x_cutoff > origin_x:  # iterates right starting from the left corner
        for x in range(math.ceil(origin_x), math.ceil(x_cutoff)):
            for y in range(math.ceil(origin_y + less_p_slope*(x - origin_x)),
                           math.ceil(origin_y + more_p_slope*(x - origin_x))):
                out.append((x, y))
    elif x_cutoff < origin_x:  # iterates right starting from the flat edge on the left
        for x in range(math.ceil(x_cutoff), math.ceil(origin_x)):
            for y in range(math.ceil(origin_y + more_p_slope*(x - origin_x)),
                           math.ceil(origin_y + less_p_slope*(x - origin_x))):
                out.append((x, y))
    return out

