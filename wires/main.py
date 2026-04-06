import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import opening
from skimage.measure import label


def load_images():
    images = []
    for i in range(1, 7):
        image = np.load(f"./data/wires{i}.npy")
        images += [image]
    return images



def main():
    print("Task wires")
    print("PS. every wire has AT LEAST ONE PART")

    images = load_images()

    for image_number, image in enumerate(images):
        print(f"Handling image {image_number}:")

        wire_sectors = list()

        # crop image into wires-images
        crop_start_index = 0
        for i in range(1, image.shape[0]):
            if np.any(image[i-1, :] != 0) and np.all(image[i, :] == 0):
                wire_sectors += [(image[crop_start_index:i+1, :]).copy()]
                crop_start_index = i
                plt.imshow(wire_sectors[-1])
                plt.show()

        # use opening() to split wire into parts
        # if wire is not broken, it has one part
        gap_kernel = np.ones((3, 1))
        amount_wires = 0
        for i in range(len(wire_sectors)):
            wire_sectors[i] = opening(wire_sectors[i], gap_kernel)
            amount_wire_parts = label(wire_sectors[i]).max()
            if amount_wire_parts != 0:
                amount_wires += 1
                print(f"Wire {i}: amount parts: {amount_wire_parts}")

        print(f"Amount wires: {amount_wires}")
        print()




if __name__ == "__main__":
    main()


