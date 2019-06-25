from point import is_clockwise, is_counterclockwise, on_same_edge, distance_squared


class BorderNode:

    def __init__(self, point):
        self.point = point

    def __str__(self):
        output = ""
        node = self
        while node is not self.last:
            output += node.point.__str__() + " "
            node = node.next
        output += node.point.__str__() + " "
        return output

    def to_list(self):
        output = list()
        node = self
        while node is not self.last:
            output.append(node.point)
            node = node.next
        output.append(node.point)
        return output

    def find_possible_bridges(self):
        n1 = self.next
        n2 = n1.next
        output = [(self, self.next)]

        while n2 is not self:
            p1 = n1.point
            p2 = n2.point

            # edge is oriented towards self, and the new edge is not obscured by the two edges that "self" is a part of
            # honestly not sure if this solves the problem I was having, or if it is just a band-aid
            if not is_counterclockwise(self.point, p1, p2) and \
                    not (
                            (is_clockwise(self.point, p1, self.next.point) and
                             is_counterclockwise(self.point, p1, self.last.point)) or
                            (is_clockwise(self.point, p2, self.next.point) and
                             is_counterclockwise(self.point, p2, self.last.point))
                    ):
                if is_counterclockwise(self.point, output[-1][1].point, p1):  # output[-1] blocks (p1, p2) or vice versa
                    if is_counterclockwise(p1, p2, output[-1][1].point):  # (p1, p2) blocks output[-1]
                        to_append = True
                        # while there are removable output edges and output[-1] blocks (p1, p2) or vice versa
                        while len(output) > 1 and is_counterclockwise(self.point, output[-1][1].point, p1):
                            if is_counterclockwise(p1, p2, output[-1][1].point):
                                output.pop(-1)  # may not call at all
                            else:  # if one of the past output edges ends up in front of this one
                                to_append = False
                                break  # get out of this while loop

                        if to_append:
                            output.append((n1, n2))
                    # else: output[-1] blocks (p1, p2) - do nothing; do not append n1 and n2
                else:  # if collinear (meaning n1 and output[-1][1] are probably the same) or clockwise
                    output.append((n1, n2))

            n1 = n1.next
            n2 = n2.next

        while len(output) > 1 and \
                not is_counterclockwise(self.point, self.last.point, output[-1][1].point) and \
                self.last.point is not output[-1][1].point:
            output.pop(-1)

        return output[1:]  # cut off the very first edge, since it was only there for reference

    def n1_of_largest_edge(self, width, height):
        max_l_squared = 0
        output = self

        n1 = self
        n2 = self.next
        while n2 is not self:
            if not on_same_edge(n1.point, n2.point, width, height):
                l_squared = distance_squared(n1.point, n2.point)
                if l_squared > max_l_squared:
                    max_l_squared = l_squared
                    output = n1
            n1 = n1.next
            n2 = n2.next

        return output

    def n1_of_diagonal_edge(self, width, height):  # seems to lead to very small edges and crashing
        min_difference = None

        output = self

        n1 = self
        n2 = self.next
        while n2 is not self:
            p1 = n1.point
            p2 = n2.point
            if not on_same_edge(p1, p2, width, height):
                difference = abs((p1.x - p2.x) - (p2.y - p1.y))
                if min_difference is None or difference < min_difference:
                    min_difference = difference
                    output = n1
            n1 = n1.next
            n2 = n2.next

        return output

    def adjacent_edge_nodes(self, target, width, height):
        match_x = target.x_locked(width)
        match_y = target.y_locked(height)

        search1 = self
        search2 = self
        starting = True

        while search1 is not search2 or starting:
            starting = False

            if match_x and match_y:
                if (round(target.x, 5) == round(search1.point.x, 5) and
                        round(target.y, 5) == round(search1.next.point.y, 5)) or \
                        (round(target.y, 5) == round(search1.point.y, 5) and
                         round(target.x, 5) == round(search1.next.point.x, 5)):
                    return search1, search1.next
                if (round(target.x, 5) == round(search2.point.x, 5) and
                        round(target.y, 5) == round(search2.last.point.y, 5)) or \
                        (round(target.y, 5) == round(search2.point.y, 5) and
                         round(target.x, 5) == round(search2.last.point.x, 5)):
                    return search2.last, search2
            elif match_x:
                if round(target.x, 5) == round(search1.point.x, 5) == round(search1.next.point.x, 5) and \
                        (search1.point.y < target.y < search1.next.point.y or
                         search1.point.y > target.y > search1.next.point.y):
                    return search1, search1.next
                if round(target.x, 5) == round(search2.point.x, 5) == round(search2.last.point.x, 5) and \
                        (search2.point.y < target.y < search2.last.point.y or
                         search2.point.y > target.y > search2.last.point.y):
                    return search2.last, search2
            elif match_y:
                if round(target.y, 5) == round(search1.point.y, 5) == round(search1.next.point.y, 5) and \
                        (search1.point.x < target.x < search1.next.point.x or
                         search1.point.x > target.x > search1.next.point.x):
                    return search1, search1.next
                if round(target.y, 5) == round(search2.point.y, 5) == round(search2.last.point.y, 5) and \
                        (search2.point.x < target.x < search2.last.point.x or
                         search2.point.x > target.x > search2.last.point.x):
                    return search2.last, search2

            search1 = search1.next
            search2 = search2.last

        print("Error: no edge in loop matching", target)
        return None


def loop_from_list(point_list):
    node_list = []
    for point_i in range(len(point_list)):
        node_list.append(BorderNode(point_list[point_i]))
        if point_i != 0:
            link(node_list[point_i - 1], node_list[point_i])
    link(node_list[len(point_list) - 1], node_list[0])
    return node_list[0]


def link(n1, n2):
    n1.next = n2
    n2.last = n1
