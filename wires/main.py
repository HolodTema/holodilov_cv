import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import opening
from skimage.measure import label


def load_images():
    images = []
    for i in range(1, 7):
        image = np.load(f"./data/wires{i}.npy")
        images += [image]
        # plt.imshow(image)
        # plt.show()
    return images



def main():
    images = load_images()


    for image_number, image in enumerate(images):
        print(f"Handling image {image_number}:")

        wire_sectors = list()

        horizontal_line = np.zeros(image.shape[1])
        
        crop_start_index = 0
        for i in range(image.shape[0]):
            if image[i, :] == horizontal_line:
                wire_sectors += [(image[crop_start_index:i, :]).copy()]
                crop_start_index = i
        
        print(f"Amount wires: {len(wire_sectors)}")

        for i in range(len(wire_sectors)):
            wire_sectors[i] = opening(wire_sectors[i], np.array((3, 1)))
            amount_wire_parts = label(wire_sectors[i]).max()
            print(f"Wire {i}: amount parts: {amount_wire_parts}")
        print()



if __name__ == "__main__":
    main()


