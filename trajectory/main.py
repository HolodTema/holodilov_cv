import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import label, regionprops
from itertools import permutations


AMOUNT_IMAGES = 100

def load_images():
    images = []
    for i in range(AMOUNT_IMAGES):
        image = np.load(f"./out/h_{i}.npy")
        images += [image]
    return images



def find_centroid_lists(images):
    centroid_lists = []
    for image in images:
        labeled = label(image)
        props = regionprops(labeled)
        centers = [(prop.centroid[1], prop.centroid[0]) for prop in props]
        centroid_lists += [centers]
    return centroid_lists


# centroid1, centroid2 - tuple<float>
def get_distance(centroid1, centroid2):
    return ((centroid1[0] - centroid2[0])**2 + (centroid1[1] - centroid2[1])**2)**0.5



def main():
    images = load_images()

    # centroid_lists has type like list<list<tuple<float>>>
    # where tuple contains 2 elements: y and x float-coordinates of centroid
    # list of such tuples - objects in single image
    # 
    # so, centroid_lists is list of lists of tuples of float
    centroid_lists = find_centroid_lists(images)
    
    centroids_first_image = centroid_lists[0]
    amount_objects = len(centroids_first_image)

    # every image regionprops() function can label objects in a different way
    # so, centroids of objects are shuffled in every centroid_lists element
    #
    # to understand who is who, we compare current and previous image-centroids
    # and we find the permutation when changes in coordinates are minimal
    dict_trajectories = {i: [] for i in range(amount_objects)}
    for i, centroid in enumerate(centroids_first_image):
        dict_trajectories[i] += [centroid]

    centroids_prev = centroids_first_image
    for i in range(1, AMOUNT_IMAGES):
        centroids_current = centroid_lists[i]

        min_sum = 2**16
        min_centroids_perm = centroids_current
        for centroids_current_perm in permutations(centroids_current):
            # we need to calculate sum of distances objects in centroids_prev and centroids_current_perm
            sum_distances = 0.0
            for obj_id in range(amount_objects):
                sum_distances += get_distance(centroids_current_perm[obj_id], centroids_prev[obj_id])
            if sum_distances < min_sum:
                min_sum = sum_distances
                min_centroids_perm = centroids_current_perm

        #so, we found the permutation of centroids which is min distance comparing previous image
        for i, centroid in enumerate(min_centroids_perm):
            dict_trajectories[i] += [centroid]
        

    # now dict_trajectory contains right trajectories for all the objects
    # it is time to build matplotlib visualisation!
    plt.figure(figsize=(8, 8))

    for obj_id in dict_trajectories:
        trajectory = dict_trajectories[obj_id]

        trajectory_y = [centroid[0] for centroid in trajectory]
        trajectory_x = [centroid[1] for centroid in trajectory]

        plt.plot(trajectory_x, trajectory_y, marker='o', linewidth=2, markersize=4, label=f"object {obj_id}")

    plt.title("Object trajectories:")
    plt.xlabel("X coordinate")
    plt.ylabel("Y coordinate")

    plt.legend()
    plt.show()
    


if __name__ == "__main__":
    main()

