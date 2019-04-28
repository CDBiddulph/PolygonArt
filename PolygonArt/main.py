import poly_renderer as rend
import tri_handler as th
import png
import time

reader = png.Reader("input\\small_parrot.png")

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

tri_handler = th.TriHandler(pixel_array)

# target variance, variance allowance, minimum leap,
# test shift size, final shift size, adjust iterations
tris = tri_handler.get_smart_tris(1500, 100, 2.0, 0.2, 0.1, 1)

# initial side, test shift percentage, final shift percentage, adjust iterations
# tris = tri_handler.get_rect_tris(7, 0.1, 0.05, 500)

renderer = rend.PolyRenderer(pixel_array, tris)

t = time.time()
renderer.v_from_edge_render('output\\from_edge.png', (0, 10), (10, 0))
print(time.time() - t)
# renderer.render('output\\output.png')
# renderer.variance_render('output\\variance.png')
# renderer.bw_render('output\\bw_output.png')
