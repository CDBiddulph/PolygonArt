import poly_renderer as rend
import tri_handler as th
import png
from time_handler import TimeHandler

time_h = TimeHandler()
time_h.start_timing("setup")

reader = png.Reader("input\\scream.png")

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

# target variance, variance allowance, minimum leap, maximum leap
# test shift size, final shift size, adjust iterations
# time handler
tris = tri_handler.get_smart_tris(500000, 10000, 5.0, 10000000, 0.2, 0.05, 200)

# initial side, test shift percentage, final shift percentage, adjust iterations
# tris = tri_handler.get_rect_tris(40, 0.1, 0.05, 0)

renderer = rend.PolyRenderer(pixel_array, tris)

# t = time.time()
# renderer.v_from_edge_render('output\\from_edge.png', (0, 10), (10, 0))
# print(time.time() - t)
renderer.render('output\\output.png')
# renderer.variance_render('output\\variance.png')
# renderer.bw_render('output\\bw_output.png')
