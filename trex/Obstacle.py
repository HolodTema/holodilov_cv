from enum import Enum
import numpy as np
from Zone import Zone


class ObstacleType(Enum):
    SLIM_LOW = 0
    SLIM_TALL = 1
    WIDE_LOW = 2
    WIDE_TALL = 3
    BIRD_TO_DUCK = 4


class Obstacle:

    def __init__(self, game_window: Zone, zone: Zone, image: np.ndarray):
        for i in range(image.shape[0]):
            if np.sum(image[i, :]) > 0:
                self.top_border = i
                break

        for i in range(image.shape[1]):
            if np.sum(image[:, i]) > 0:
                self.left_border = i
                break

        for i in range(image.shape[1] - 1, -1, -1):
            if np.sum(image[:, i]) > 0:
                self.right_border = i
                break

        height_percent = 1 - float(self.top_border) / float(zone.height)
        self.is_tall = height_percent > 0.65

        self.top_border += zone.top
        self.left_border += zone.left
        self.right_border += zone.left
        self.width = self.right_border - self.left_border

        width_percent = float(self.width) / float(game_window.width)
        self.is_wide = width_percent > 0.7

    def move_with_speed(self, speed: float):
        self.right_border -= int(speed+8)
        self.left_border -= int(speed+8)

