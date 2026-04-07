import matplotlib.pyplot as plt
import numpy as np
from skimage.io import imread
from skimage.measure import label, regionprops
from pathlib import Path


def get_centroid_coords_attributes(symbol_prop):
    centroid_x, centroid_y = symbol_prop.centroid_local
    centroid_x /= symbol_prop.image.shape[1]
    centroid_y /= symbol_prop.image.shape[0]
    return centroid_x, centroid_y



def get_perimeter_attribute(symbol_prop):
    return symbol_prop.perimeter / symbol_prop.image.size


def get_aspect_ratio_attribute(symbol_prop):
    aspect_ratio = symbol_prop.image.shape[1] / symbol_prop.image.shape[0]
    if aspect_ratio > 1:
        return aspect_ratio ** (-1)
    else:
        return aspect_ratio



def get_area_attribute(symbol_prop):
    return symbol_prop.area / symbol_prop.image.size



def get_eccentricity_attribute(symbol_prop):
    return symbol_prop.eccentricity



# to make this attribute more useful, I addded min limit value
def get_vertical_lines_attribute(symbol_prop):
    result = 0
    min_limit = symbol_prop.image.shape[0] 

    for x in range(symbol_prop.image.shape[1]):
        result += int(np.sum(symbol_prop.image[:, x]) >= min_limit)
    return result / symbol_prop.image.shape[1]



# to make this attribute more useful, I addded min limit value
def get_horizontal_lines_attribute(symbol_prop):
    result = 0
    min_limit = symbol_prop.image.shape[1]

    for y in range(symbol_prop.image.shape[0]):
        result += int(np.sum(symbol_prop.image[y, :]) >= min_limit)
    return result / symbol_prop.image.shape[0]



def get_amount_holes_attribute(symbol_prop):
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



# число эйлера для изображения = кол-во-компонент-связности - кол-во-дыр
# кол-во-компонент-связности - кол-во частей самого foreground
# в нашем случае кол-во-компонент-связности = 1 всегда (все наши символы связны)
def get_euler_attribute(symbol_prop):
    # это и есть кол-во-компонент-связности. В нашем случае = 1
    # но мы все равно посчитали так (хардкод - плохо)
    amount_foreground_components = label(symbol_prop.image).max()

    inverted_image = np.logical_not(symbol_prop.image)
    #labeled_background_components - все фоновые области символа. 
    # Это и дырки внутри символа, и фоновые области по границам символа
    labeled_background_components = label(inverted_image)
    
    # create mask with borders of the image
    boundary_mask = np.zeros_like(symbol_prop.image, dtype=bool)
    boundary_mask[0, :] = True
    boundary_mask[-1, :] = True
    boundary_mask[:, 0] = True
    boundary_mask[:, -1] = True

    # border_background_labels - номера меток фоновых областей на границе изображения
    border_background_labels = np.unique(labeled_background_components[boundary_mask])

    # далее надо посчитать только дырки внутри символов
    amount_holes = 0
    for label_number in range(1, labeled_background_components.max() + 1):
        if label_number not in border_background_labels:
            # если номера метки нет в списке граничных номеров меток - это дырка.
            amount_holes += 1
    
    # находим число эйлера
    euler_number = amount_foreground_components - amount_holes

    # число эйлера надо нормализовать - чтобы оно было в интервале [0; 1]
    # мы знаем amount_foreground_components = 1 всегда для всех наших символов
    # мы знаем amount_holes от 0 до 2 
    # поэтому euler_number in [-1; 1]
    euler_number_normalized = (euler_number + 1) / 2
    return euler_number_normalized



# vertical_profile - берем вертикальный столбик посередине изображения
# и считаем кол-во переходов пикселей с 0 до 1 и с 1 до 0 в этом столбике
# и нормализуем это значение
def get_vertical_profile_attribute(symbol_prop):
    center_column = symbol_prop.image.shape[1] // 2
    vertical_profile = symbol_prop.image[:, center_column]
    
    # find amount transitions (pixels changing from 0 to 1 or from 1 to 0)
    transitions = 0
    for i in range(1, len(vertical_profile)):
        if vertical_profile[i] != vertical_profile[i-1]:
            transitions += 1
    # normalize value
    return transitions / symbol_prop.image.shape[0]



# какой процент пикселей изображения находится в его левой части
def get_left_pixels_percent_attribute(symbol_prop):
    center_column = symbol_prop.image.shape[1] // 2
    image_left_part = symbol_prop.image[:, 0:center_column]

    amount_left_pixels = np.sum(image_left_part)
    return amount_left_pixels / symbol_prop.image.size



# какой процент пикселей изображения находится в его верхней части
def get_top_pixels_percent_attribute(symbol_prop):
    center_row = symbol_prop.image.shape[0] // 2
    image_top_part = symbol_prop.image[0:center_row, :]

    amount_top_pixels = np.sum(image_top_part)
    return amount_top_pixels / symbol_prop.image.size




# extractor returns numpy-array of symbol attributes
# every attribute has value [0; 1]
def extractor(symbol_prop):
        centroid_x, centroid_y = get_centroid_coords_attributes(symbol_prop)

        return np.array([
            centroid_x, 
            centroid_y,
            get_perimeter_attribute(symbol_prop),
            get_aspect_ratio_attribute(symbol_prop),
            get_area_attribute(symbol_prop),
            get_eccentricity_attribute(symbol_prop),
            get_vertical_lines_attribute(symbol_prop),
            get_horizontal_lines_attribute(symbol_prop),
            # после добавления числа эйлера число дырок излишне - это почти то же самое
            # get_amount_holes_attribute(symbol_prop),
            get_euler_attribute(symbol_prop),
            get_vertical_profile_attribute(symbol_prop),
            get_left_pixels_percent_attribute(symbol_prop),
            get_top_pixels_percent_attribute(symbol_prop)
        ])



# prop_to_recognize - symbol regionprop we need to recognize
# dict_symbol_with_attrs - dict, where key is symbol and value is the list of attrs of the symbol
def classificator(prop_to_recognize, dict_symbols_with_attrs):
    attrs_to_recognize = extractor(prop_to_recognize)

    result = ""
    min_distance = 10**16

    # compare attributes we need to recognize with all possible symbols attributes
    # and handle distance between attribute lists
    # minimal distance = we recognized the symbol
    for symbol in dict_symbols_with_attrs:
        symbol_attrs = dict_symbols_with_attrs[symbol]
        distance = ((symbol_attrs - attrs_to_recognize) ** 2).sum() ** 0.5
        if distance < min_distance:
            min_distance = distance
            result = symbol
    return result




def main():
    # remove alpha-channel
    image_alphabet = imread("./alphabet-small.png")[:, :, :-1]

    # make image binary
    binary_alphabet = image_alphabet.mean(2) < 255
    # every object on image have a label (number from 1 to ...)
    labeled_alphabet = label(binary_alphabet)
    # get properties of all the labeled objects
    props_alphabet = regionprops(labeled_alphabet)

    symbols = ['8', 'O', 'A', 'B', '1', 'W', 'X', '*','/', '-']
    symbol_attributes = dict()
    for symbol_prop, symbol in zip(props_alphabet, symbols):
        symbol_attributes[symbol] = extractor(symbol_prop)

    image_to_recognize = imread("./alphabet.png")[:, :, :-1]
    binary_to_recognize = image_to_recognize.mean(2) > 0
    labeled_to_recognize = label(binary_to_recognize)
    props_to_recognize = regionprops(labeled_to_recognize)
    
    result = dict()
    
    path_to_save = Path(__file__).parent / "out"
    path_to_save.mkdir(exist_ok=True)
    
    plt.figure(figsize=(7, 7))
    
    print("start recognizing...")
    for i, prop in enumerate(props_to_recognize):
        print(f"recognizing symbol {i}")
        # classificator() handles attributes of the symbol and returns recognized symbol
        recognized_symbol = classificator(prop, symbol_attributes)

        if recognized_symbol not in result:
            result[recognized_symbol] = 1
        else:
            result[recognized_symbol] += 1
        
        # show recognized symbol
        plt.cla()
        plt.title(f"Recognized symbol is '{recognized_symbol}'")
        plt.imshow(prop.image)
        # save image to the out directory
        plt.savefig(path_to_save / f"image_{prop.label}.png")

    # print result - amount of recognized symbols
    print(result)



if __name__ == "__main__":
    main()


