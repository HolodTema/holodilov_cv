import matplotlib.pyplot as plt
import numpy as np
from skimage.io import imread
from skimage.measure import label, regionprops



def get_vertical_lines(symbol_prop):
    result = 0

    for x in range(symbol_prop.image.shape[1]):
        result += int(np.sum(symbol_prop.image[:, x]) >= symbol_prop.image.shape[0])
    return result / symbol_prop.image.shape[1]



def get_horizontal_lines(symbol_prop):
    result = 0
    for y in range(symbol_prop.image.shape[0]):
        result += int(np.sum(symbol_prop.image[y, :]) >= symbol_prop.image.shape[1])
    return result / symbol_prop.image.shape[0]



def get_amount_holes(symbol_prop):
    symbol_shape = symbol_prop.image.shape
    # not to count edges as holes, we crop our image
    new_image = np.zeros((symbol_shape[0] - 2, symbol_shape[1] - 2))
    new_image = symbol_prop.image[1:-1, 1:-1]
    
    # then invert the image to count holes
    new_image = np.logical_not(new_image)
    labeled = label(new_image)
    if labeled.size == 0:
        return 0
    amount_holes = labeled.max()
    return amount_holes



def get_aspect_ratio(symbol_prop):
    aspect_ratio = symbol_prop.image.shape[1] / symbol_prop.image.shape[0]
    if aspect_ratio > 1:
        return aspect_ratio ** (-1)
    else:
        return aspect_ratio



def get_percent_area(symbol_prop):
    return symbol_prop.area / symbol_prop.image.size



def get_eccentricity(symbol_prop):
    return symbol_prop.eccentricity


def get_amount_bays(symbol_prop):
    prop_image_inverted = np.logical_not(symbol_prop.image)
    prop_image_inverted_labeled = label(prop_image_inverted)
    amount_bays = 0
    for prop in regionprops(prop_image_inverted_labeled):
        if prop.area > 3:
            amount_bays += 1
    return amount_bays


# какой процент пикселей изображения находится в его верхней части
def get_top_pixels_percent(symbol_prop):
    center_row = symbol_prop.image.shape[0] // 2
    image_top_part = symbol_prop.image[0:center_row, :]

    amount_top_pixels = np.sum(image_top_part)
    return amount_top_pixels / symbol_prop.image.size



def classificator(prop):
    holes = get_amount_holes(prop)

    if holes == 2:
        # B, 8
        vertical_lines = get_vertical_lines(prop)
        if vertical_lines > 0:
            return "B"
        else:
            return "8"
    elif holes == 1:
        # A, 0, D, P
        vertical_lines = get_vertical_lines(prop)
        if vertical_lines > 3:
            # D, P
            top_pixels_percent = get_top_pixels_percent(prop)
            if top_pixels_percent > 0.6:
                return "P"
            else:
                return "D"
        else:
            # A, 0
            eccentricity = get_eccentricity(prop)
            if eccentricity < 0.4:
                return "0"
            else:
                return "A"
    else:
        # W, -, X, /, 1, *
        aspect_ratio = get_aspect_ratio(prop)
        if aspect_ratio > 0.9:
            return "*"
        # W, -, X, /, 1
        percent_area = get_percent_area(prop)
        if percent_area >= 0.95:
            return "-"
        # W, X, /, 1
        vertical_lines = get_vertical_lines(prop)
        horizontal_lines = get_horizontal_lines(prop)
        if vertical_lines > 0 and horizontal_lines > 0:
            return "1"
        # W, X, /
        amount_bays = get_amount_bays(prop)
        if amount_bays == 5:
            return "W"
        elif amount_bays == 4:
            return "X"
        else: 
            return "/"



def main():
    image_symbols = imread("./symbols.png")[:, :, :-1]
    binary_symbols = image_symbols.mean(2) > 0
    labeled_symbols = label(binary_symbols)
    props_symbols = regionprops(labeled_symbols)

    dict_result = dict()

    for prop in props_symbols:
        recognized_symbol = classificator(prop)

        if recognized_symbol not in dict_result:
            dict_result[recognized_symbol] = 1
        else:
            dict_result[recognized_symbol] += 1

    print(dict_result)



if __name__ == "__main__":
    main()


