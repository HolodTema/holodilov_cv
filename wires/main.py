import numpy as np
import matplotlib.pyplot as plt
import skimage


def load_images():
    images = []
    for i in range(1, 7):
        image = np.load(f"./data/wires{i}.npy")
        images += [image]
        plt.imshow(image)
        plt.show()
    return images



def main():
    images = load_images()





if __name__ == "__main__":
    main()


