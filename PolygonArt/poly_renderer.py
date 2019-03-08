import png
import tri_handler as th


class PolyRenderer:

    def __init__(self, i_pix, tris):
        self.i_pix = i_pix  # original pixels
        self.tris = tris
        self.o_pix = [[0 for _ in i_pix[0]] for _ in i_pix]  # final pixels - initialize as all black

    def render(self, path):
        tri_handler = th.TriHandler(self.i_pix)
        for tri in self.tris:
            tri_pix = th.pixels_in_tri(tri)
            if len(tri_pix) != 0:
                self.paint_pixels(tri_pix, tri_handler.median_color(tri_pix))
        self.save_image(path)

    def bw_render(self, path):
        tri_handler = th.TriHandler(self.i_pix)
        flag = True
        for tri in self.tris:
            flag = not flag
            tri_pix = th.pixels_in_tri(tri)
            if len(tri_pix) != 0:
                self.paint_pixels(tri_pix, (0, 0, 0) if flag else (255, 255, 255))
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
