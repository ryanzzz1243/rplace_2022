from enum import Enum
import numpy as np
from multiprocessing.sharedctypes import Value
from PIL import Image
from PIL import ImageColor
from os.path import exists

class color(Enum):
    RED = ImageColor.getrgb("#ff4500ff")
    ORANGE = ImageColor.getrgb("#ffa800ff")
    YELLOW = ImageColor.getrgb("#ffd635ff")
    GREEN = ImageColor.getrgb("#00a368ff")
    LIME = ImageColor.getrgb("#7eed56ff")
    DBLUE = ImageColor.getrgb("#2450a4ff")
    BLUE = ImageColor.getrgb("#3690eaff")
    LBLUE = ImageColor.getrgb("#51e9f4ff")
    DPURPLE = ImageColor.getrgb("#811e9fff")
    PURPLE = ImageColor.getrgb("#b44ac0ff")
    PINK = ImageColor.getrgb("#ff99aaff")
    BROWN = ImageColor.getrgb("#9c6926ff")
    BLACK = ImageColor.getrgb("#000000ff")
    DGREY = ImageColor.getrgb("#898d90ff")
    LGREY = ImageColor.getrgb("#d4d7d9ff")
    WHITE = ImageColor.getrgb("#ffffffff")

all_colors = color.__members__.values()

def get_user_img_size(bounds_x: tuple = (0, float("inf")), bounds_y: tuple = (0, float("inf"))) -> tuple:
    tgt_dims = ("width", "height")
    tgt_size = [-1, -1]
    bounds = bounds_x
    for i in range(len(tgt_size)):
        # while out of bounds
        while tgt_size[i] < bounds[0] or tgt_size[i] > bounds[1]:
            try:
                req_s = int(input(f"Input desired {tgt_dims[i]}: "))
            except ValueError as ve:
                print(f"Invalid input: {ve}")
                continue
            tgt_size[i] = req_s
            bounds = bounds_y
    return tuple(tgt_size)

def get_user_int(prompt: str) -> int:
    while(True):
        try:
            user_in = int(input(prompt))
        except ValueError as ve:
            print(f"Invalid input: {ve}")
            continue
        return user_in

def get_user_bool(prompt: str) -> bool:
    return input(prompt).upper() == 'Y'

def get_user_file(prompt: str) -> str:
    user_in = input(prompt)
    return get_file(user_in)

def get_file(file_loc: str) -> str:
    if exists(file_loc):
        return file_loc
    
def color_closest(source: list) -> list:
    min_dist = float('INF')
    best_color = source
    global all_colors
    for colorrr in all_colors:
        colorr = colorrr.value
        distance = 0
        for i in range(len(source)):
            distance += (colorr[i]-source[i])**2
        distance = distance**0.5
        if distance < min_dist:
            min_dist = distance
            best_color = colorr[:len(source)]
    return best_color

class rplace_image:
    def __init__(self, image: str):
        '''Initialize with file location'''
        try:
            IMG = Image.open(image)
        except:
            return None
        self.img = IMG
        self.x = IMG.size[0]
        self.y = IMG.size[1]
        '''img_np = np.asarray(IMG)
        # Preprocess image to avoid rolling errors.
        for x in range(self.x):
            for y in range(self.y):
                img_np[y][x] = color_closest(img_np[y][x])
        self.img = Image.fromarray(img_np)'''

    def pixelate(self, x_size: int, y_size: int):
        src_w, src_h = self.img.size
        x_size = round(x_size)
        y_size = round(y_size)
        w_offset = round(src_w / x_size)
        h_offset = round(src_h / y_size)
        src_img = np.asarray(self.img)
        tgt_img = np.empty(shape=(y_size, x_size, len(src_img[0][0])), dtype=src_img.dtype)
        for x_tgt in range(0, x_size):
            for y_tgt in range(0, y_size):
                avg_color = [0]*len(self.img.mode)
                count = 0
                # sample the area
                for x_src in range(x_tgt*w_offset, (x_tgt*w_offset)+w_offset):
                    for y_src in range(y_tgt*h_offset, (y_tgt*h_offset)+h_offset):
                        error = False
                        for i in range(len(avg_color)):
                            try:
                                avg_color[i] += src_img[y_src][x_src][i]
                            except IndexError as ie:
                                error = True
                                break
                        if not error:
                            count += 1
                avg_color = color_closest([item//count for item in avg_color]) # average rgb values
                tgt_img[y_tgt][x_tgt] = avg_color
        tgt_out = Image.fromarray(tgt_img)
        return tgt_out

    def pixelate_square(self, square: int):
        return self.pixelate(self.x / square, self.y / square)

def main():
    file = get_user_file("Specify image: ")
    if not file:
        return None
    px = rplace_image(file)
    #size = get_user_img_size((0, px.x-1), (0, px.y-1))
    #out = px.pixelate(size[0], size[1])
    if get_user_bool("Specify color restrictions? Y/N: "):
        print("Possible colors: ")
        print([colorr.name for colorr in color], sep=", ")
        print("Specify the colors to allow by name sperated by commas: ")
        color_filter_user = input()
        color_filters = [f"{value.lstrip().strip()}" for value in color_filter_user.upper().split(',')]
        if not color_filters:
            print("No filters applied.")
        global all_colors
        all_colors = list()
        for c_filter in color_filters:
            try:
                all_colors.append(color[c_filter])
            except KeyError as ke:
                print(f"Invalid color \"{c_filter}\": {ke}")
                continue
    # get sizes
    sizes = input("Square sizes (int), separated by comma: ")
    sizes = sizes.strip().split(',')
    for index, size in enumerate(sizes):
        try:
            sizes[index] = int(sizes[index].lstrip().strip())
        except ValueError as ve:
            print(f"Invalid size in your input: {ve}")
            continue
    sizes = [value for value in sizes if type(value) == int]
    outs = list()
    for size in sizes:
        outs.append(px.pixelate_square(size))
    out_path = input("Name to save to (do not include extension): ")
    for index, out in enumerate(outs):
        out.save(f"img/{out_path}-{index}.{(px.img.format).lower()}", format=px.img.format)

if __name__ == "__main__":
    main()