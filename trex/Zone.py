import numpy as np


class Zone:

    def __init__(self, left: int, top: int, width: int, height: int):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def get_bottom_right_x(self):
        return self.left + self.width

    def get_bottom_right_y(self):
        return self.top + self.height

    def get_absolute_zone_from_parent_zone(self, parent_zone):
        absolute_left = parent_zone.left + self.left
        absolute_top = parent_zone.top + self.top
        return Zone(absolute_left, absolute_top, self.width, self.height)

    def set_from_dict(self, dictionary: dict):
        self.left = dictionary["left"]
        self.top = dictionary["top"]
        self.width = dictionary["width"]
        self.height = dictionary["height"]

    def crop_np_image(self, image: np.ndarray):
        bottom_right_x = self.get_bottom_right_x()
        bottom_right_y = self.get_bottom_right_y()
        return image[self.top:bottom_right_y, self.left:bottom_right_x]
