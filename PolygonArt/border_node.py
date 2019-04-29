class BorderNode:

    def __init__(self, point):
        self.point = point


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
