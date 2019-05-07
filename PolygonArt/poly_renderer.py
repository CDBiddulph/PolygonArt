import png
import tri_handler as th
import colorsys


class PolyRenderer:

    def __init__(self, i_pix, tris):
        self.i_pix = i_pix  # original pixels
        self.tris = tris
        self.o_pix = [[240 for _ in i_pix[0]] for _ in i_pix]  # final pixels - initialize as all black

    def render(self, path):
        tri_handler = th.TriHandler(self.i_pix)
        for tri in self.tris:
            tri_pix = th.pixels_in_tri(tri)
            if len(tri_pix) != 0:
                self.paint_pixels(tri_pix, tri_handler.median_color(tri_pix))
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
        tri_handler = th.TriHandler(self.i_pix)
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

    def paint_pixels(self, pix, color):
        for p in pix:
            self.paint_pixel(p, color)

    def paint_pixel(self, point, color):
        start_index = point[0] * 3
        for i in range(3):
            self.o_pix[point[1]][start_index + i] = color[i]

    def save_image(self, path):
        f = open(path, 'wb')
        w = png.Writer(len(self.o_pix[0])//3, len(self.o_pix))
        w.write(f, self.o_pix)
        f.close()
