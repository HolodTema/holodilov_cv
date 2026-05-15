import mss
from pathlib import Path
import json
import time
from Overlay import Overlay
from Zone import Zone
from Obstacle import Obstacle
from numpy_util import *
import keyboard


class DinoAutoRunner:
    MIN_SPEED = 6
    MAX_SPEED = 13
    ACCELERATION = 0.001

    def __init__(self, config_filename):
        path = Path(__file__).parent / config_filename
        if not (path.exists()):
            raise RuntimeError("Error: unable open config file.")
        with path.open("r") as f:
            self.game_window = Zone(0, 0, 0, 0)
            self.game_window.set_from_dict(json.load(f))

        self.overlay = Overlay()
        self.is_running = False
        self.recognize_forefront = True
        self.speed = None
        self.forefront_zone = None
        self.obstacle_queue = None
        self.image_binary = None

    def start_autorun(self):
        self.is_running = True
        self.speed = self.MIN_SPEED
        self.obstacle_queue = list()
        self.forefront_zone = Zone(
            left=int(self.game_window["width"] * 0.82),
            top=int(self.game_window["height"] * 0.7),
            width=int(self.game_window["width"] * 0.12),
            height=int(self.game_window["height"] * 0.29)
        )

        self.overlay.start()
        self.overlay.draw_rect_from_zone(self.game_window)
        self.overlay.draw_rect_from_zone(self.forefront_zone)

        while self.is_running:
            self._take_screenshot()
            self._handle_forefront()
            if self.speed < self.MAX_SPEED:
                self.speed += self.ACCELERATION
            time.sleep(0.0166)

    def stop_autorun(self):
        self.overlay.stop()
        self.is_running = False

    def _take_screenshot(self):
        with mss.MSS() as sct:
            image = np.array(sct.grab(self.game_window))[:, :, :-1]
            image_gray = np.sum(image, axis=2)
            self.image_binary = (image_gray < 600)

    def _jump(self):
        keyboard.send("up")

    def _duck(self):
        pass

    def _handle_forefront(self):
        image_forefront = self.forefront_zone.crop_np_image(self.image_binary)

        horizontal_padding = int(self.forefront_zone.width * 0.1)
        zone_forefront_left = Zone(
            left=self.forefront_zone.left,
            top=self.forefront_zone.top,
            width=horizontal_padding,
            height=self.forefront_zone.height
        )
        zone_forefront_right = Zone(
            left=self.forefront_zone.width-horizontal_padding,
            top=self.forefront_zone.top,
            width=horizontal_padding,
            height=self.forefront_zone.height
        )
        image_left = zone_forefront_left.crop_np_image(self.image_binary)
        image_right = zone_forefront_right.crop_np_image(self.image_binary)

        percent_dark_pixels_left = np.sum(image_left) / get_amount_pixels(image_left)
        percent_dark_pixels_right = np.sum(image_right) / get_amount_pixels(image_right)

        if percent_dark_pixels_right < 0.1 and percent_dark_pixels_left < 0.1:
            if self.recognize_forefront:
                zone_inner = Zone(
                    left=self.forefront_zone + horizontal_padding,
                    top=self.forefront_zone.top,
                    width=self.forefront_zone.width - horizontal_padding,
                    height=self.forefront_zone.height
                )
                image_inner = zone_inner.crop_np_image(self.image_binary)
                percent_dark_pixels_inner = np.sum(image_inner) / get_amount_pixels(image_inner)
                if percent_dark_pixels_inner > 0.1:
                    obstacle = Obstacle(
                        game_window=self.game_window,
                        zone=zone_inner,
                        image=image_inner
                    )
                    self.obstacle_queue += [obstacle]
                    self.recognize_forefront = False
        else:
            self.recognize_forefront = True


def main():
    print("T-REX auto runner (by python_hackersha)")
    auto_runner = DinoAutoRunner("config.json")
    print("Press 1 to start autorun")
    while True:
        if keyboard.is_pressed('1') and not auto_runner.is_running:
            print("4")
            time.sleep(1)
            print("3")
            time.sleep(1)
            print("2")
            time.sleep(1)
            print("1")
            time.sleep(1)
            print("GO!")
            auto_runner.start_autorun()


if __name__ == "__main__":
    main()

