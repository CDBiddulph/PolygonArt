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
        return output

    def find_possible_bridges(self):
        n1 = self.next
        n2 = n1.next
        central_point = self.point
        output = list()
        while n2 is not self:
            p1 = n1.point
            p2 = n2.point

            if is_clockwise(central_point, p1, p2):
                ready = False  # ready to move on to the next edge
                while not ready:
                    if len(output) == 0:
                        if is_clockwise(central_point, self.next.point, p1) or \
                                self.next.point is p1:
                            output.append((n1, n2))
                        ready = True
                    else:
                        # lvp (last valid point) is the last point of the most recently-added valid edge
                        # take note that lvp could be the same as p1
                        lvp = output[-1][1].point
                        if is_counterclockwise(central_point, lvp, p1):
                            # should be impossible for p1, p2, and lvp to be collinear here?
                            if is_counterclockwise(p1, p2, lvp):  # this edge is in front of the edge of lvp
                                output.pop(-1)
                                # should be the only situation in which ready is False
                            else:
                                ready = True
                        else:  # if colinear or clockwise
                            output.append((n1, n2))
                            ready = True

            n1 = n1.next
            n2 = n2.next

        while len(output) != 0 and \
                not is_counterclockwise(central_point, self.last.point, output[-1][1].point) and \
                self.last.point is not output[-1][1].point:
            output.pop(-1)

        return output

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
