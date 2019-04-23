import poly_renderer as rend
import tri_handler as th
import png

reader = png.Reader("input\\medium_parrot.png")

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

# side length, shift size, adjust iterations
# tris = tri_handler.get_rect_tris(15, .2, 25)

# target variance, variance allowance, minimum leap,
# shift size, adjust iterations
tris = tri_handler.get_smart_tris(1500, 100, 2.0,
                                  .2, 1)

# tri_handler.print_average_variance()

renderer = rend.PolyRenderer(pixel_array, tris)
# renderer.render('output\\output.png')
# renderer.variance_render('output\\variance.png')
# renderer.bw_render('output\\bw_output.png')
