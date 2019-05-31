from point import Point, slope, intersection, segment_intersection, on_same_edge, is_clockwise
from border_node import BorderNode, loop_from_list, link
import math
import statistics as stat
from enum import Enum
import random

import poly_renderer as rend


class Direction(Enum):
    NEUTRAL = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class TriHandler:

    def __init__(self, pixels, time_h):
        # pixels is a list with dimensions [height][width*3]
        # the second dimension stores the RGB for each pixel in the row
        self.pixels = pixels
        self.width = int(len(pixels[0])/3)
        self.height = len(pixels)
        # points is a list of points (with references to other points)
        self.points = list()
        # tris is a list of 3-lists of points
        self.tris = list()
        # tri_num is the index of the last triangle created, for debugging
        self.tri_num = 0
        # border_loops is a list of nodes representing each individual loop of border nodes
        self.border_loops = list()

        # debugs for efficiency
        self.time_h = time_h

    def get_rect_tris(self, initial_side, test_shift_size, max_final_shift, adjust_iterations):
        self.rect_initialize(initial_side)
        self.adjust_points(test_shift_size, max_final_shift, adjust_iterations)
        return list(self.tris)

    def get_smart_tris(self, target_v, v_allowance, min_leap, max_leap,
                       test_shift_size, final_shift_size, adjust_iterations):
        self.smart_initialize(target_v, v_allowance, min_leap, max_leap)
        self.adjust_points(test_shift_size, final_shift_size, adjust_iterations)
        return list(self.tris)

    def smart_initialize(self, target_v, v_allowance, min_leap, max_leap):
        self.border_loops.append(self.first_border_node(target_v, v_allowance, min_leap, max_leap))
        while len(self.border_loops) != 0:
            self.step(self.border_loops.pop(0), target_v, v_allowance, min_leap, max_leap)

    def step(self, node, target_v, v_allowance, min_leap, max_leap):
        self.time_h.start_timing("step")
        if node is node.next.next.next:
            self.add_tri(node.point, node.next.point, node.next.next.point)
            self.test_render_new_triangle()
        elif node is not node.next.next and \
                node is not node.next:

            n1 = node.n1_of_largest_edge(self.width, self.height)
            n2 = n1.next
            p1 = n1.point
            p2 = n2.point

            longest_pb = self.longest_perpendicular_bisector(n1, n2)
            new_point = self.v_binary_search(longest_pb[0], longest_pb[1],
                                             target_v, v_allowance, min_leap, max_leap, p1, p2)

            self.points.append(new_point)
            add_edge(p1, new_point)
            add_edge(new_point, p2)
            self.add_tri(p1, p2, new_point)

            self.test_render_new_triangle()

            if new_point.on_edge(self.width, self.height):
                left_edge_node, right_edge_node = n1.adjacent_edge_nodes(new_point, self.width, self.height)

                left_new_node = BorderNode(new_point)
                link(left_edge_node, left_new_node)
                link(left_new_node, n2)

                right_new_node = BorderNode(new_point)
                link(n1, right_new_node)
                link(right_new_node, right_edge_node)

                self.search_for_bridges(left_new_node, target_v, v_allowance, min_leap, max_leap)
                self.search_for_bridges(right_new_node, target_v, v_allowance, min_leap, max_leap)

            else:
                new_node = BorderNode(new_point)
                link(n1, new_node)
                link(new_node, n2)

                self.search_for_bridges(new_node, target_v, v_allowance, min_leap, max_leap)
        self.time_h.end_timing("step")

    def test_render_new_triangle(self):

        self.time_h.start_timing("test_render_new_triangle")
        print(self.tri_num)

        if self.tri_num % 100 == 0 or (self.tri_num < 100 and self.tri_num % 10 == 0):
            test_renderer = rend.PolyRenderer(self.pixels, self.tris)
            test_renderer.render('output\\output{0}.png'.format(self.tri_num))
            # test_renderer.variance_render('output\\variance{0}.png'.format(self.tri_num))

        self.tri_num += 1

        self.time_h.end_timing("test_render_new_triangle")

        # self.time_h.print_report()

    def search_for_bridges(self, central_node, target_v, v_allowance, min_leap, max_leap):
        self.time_h.start_timing("search_for_bridges")

        valid_edges = central_node.find_possible_bridges()
        max_variance = target_v + v_allowance
        next_next = central_node.next
        central_point = central_node.point

        for edge in valid_edges:
            n1 = edge[0]
            n2 = edge[1]

            if (central_point.dist_squared_from_line(n1.point, n2.point) < pow(min_leap, 2) and
                central_point.in_stripe(n1.point, n2.point) and
                not on_same_edge(n1.point, n2.point, self.width, self.height)) or \
                (n1.point.dist_squared_from_line(n2.point, central_point) > pow(min_leap, 2) and
                 n2.point.dist_squared_from_line(n1.point, central_point) > pow(min_leap, 2) and
                 self.variance(pixels_in_tri([central_point, n1.point, n2.point]), cap=max_variance) < max_variance):

                new_node = BorderNode(central_point)
                link(n1, new_node)
                link(new_node, next_next)

                next_next = n2

                add_edge(n1.point, new_node.point)
                add_edge(n2.point, new_node.point)
                self.add_tri(n1.point, n2.point, new_node.point)

                self.test_render_new_triangle()

                self.border_loops.append(new_node.last)

        link(central_node, next_next)
        self.border_loops.append(central_node.last)

        self.time_h.end_timing("search_for_bridges")

    def v_binary_search(self, start_point, max_point, target, allowance, min_leap, max_leap, p1, p2):
        self.time_h.start_timing("v_binary_search")
        min_v = target - allowance
        max_v = target + allowance

        change_vector = max_point[0] - start_point[0], max_point[1] - start_point[1]

        # not taking the square root to increase efficiency
        min_p_leap_squared = math.pow(min_leap, 2) / (math.pow(change_vector[0], 2) + math.pow(change_vector[1], 2))
        max_p = max_leap / math.sqrt(math.pow(change_vector[0], 2) + math.pow(change_vector[1], 2))

        if Point(max_point[0], max_point[1]).on_edge(self.width, self.height):
            percent = min(1.0, max_p)
        else:
            percent = min(0.5, max_p)
        p_leap = percent / 2

        while True:
            new_point = Point(start_point[0] + change_vector[0] * percent, start_point[1] + change_vector[1] * percent)
            pix = pixels_in_tri([p1, p2, new_point])
            variance = self.variance(pix, cap=max_v)

            if math.pow(p_leap, 2) < min_p_leap_squared:
                self.time_h.end_timing("v_binary_search")
                return new_point

            if (variance is None or variance <= min_v) and percent < 1.0:
                percent += p_leap
            elif variance >= max_v and percent > 0.0:
                percent -= p_leap
            else:
                self.time_h.end_timing("v_binary_search")
                return new_point

            p_leap = p_leap / 2

    # p1 -> endpoint -> p2 will be counterclockwise
    def longest_perpendicular_bisector(self, n1, n2):
        self.time_h.start_timing("longest_perpendicular_bisector")

        p1 = n1.point
        p2 = n2.point
        start_point = (p1.x + p2.x) / 2, (p1.y + p2.y) / 2
        end_point = self.border_intersection(start_point, ((p1.y - p2.y), -(p1.x - p2.x)))

        node = n2
        while node is not n1:
            intersect = segment_intersection(start_point, end_point, node.point.to_tuple(), node.next.point.to_tuple())
            if intersect is not None:
                end_point = intersect
            node = node.next

        node = n2.next
        while node is not n1:
            point = node.point
            if is_clockwise(p1, p2, point):
                if is_clockwise(point, start_point, end_point):
                    intersect = intersection(start_point, end_point, p1, point)
                else:
                    intersect = intersection(start_point, end_point, p2, point)
                if intersect is not None and \
                        is_clockwise(p1, start_point, intersect) and \
                        is_clockwise(p1, intersect, end_point):
                    end_point = intersect

            node = node.next

        self.time_h.end_timing("longest_perpendicular_bisector")
        return start_point, end_point

    def border_intersection(self, start_point, direction):
        self.time_h.start_timing("border_intersection")

        end_point = start_point[0] + direction[0], start_point[1] + direction[1]
        output = None

        if direction[0] > 0:
            output = intersection(start_point, end_point, (self.width, 0), (self.width, 1))
        elif direction[0] < 0:
            output = intersection(start_point, end_point, (0, 0), (0, 1))

        if direction[1] > 0 and (output is None or output[1] > self.height):
            temp = intersection(start_point, end_point, (0, self.height), (1, self.height))
            if temp is not None:
                output = temp
        elif direction[1] < 0 and (output is None or output[1] < 0):
            temp = intersection(start_point, end_point, (0, 0), (1, 0))
            if temp is not None:
                output = temp

        self.time_h.end_timing("border_intersection")
        return output

    def first_border_node(self, target_v, v_allowance, min_leap, max_leap):
        self.time_h.start_timing("first_border_node")

        side = min(self.width, self.height) / 2
        leap = side / 2
        tl = Point(0, 0)
        min_v = target_v - v_allowance
        max_v = target_v + v_allowance

        while True:
            variance = self.variance(pixels_in_tri([tl, Point(0, side), Point(side, 0)]), cap=max_v)

            if leap < min_leap:
                break

            if (variance is None or variance <= min_v) and side < min(self.width, self.height):
                side += leap
            elif variance >= max_v and side > 0.0:
                side -= leap
            else:
                break

            leap = leap / 2

        # just going to divide by two to avoid making a big, flat edge
        p1 = Point(0, side / 2)
        p2 = Point(side / 2, 0)

        self.points.append(p1)
        self.points.append(p2)
        self.points.append(tl)

        add_edge(p1, p2)
        add_edge(p2, tl)
        add_edge(tl, p1)

        self.add_tri(p1, p2, tl)

        self.test_render_new_triangle()

        self.time_h.end_timing("first_border_node")
        return loop_from_list([p1, p2, Point(self.width, 0), Point(self.width, self.height), Point(0, self.height)])

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

    def adjust_points(self, t_shift_size, max_f_shift, num_iter):
        for p in range(len(self.points)):
            self.points[p].sort_adjacent()
        for iteration in range(num_iter):
            test_renderer = rend.PolyRenderer(self.pixels, self.tris)
            test_renderer.render('output\iteration{}.png'.format(iteration))
            # test_renderer.variance_render('output\\v_iteration{}.png'.format(iteration))
            # self.print_net_variance()
            print("Iteration", (iteration + 1))
            for p in range(len(self.points)):
                point = self.points[p]
                if not point.on_edge(self.width, self.height):
                    a_tris = point.adjacent_tris()
                    m_colors = []  # parallel array for triangle colors

                    # we simplify by assuming initial median colors, calculating them one time rather than five
                    for i in range(len(a_tris)):
                        pix = pixels_in_tri(a_tris[i])
                        m_colors.append(self.median_color(pix))

                    test_coords = point.get_test_coords(t_shift_size)

                    # up, right, down, left
                    variances = []

                    o_point = point.x, point.y

                    for i in range(0, 4):
                        point.x = test_coords[i][0]
                        point.y = test_coords[i][1]

                        # Does recalculating the median help, and how much does it hurt?
                        # Future research may be necessary.

                        variances.append(self.net_variance(a_tris, m_colors))

                    # reset point to its original position
                    # resetting y happens to be redundant in this case
                    point.x = o_point[0]
                    point.y = o_point[1]

                    # negative values push the point left, positive values push it right
                    horizontal_push = variances[3] - variances[1]
                    # negative values push the point up, positive values push it down
                    vertical_push = variances[0] - variances[2]

                    final_point =\
                        point.get_final_coords(vertical_push, horizontal_push, max_f_shift)

                    point.x = final_point[0]
                    point.y = final_point[1]

    def net_variance(self, tris, colors):
        output = 0

        for i in range(len(tris)):
            median = colors[i]
            if median:
                pix = pixels_in_tri(tris[i])
                if len(pix) != 0:
                    output += self.variance(pix, median)
        return output

    def variance(self, pix, median=None, cap=None):
        # self.time_h.start_timing("variance")
        if len(pix) == 0:
            return None
        if median is None:
            median = self.median_color(pix)
        squared_sum = 0
        for p in pix:
            color = self.get_color(p)
            if color:
                squared_sum += math.pow(color[0] - median[0], 2)
                squared_sum += math.pow(color[1] - median[1], 2)
                squared_sum += math.pow(color[2] - median[2], 2)
                if cap is not None and squared_sum > cap:
                    return cap
        # self.time_h.end_timing("variance")
        return squared_sum

    def print_net_variance(self):
        output = 0
        for tri in self.tris:
            tri_pix = pixels_in_tri(tri)
            if len(tri_pix) != 0:
                output += self.variance(tri_pix)
        print("Net variance:", output)

    # would the mean actually be preferable for the purposes of adjustment?
    def median_color(self, pix, sample_size=math.inf):
        if len(pix) == 0:
            return None
        r = []
        g = []
        b = []
        pix_sample = pix if sample_size > len(pix) else random.sample(pix, sample_size)
        for p in pix_sample:
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
    # if the elements of tris are tuples, turn them into points
    if isinstance(tri[0], tuple):
        tri[0] = Point(tri[0][0], tri[0][1])
    if isinstance(tri[1], tuple):
        tri[1] = Point(tri[1][0], tri[1][1])
    if isinstance(tri[2], tuple):
        tri[2] = Point(tri[2][0], tri[2][1])

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

