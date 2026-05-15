import numpy as np


def get_top_pixel_percent_pos(arr):
    for i in range(arr.shape[0]):
        if np.sum(arr[i, :]) > 0:
            return (i / arr.shape[0])
    return -1


def get_bottom_pixel_percent_pos(arr):
    for i in range(arr.shape[0]-1, -1, -1):
        if np.sum(arr[i, :]) > 0:
            return (i / arr.shape[0])
    return -1


def get_left_pixel_percent_pos(arr):
    for i in range(arr.shape[1]):
        if np.sum(arr[:, i]) > 0:
            return (i / arr.shape[1])
    return -1


def get_right_pixel_percent_pos(arr):
    for i in range(arr.shape[1]-1, -1, -1):
        if np.sum(arr[:, i]) > 0:
            return (i / arr.shape[1])
    return -1


def get_width_percent(arr):
    return get_right_pixel_percent_pos(arr) - get_left_pixel_percent_pos(arr)

