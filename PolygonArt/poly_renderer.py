import png
import tri_handler as th
import colorsys
from point import Point


class PolyRenderer:

    def __init__(self, i_pix, tris, scale=1, m_radius=1):
        self.i_pix = i_pix  # original pixels
        self.width = int(len(i_pix[0])/3)
        self.height = len(i_pix)
        self.tris = tris

        self.xs = true_scale(scale, self.width)
        self.ys = true_scale(scale, self.height)
        self.o_width = int(self.xs * self.width + 0.5)
        self.o_height = int(self.ys * self.height + 0.5)
        self.o_pix = [[0 for _ in range(self.o_width * 3)] for _ in range(self.o_height)]  # initialize as all black

        self.markers = list()
        self.m_radius = m_radius

    def render(self, path):
        tri_handler = th.TriHandler(self.i_pix, None)
        for unscaled_tri in self.tris:
            unscaled_tri_pix = th.pixels_in_tri(unscaled_tri)
            tri = self.scaled_tri(unscaled_tri)
            tri_pix = th.pixels_in_tri(tri)
            if len(unscaled_tri_pix) != 0:
                self.paint_pixels(tri_pix, tri_handler.median_color(unscaled_tri_pix))
            elif len(tri_pix) != 0:
                x = int(unscaled_tri[0].x)
                y = int(unscaled_tri[0].y)
                x = x if x < self.width else self.width - 1
                y = y if y < self.height else self.height - 1
                self.paint_pixels(tri_pix, tri_handler.get_color((x, y)))
        self.render_markers()
        self.save_image(path)

    def bw_render(self, path):
        flag = True
        for tri in self.tris:
            flag = not flag
            tri_pix = th.pixels_in_tri(tri)
            if len(tri_pix) != 0:
                self.paint_pixels(tri_pix, (0, 0, 0) if flag else (255, 255, 255))
        self.save_image(path)

    variance_range = 20000

    def variance_render(self, path):
        tri_handler = th.TriHandler(self.i_pix, None)
        for tri in self.tris:
            tri_pix = th.pixels_in_tri(tri)
            if len(tri_pix) != 0:
                hue = tri_handler.variance(tri_pix) / self.variance_range
                hue = hue if hue < 1 else 1
                hue = (1 - hue) * 0.7
                hue = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                hue = (hue[0] * 255, hue[1] * 255, hue[2] * 255)
                self.paint_pixels(tri_pix, hue)
        self.save_image(path)

    v_from_edge_range = 1000000

    def v_from_edge_render(self, path, p1, p2):
        tri_handler = th.TriHandler(self.i_pix)
        for x in range(int(len(self.o_pix[0]) / 3)):
            for y in range(len(self.o_pix)):
                tri_pix = th.pixels_in_tri([(p1[0] - 0.5, p1[1] - 0.5), (p2[0] - 0.5, p2[1] - 0.5), (x - 0.5, y - 0.5)])
                if len(tri_pix) != 0:
                    hue = tri_handler.variance(tri_pix, cap=self.v_from_edge_range) / self.v_from_edge_range
                    hue = hue if hue < 1 else 1
                    hue = (1 - hue) * 0.7
                    hue = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                    hue = (hue[0] * 255, hue[1] * 255, hue[2] * 255)
                    self.paint_pixel((x, y), hue)
            # print("Column", x)

        pink = (255, 0, 255)
        self.paint_pixel(p1, pink)
        self.paint_pixel(p2, pink)

        self.save_image(path)

    def render_markers(self):
        for m in self.markers:
            cx = int(m.x * self.xs)
            cy = int(m.y * self.ys)
            for x in range(cx - self.m_radius, cx + self.m_radius):
                for y in range(cy - self.m_radius, cy + self.m_radius):
                    self.paint_pixel((x, y), m.color)

    def paint_pixels(self, pix, color):
        for p in pix:
            self.paint_pixel(p, color)

    def paint_pixel(self, point, color):
        if 0 <= point[0] < self.o_width and 0 <= point[1] < self.o_height:
            start_index = point[0] * 3
            for i in range(3):
                self.o_pix[point[1]][start_index + i] = color[i]

    def save_image(self, path):
        f = open(path, 'wb')
        w = png.Writer(len(self.o_pix[0])//3, len(self.o_pix))
        w.write(f, self.o_pix)
        f.close()

    def scaled_tri(self, tri):
        if self.xs == 1 and self.ys == 1:
            return tri
        p0 = Point(tri[0].x * self.xs, tri[0].y * self.ys)
        p1 = Point(tri[1].x * self.xs, tri[1].y * self.ys)
        p2 = Point(tri[2].x * self.xs, tri[2].y * self.ys)
        return [p0, p1, p2]


def true_scale(scale, dimension):
    return int(scale * dimension + 0.5) / dimension  # adding 0.5 ensures rounding to nearest integer
