import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import label, regionprops


def load_images():
    images = []
    for i in range(100):
        image = np.load(f"./out/h_{i}.npy")
        images += [image]
    return images



def find_centroids(images):
    centroids = []
    for image in images:
        labeled = label(image)
        props = regionprops(labeled)
        centers = [(prop.centroid[1], prop.centroid[0]) for prop in props]
        print(centers)
    return centroids





def main():
    images = load_images()
    centroids = find_centroids(images)


    
if __name__ == "__main__":
    main()

