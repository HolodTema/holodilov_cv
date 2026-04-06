import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import opening
from skimage.measure import label


def main():
    image = np.load("./stars.npy")
    plt.imshow(image)
    plt.show()

    array_plus = np.array([
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
    ])

    array_cross = np.array([
        [1, 0, 0, 0, 1],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [1, 0, 0, 0, 1],
    ])

    amount_pluses = label(opening(image, array_plus)).max()
    amount_crosses = label(opening(image, array_cross)).max()
    
    amount_stars = amount_pluses + amount_crosses
    print(amount_stars)



if __name__ == "__main__":
    main()


