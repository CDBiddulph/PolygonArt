from point import Point, slope
import math
import statistics as stat
from enum import Enum
import queue

import poly_renderer as rend


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
        # edge queue is a FIFO queue of 2-tuples of points
        self.edge_queue = queue.Queue()

    def get_rect_tris(self, side, shift_size, adjust_iterations):
        self.rect_initialize(side)
        self.adjust_points(shift_size, adjust_iterations)
        return list(self.tris)

    def get_smart_tris(self, target_v, v_allowance, min_leap,
                       shift_size, adjust_iterations):
        self.smart_initialize(target_v, v_allowance, min_leap)
        self.adjust_points(shift_size, adjust_iterations)
        return list(self.tris)

    def smart_initialize(self, target_v, v_allowance, min_leap):
        self.add_first_tri()

        tri_num = 0
        while not self.edge_queue.empty():
            edge = self.edge_queue.get()
            p1 = edge[0]
            p2 = edge[1]

            

            test_renderer = rend.PolyRenderer(self.pixels, self.tris)
            test_renderer.render('output\\output{0}.png'.format(tri_num))
            test_renderer.variance_render('output\\variance{0}.png'.format(tri_num))
            tri_num += 1

    def add_first_tri(self):
        p1 = Point(0, 0)
        p2 = Point(20, 0)
        p3 = Point(0, 20)

        self.points.append(p1)
        self.points.append(p2)
        self.points.append(p3)

        add_edge(p1, p2)
        add_edge(p2, p3)
        add_edge(p3, p1)

        self.add_tri(p1, p2, p3)

        self.edge_queue.put((p2, p3))

    def rect_initialize(self, side):
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
            # test_renderer = rend.PolyRenderer(self.pixels, self.tris)
            # test_renderer.render('output\iteration{}.png'.format(iteration))
            # test_renderer.variance_render('output\\v_iteration{}.png'.format(iteration))
            # self.print_average_variance()
            # print("Iteration", (iteration + 1))
            for p in range(len(self.points)):
                point = self.points[p]
                if not point.on_edge(self.width, self.height):
                    point.sort_adjacent()

                    a_tris = point.adjacent_tris()
                    m_colors = []  # parallel array for triangle colors

                    # we simplify by assuming initial median colors, calculating them one time rather than five
                    for i in range(len(a_tris)):
                        pix = pixels_in_tri(a_tris[i])
                        m_colors.append(self.median_color(pix))

                    test_coords = point.get_test_coords(shift_size, p)

                    least_v = self.net_variance(a_tris, m_colors)
                    best_coords_i = 0
                    for i in range(1, 4):
                        point.x = test_coords[i][0]
                        point.y = test_coords[i][1]

                        # Does recalculating the median help, and how much does it hurt?
                        # Future research may be necessary.

                        variance = self.net_variance(a_tris, m_colors)
                        if variance < least_v:
                            least_v = variance
                            best_coords_i = i

                    point.x = test_coords[best_coords_i][0]
                    point.y = test_coords[best_coords_i][1]

                    # if best_coords_i != 0:
                    #     test_renderer = rend.PolyRenderer(self.pixels, self.tris)
                    #     test_renderer.render('output\shift{}_{}.png'.format(p, Direction(best_coords_i).name))

    def net_variance(self, tris, colors):
        output = 0

        for i in range(len(tris)):
            median = colors[i]
            if median:
                pix = pixels_in_tri(tris[i])
                if len(pix) != 0:
                    output += self.variance(pix, median)
        return output

    def variance(self, pix, median=None):
        if median is None:
            median = self.median_color(pix)
        squared_sum = 0
        for p in pix:
            color = self.get_color(p)
            if color:
                squared_sum += math.pow(color[0] - median[0], 2)
                squared_sum += math.pow(color[1] - median[1], 2)
                squared_sum += math.pow(color[2] - median[2], 2)
        return squared_sum / len(pix)

    def print_average_variance(self):
        output = 0
        for tri in self.tris:
            tri_pix = pixels_in_tri(tri)
            if len(tri_pix) != 0:
                output += self.variance(tri_pix)  # TODO: this never seems to be accurate
        print("Average variance:", output / len(self.tris))

    # would the mean actually be preferable for the purposes of adjustment?
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

