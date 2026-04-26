import numpy as np
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.measure import label, regionprops


# get RGB tuple from the center of prop.image
def get_centroid_rgb_color(src_image, prop):
    centroid_y, centroid_x = prop.centroid
    centroid_x = int(centroid_x)
    centroid_y = int(centroid_y)
    (red, green, blue) = src_image[centroid_y, centroid_x, :]
    red = int(red)
    green = int(green)
    blue = int(blue)
    return (red, green, blue)


# if every horizontal line is fullfilled with 1 - we can say it is rectangle
def is_rectangle(prop):
    for y in range(prop.image.shape[0]):
        if np.sum(prop.image[y, :]) != prop.image.shape[1]:
            return False
    return True



def main():
    image = imread("./balls_and_rects.png")
    binary = image.sum(2) > 0
    labeled = label(binary)
    
    props = regionprops(labeled)
    amount_figures = len(props)
    print(f"Amount figures = {amount_figures}")

    dict_rect = dict()
    dict_circle = dict()
    amount_rect = 0
    for prop in props:
        is_rect = is_rectangle(prop)
        tuple_rgb = get_centroid_rgb_color(image, prop)
        if is_rect:
            amount_rect += 1
            if tuple_rgb in dict_rect:
                dict_rect[tuple_rgb] += 1
            else:
                dict_rect[tuple_rgb] = 1
        else:
            if tuple_rgb in dict_circle:
                dict_circle[tuple_rgb] += 1
            else:
                dict_circle[tuple_rgb] = 1


    print(f"Amount rectangles = {amount_rect}")
    print(f"Amount circles = {amount_figures - amount_rect}")
    print()
    print("Rectangles by their colors (RGB):")
    print(dict_rect)
    print()
    print("Circles by their colors (RGB):")
    print(dict_circle)



if __name__ == "__main__":
    main()


