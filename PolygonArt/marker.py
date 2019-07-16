class Marker:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        if color is None:
            self.color = get_color(6)
        else:
            self.color = color


int_to_color = {
    0: (255, 0, 0),
    1: (0, 0, 255),
    2: (0, 255, 0),
    3: (255, 255, 0),
    4: (0, 255, 255),
    5: (255, 0, 255),
    6: (255, 255, 255),
    7: (0, 0, 0)
}


def get_color(num):
    return int_to_color.get(num % len(int_to_color))
