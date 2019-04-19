import poly_renderer as rend
import tri_handler as th
import png

reader = png.Reader("input\\parrot.png")

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
tris = tri_handler.get_rect_tris(40, .1, 25)

# target variance, variance allowance, minimum protrusion, minimum leap
# shift size, adjust iterations
# tris = tri_handler.get_smart_tris(40, .4, 25)

renderer = rend.PolyRenderer(pixel_array, tris)
renderer.render('output\\output.png')
renderer.bw_render('output\\bw_output.png')
