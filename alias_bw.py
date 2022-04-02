from PIL import Image
import numpy as np
import pixelator

ALLOWED = (0, 255)

img_file = pixelator.get_user_file(f"Input file: ")
img = Image.open(img_file)
img_ar = np.asarray(img)

w, h = img.size

def closer_bw(value: int):
    if 255-value > value:
        return 0
    return 255

for x in range(w):
    for y in range(h):
        for i in range(len(img_ar[y][x])):
            if img_ar[y][x][i] not in ALLOWED:
                img_ar[y][x][i] = closer_bw(img_ar[y][x][i])

out_img = Image.fromarray(img_ar)
save_loc = input(f"Name to save to: ")
out_img.save(save_loc, "PNG")
