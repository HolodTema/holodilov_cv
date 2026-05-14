import mss
from pathlib import Path
import json
import time
from Overlay import Overlay
from ObstacleType import ObstacleType
from numpy_util import *
import keyboard
from pyKey.windows import pressKey, releaseKey, press


class DinoAutoRunner:
    MIN_SPEED = 6
    MAX_SPEED = 13
    ACCELERATION = 0.0006

    def __init__(self, config_filename):
        path = Path(__file__).parent / config_filename
        if not (path.exists()):
            raise RuntimeError("Error: unable open config file.")
        with path.open("r") as f:
            self.game_window = json.load(f)

        self.overlay = Overlay()
        self.is_running = False
        self.recognize_forefront = True
        self.speed = None
        self.frames_since_short_jump = None
        self.frames_since_long_jump = None
        self.image_binary = None
        self.obstacle_zone = None
        self.forefront_zone = None
        self.obstacle_queue = None

    def start_autorun(self):
        self.is_running = True
        self.frames_since_short_jump = 0
        self.frames_since_long_jump = 0
        self.speed = self.MIN_SPEED
        self.obstacle_queue = list()
        self.overlay.start()
        self.overlay.draw_rect(self.game_window)
        self._update_obstacle_zone()
        self._update_forefront_zone()
        self._draw_obstacle_zone()
        self._draw_forefront_zone()
        while self.is_running:
            self._take_screenshot()
            self._handle_forefront()
            self._update_obstacle_zone()
            self._handle_obstacle()
            if self.speed < self.MAX_SPEED:
                self.speed += self.ACCELERATION
            if self.frames_since_short_jump == 4:
                releaseKey("UP")
            self.frames_since_short_jump += 1
            self.frames_since_long_jump += 1
            time.sleep(0.01)

    def stop_autorun(self):
        self.overlay.stop()
        self.is_running = False

    def is_running(self):
        return self.is_running

    def _take_screenshot(self):
        with mss.MSS() as sct:
            image = np.array(sct.grab(self.game_window))[:, :, :-1]
            self.image_gray = np.sum(image, axis=2)
            self.image_binary = (self.image_gray < 600)

    def _update_obstacle_zone(self):
        obstacle_type_coefficient = 0.093
        if len(self.obstacle_queue) > 0:
            if self.obstacle_queue[0] == ObstacleType.WIDE_TALL:
                obstacle_type_coefficient = 0.058
            if self.obstacle_queue[0] == ObstacleType.SLIM_TALL:
                obstacle_type_coefficient = 0.045
            if self.obstacle_queue[0] == ObstacleType.WIDE_LOW:
                obstacle_type_coefficient = 0.093
            if self.obstacle_queue[0] == ObstacleType.SLIM_LOW:
                obstacle_type_coefficient = 0.093

        speed_delta = int(self.game_window["width"] * 0.01 * self.speed)
        self.obstacle_zone = dict()
        self.obstacle_zone["left"] = int(self.game_window["width"]*0.065) + speed_delta
        self.obstacle_zone["top"] = int(self.game_window["height"]*0.7)
        self.obstacle_zone["width"] = int(self.game_window["width"]*obstacle_type_coefficient)
        self.obstacle_zone["height"] = int(self.game_window["height"]*0.29)

    def _update_forefront_zone(self):
        self.forefront_zone = dict()
        self.forefront_zone["left"] = int(self.game_window["width"] * 0.87)
        self.forefront_zone["top"] = int(self.game_window["height"] * 0.7)
        self.forefront_zone["width"] = int(self.game_window["width"] * 0.12)
        self.forefront_zone["height"] = int(self.game_window["height"] * 0.29)

    def _draw_obstacle_zone(self):
        obstacle_zone_absolute = dict()
        obstacle_zone_absolute["left"] = self.game_window["left"] + self.obstacle_zone["left"]
        obstacle_zone_absolute["top"] = self.game_window["top"] + self.obstacle_zone["top"]
        obstacle_zone_absolute["width"] = self.obstacle_zone["width"]
        obstacle_zone_absolute["height"] = self.obstacle_zone["height"]
        self.overlay.draw_rect(obstacle_zone_absolute)

    def _draw_forefront_zone(self):
        forefront_zone_absolute = dict()
        forefront_zone_absolute["left"] = self.game_window["left"] + self.forefront_zone["left"]
        forefront_zone_absolute["top"] = self.game_window["top"] + self.forefront_zone["top"]
        forefront_zone_absolute["width"] = self.forefront_zone["width"]*1.05
        forefront_zone_absolute["height"] = self.forefront_zone["height"]*1.05
        self.overlay.draw_rect(forefront_zone_absolute)

    def _long_jump(self):
        if self.frames_since_long_jump >= 10:
            self.frames_since_long_jump = 0
            press("UP", 0.005)
            print("long")
            if len(self.obstacle_queue) > 0:
                self.obstacle_queue.pop(0)

    def _short_jump(self):
        if self.frames_since_short_jump >= 25:
            self.frames_since_short_jump = 0
            pressKey("UP")
            print("short")
            if len(self.obstacle_queue) > 0:
                self.obstacle_queue.pop(0)

    def _duck(self):
        keyboard.press("down")
        time.sleep(0.3)
        keyboard.release("down")

    def _handle_forefront(self):
        bottom_right_x = self.forefront_zone["left"] + self.forefront_zone["width"]
        bottom_right_y = self.forefront_zone["top"] + self.forefront_zone["height"]
        image_forefront_zone = self.image_binary[self.forefront_zone["top"]:bottom_right_y, self.forefront_zone["left"]:bottom_right_x]

        image_padding_right = image_forefront_zone[:, :int(self.forefront_zone["width"]*0.1)]
        image_padding_left = image_forefront_zone[:, int(self.forefront_zone["width"]*0.9):]
        percent_dark_pixels_right = np.sum(image_padding_right) / (image_padding_right.shape[0]*image_padding_right.shape[1])
        percent_dark_pixels_left = np.sum(image_padding_left) / (image_padding_left.shape[0]*image_padding_left.shape[1])
        if percent_dark_pixels_right < 0.1 and percent_dark_pixels_left < 0.1:
            if self.recognize_forefront:
                image_forefront_inner = image_forefront_zone[:, int(self.forefront_zone["width"]*0.1):int(self.forefront_zone["width"]*0.9)]
                if np.sum(image_forefront_inner) / (image_forefront_inner.shape[0]*image_forefront_inner.shape[1]) > 0.1:
                    top_pixel_percent_pos = get_top_pixel_percent_pos(image_forefront_inner)
                    width_percent = get_width_percent(image_forefront_inner)
                    if top_pixel_percent_pos < 0.2:
                        if width_percent < 0.6:
                            print("SLIM TALL")
                            self.obstacle_queue += [ObstacleType.SLIM_TALL]
                        else:
                            print("WIDE TALL")
                            self.obstacle_queue += [ObstacleType.WIDE_TALL]
                    else:
                        if width_percent < 0.6:
                            print("SLIM LOW")
                            self.obstacle_queue += [ObstacleType.SLIM_LOW]
                        else:
                            print("WIDE LOW")
                            self.obstacle_queue += [ObstacleType.WIDE_LOW]
                    self.recognize_forefront = False
        else:
            self.recognize_forefront = True

    def _handle_obstacle(self):
        bottom_right_x = self.obstacle_zone["left"]+self.obstacle_zone["width"]
        bottom_right_y = self.obstacle_zone["top"]+self.obstacle_zone["height"]
        image_obstacle_zone = self.image_binary[self.obstacle_zone["top"]: bottom_right_y, self.obstacle_zone["left"]:bottom_right_x]

        amount_pixels = self.obstacle_zone["width"] * self.obstacle_zone["height"]
        amount_pixels_bottom_third = self.obstacle_zone["width"] * int(self.obstacle_zone["height"]/3)
        percent_dark_pixels = np.sum(image_obstacle_zone) / amount_pixels
        percent_dark_pixels_bottom_third = np.sum(image_obstacle_zone[int(self.obstacle_zone["height"]/3*2):, :]) / amount_pixels_bottom_third
        if percent_dark_pixels > 0.1:
            if percent_dark_pixels_bottom_third < 0.1:
                self._duck()
            else:
                if len(self.obstacle_queue) > 0:
                    if self.obstacle_queue[0] == ObstacleType.WIDE_TALL:
                        self._long_jump()
                    else:
                        self._short_jump()
                else:
                    pass
                    # self._short_jump()


def main():
    print("T-REX auto runner (by python_hackersha)")
    auto_runner = DinoAutoRunner("config.json")
    print("Press 1 to start autorun")
    while True:
        if keyboard.is_pressed('1') and not auto_runner.is_running:
            print("autorun started")
            auto_runner.start_autorun()


def test():
    print("test will be in 5 sec")
    time.sleep(5.0)
    press("UP", 0.06)


if __name__ == "__main__":
    main()

