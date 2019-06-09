import poly_renderer as rend
import tri_handler as th
import png
from time_handler import TimeHandler
import sys

time_h = TimeHandler()
time_h.start_timing("setup")

sys.setrecursionlimit(50000)  # otherwise pickle will throw a RecursionError

reader = png.Reader("input\\small_dog.png")

img = reader.read()
width = img[0]
row_iter = img[2]
hasAlpha = img[3]['alpha']

pixel_array = []

if hasAlpha:
    for r in row_iter:
        r_array = []
        for p in range(0, width * 4, 4):
            for c in range(p, p+3):
                r_array.append(r[c])
        pixel_array.append(r_array)
else:
    for r in row_iter:
        pixel_array.append(r)

tri_handler = th.TriHandler(pixel_array, time_h)

tri_handler = th.load_state("states\\debug1100")

# target variance, variance allowance, minimum leap, maximum leap
tri_handler.smart_initialize(100000, 10000, 5.0, 10000000)

# test shift size, final shift size, adjust iterations
tri_handler.adjust_points(0.2, 0.05, 50)

tris = tri_handler.get_tris()
renderer = rend.PolyRenderer(pixel_array, tris, scale=5.0)

renderer.render('output\\output.png')
# renderer.variance_render('output\\variance.png')
# renderer.bw_render('output\\bw_output.png')
