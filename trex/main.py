import mss
import numpy as np
from pathlib import Path
import json
import keyboard
import time
from Overlay import Overlay


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
        self.speed = None
        self.background_brightness = None
        self.image_gray = None
        self.obstacle_zone = None

    def start_autorun(self):
        self.is_running = True
        self.speed = self.MIN_SPEED
        self.background_brightness = 700
        self.overlay.start()
        self.overlay.draw_rect(self.game_window)
        self._update_obstacle_zone()
        self._draw_obstacle_zone()
        while self.is_running:
            self._take_screenshot()
            self._update_obstacle_zone()
            self._handle_obstacle()
            if int(time.time()) % 3 == 0:
                self._update_background_brightness()
            if self.speed < self.MAX_SPEED:
                self.speed += self.ACCELERATION
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
        speed_delta = int(self.game_window["width"] * 0.01 * self.speed)
        self.obstacle_zone = dict()
        self.obstacle_zone["left"] = int(self.game_window["width"]*0.06) + speed_delta
        self.obstacle_zone["top"] =  int(self.game_window["height"]*0.67)
        self.obstacle_zone["width"] = int(self.game_window["width"]*0.02) + speed_delta
        self.obstacle_zone["height"] = int(self.game_window["height"]*0.32)

    def _draw_obstacle_zone(self):
        obstacle_zone_absolute = dict()
        obstacle_zone_absolute["left"] = self.game_window["left"] + self.obstacle_zone["left"]
        obstacle_zone_absolute["top"] = self.game_window["top"] + self.obstacle_zone["top"]
        obstacle_zone_absolute["width"] = self.obstacle_zone["width"]
        obstacle_zone_absolute["height"] = self.obstacle_zone["height"]
        self.overlay.draw_rect(obstacle_zone_absolute)


    def _update_background_brightness(self):
        background_zone_width = int(self.image_gray.shape[0] * 0.02)
        background_zone_height = int(self.image_gray.shape[1] * 0.02)
        background_zone = self.image_gray[:background_zone_width, :background_zone_height]
        self.background_brightness = np.median(background_zone)

    def _jump(self):
        keyboard.send("up")

    def _duck(self):
        keyboard.send("down")
        time.sleep(0.3)
        keyboard.release("down")

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
                self._jump()
        # dark_pixels = np.sum(abs(image_obstacle_zone - self.background_brightness) > 382)
        # amount_all_pixels = self.obstacle_zone["width"] * self.obstacle_zone["height"]
        # percent_dark_pixels = dark_pixels / amount_all_pixels
        # if percent_dark_pixels >= 0.05:
        #     self._jump()


def main():
    print("T-REX auto runner (by python_hackersha)")
    auto_runner = DinoAutoRunner("config.json")
    print("Press 1 to start autorun")
    while True:
        if keyboard.is_pressed('1') and not(auto_runner.is_running):
            print("autorun started")
            auto_runner.start_autorun()




if __name__ == "__main__":
    main()


