import poly_renderer as rend
import tri_handler as th
import png

reader = png.Reader("parrot.png")

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
tris = tri_handler.get_tris(5, 10)  # shift size, adjust iterations

renderer = rend.PolyRenderer(pixel_array, tris)
renderer.render('output.png')
renderer.bw_render('bw_output.png')
