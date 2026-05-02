import numpy as np
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.measure import label, regionprops

# check that every horizontal line of the image is full from start to end
def is_rectangle(prop):
    for y in range(prop.image.shape[0]):
        if np.sum(prop.image[y, :]) != prop.image.shape[1]:
            return False
    return True



def get_centroid_pixel_rgb_tuple(src_image, prop):
    centroid_x, centroid_y = prop.centroid_local
    red, green, blue = src_image[int(centroid_x), int(centroid_y)]
    return (red, green, blue)



def main():
    image = imread("balls_and_rects.png")
    print(image)
    plt.imshow(image)
    plt.show()
    binary = image.mean(2) > 0
    labeled = label(binary)
    plt.imshow(labeled)
    plt.show()

    dict_rect = dict()
    dict_circle = dict()
    amount_figures = 0

    for prop in regionprops(labeled):
        amount_figures += 1
        is_rect = is_rectangle(prop)
        rgb_tuple = get_centroid_pixel_rgb_tuple(image, prop)
        if is_rect:
            if rgb_tuple in dict_rect:
                dict_rect[rgb_tuple] += 1
            else:
                dict_rect[rgb_tuple] = 1
        else:
            if rgb_tuple in dict_circle:
                dict_circle[rgb_tuple] += 1
            else:
                dict_circle[rgb_tuple] = 1
            
    
    print("Amount figures:", amount_figures)
    print(dict_rect)
    print(dict_circle)

if __name__ == "__main__":
    main()
