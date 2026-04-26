import numpy as np
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.measure import label, regionprops



def get_centroid_rgb_color(src_image, prop):
    centroid_y, centroid_x = prop.centroid
    centroid_x = int(centroid_x)
    centroid_y = int(centroid_y)
    print(centroid_x)
    print(centroid_y)
    print(src_image[centroid_y, centroid_x, :])


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
        if is_rect:
            amount_rect += 1
        get_centroid_rgb_color(image, prop)


    print(f"Amount rectangles = {amount_rect}")
    print(f"Amount circles = {amount_figures - amount_rect}")

    plt.imshow(labeled)
    plt.show()



if __name__ == "__main__":
    main()


