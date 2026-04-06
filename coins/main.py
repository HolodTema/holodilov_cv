import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label



# labeled - our image, but every object has its label (number from 1 to ...)
# coin_label_value - some label of some coin
def get_single_coin_area(labeled, coin_label_value):
    return (labeled == coin_label_value).sum()



def main():
    image = np.load("./coins.npy")
    labeled = label(image)

    areas = list()
    amount_coins = labeled.max()
    for coin_label in range(1, amount_coins+1):
        areas += [get_single_coin_area(labeled, coin_label)]

    unique_areas = sorted(list(set(areas)))
    amount_coin_types = [areas.count(area) for area in unique_areas]

    nominals = [1, 2, 5, 10]
    cost = sum(nominals[i]*amount_coin_types[i] for i in range(len(nominals)))
    print("Cost of all the coins:", cost)

    plt.imshow(image)
    plt.show()

    


if __name__ == "__main__":
    main()

