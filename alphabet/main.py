from pathlib import Path
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



# число эйлера для изображения = кол-во-компонент-связности - кол-во-дыр
# кол-во-компонент-связности - кол-во частей самого foreground
# в нашем случае кол-во-компонент-связности = 1 всегда (все наши символы связны)
def get_euler_number(symbol_prop):
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
    return euler_number



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



# на сколько процентов от верхней границы символа находится y-координата центра масс
# image top = 0%
# image bottom = 100%
# y_centroid between 0% and 100%
def get_y_centroid_percent(symbol_prop):
    _, centroid_y = symbol_prop.centroid_local
    centroid_y /= symbol_prop.image.shape[0]
    return centroid_y



def classificator(prop):
    euler_number = get_euler_number(prop)

    if euler_number == -1:
        # B, 8
        vertical_lines = get_vertical_lines(prop)
        if vertical_lines > 0:
            return "B"
        else:
            return "8"
    elif euler_number == 0:
        # A, 0, D, P
        vertical_lines = get_vertical_lines(prop)
        if vertical_lines > 0:
            # D, P
            # я хотел посчитать через top_pixels_percent - не сработало
            # top_pixels_percent = get_top_pixels_percent(prop)
            # центр масс работает
            y_centroid_percent = get_y_centroid_percent(prop)
            if y_centroid_percent < 0.3:
                return "P"
            else:
                return "D"
        else:
            # A, 0
            eccentricity = get_eccentricity(prop)
            if eccentricity < 0.6:
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
    # folder to save images
    parent_path = Path(__file__).parent
    path = parent_path / "recognized"
    path.mkdir(exist_ok=True)

    # async matplotlib working not to show image every iteration
    plt.ion()

    plt.figure(figsize=(6, 8))

    image_symbols = imread("./symbols.png")[:, :, :-1]
    binary_symbols = image_symbols.mean(2) > 0
    labeled_symbols = label(binary_symbols)
    props_symbols = regionprops(labeled_symbols)

    dict_result = dict()

    amount_props = len(props_symbols)
    for i, prop in enumerate(props_symbols):
        # progres bar
        if i % 10 == 0:
            print(f"Handled {i} symbols from {amount_props}")

        recognized_symbol = classificator(prop)

        if recognized_symbol not in dict_result:
            dict_result[recognized_symbol] = 1
        else:
            dict_result[recognized_symbol] += 1

        # clear axis and other useless stuff
        plt.cla()

        plt.title(f"Recognized as {recognized_symbol}")
        plt.imshow(prop.image)
        if recognized_symbol == "/":
            plt.savefig(path / f"{prop.label}_slash.png")
        else:
            plt.savefig(path / f"{prop.label}_{recognized_symbol}.png")
    print(dict_result)



if __name__ == "__main__":
    main()


