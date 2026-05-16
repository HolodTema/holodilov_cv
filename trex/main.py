import mss
from pathlib import Path
import json
import time
from Overlay import Overlay
from Obstacle import ObstacleType
from numpy_util import *
import keyboard


class DinoAutoRunner:
    MIN_SPEED = 6
    MAX_SPEED = 13
    ACCELERATION = 0.0003

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
        self.prev_duck_time = None
        self.image_binary = None
        self.obstacle_zone = None
        self.forefront_zone = None
        self.game_over_zone = None
        self.game_over_pixels = None
        self.obstacle_queue = None
        self.obstacle_handled = None
        self.canvas_obstacle_zone_id = None

    def start_autorun(self):
        self.is_running = True
        self.obstacle_handled = False
        self.prev_duck_time = time.time()
        self.speed = self.MIN_SPEED
        self.obstacle_queue = list()
        self.overlay.start()
        self.overlay.draw_rect_from_dict(self.game_window)
        self._update_forefront_zone()
        self._draw_forefront_zone()
        self._update_game_over_zone()
        self._draw_game_over_zone()
        while self.is_running:
            self._take_screenshot()
            self._handle_forefront()
            self._update_obstacle_zone()
            if self.canvas_obstacle_zone_id is not None:
                self.overlay.clear_by_canvas_id(self.canvas_obstacle_zone_id)
            self._handle_obstacle()
            self.canvas_obstacle_zone_id = self._draw_obstacle_zone()
            if self.speed < self.MAX_SPEED:
                self.speed += self.ACCELERATION
            # game_over_pixels_now = self._get_game_over_pixels()
            # if game_over_pixels_now == self.game_over_pixels and game_over_pixels_now > 30:
            #     print("GAME OVER!")
            #     break
            # self.game_over_pixels = game_over_pixels_now
            time.sleep(0.005)

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
        obstacle_type_coefficient = 0.15
        if len(self.obstacle_queue) > 0:
            if self.obstacle_queue[0] == ObstacleType.WIDE_TALL:
                obstacle_type_coefficient = 0.13
            if self.obstacle_queue[0] == ObstacleType.SLIM_TALL:
                obstacle_type_coefficient = 0.15
            if self.obstacle_queue[0] == ObstacleType.WIDE_LOW:
                obstacle_type_coefficient = 0.17
            if self.obstacle_queue[0] == ObstacleType.SLIM_LOW:
                obstacle_type_coefficient = 0.20

        speed_delta = int(0.019 * self.speed)
        self.obstacle_zone = dict()
        self.obstacle_zone["left"] = int(self.game_window["width"] * (0.14 + speed_delta))
        self.obstacle_zone["top"] = int(self.game_window["height"] * 0.7)
        self.obstacle_zone["width"] = int(self.game_window["width"] * obstacle_type_coefficient)
        self.obstacle_zone["height"] = int(self.game_window["height"] * 0.29)

    def _update_forefront_zone(self):
        self.forefront_zone = dict()
        self.forefront_zone["left"] = int(self.game_window["width"] * 0.82)
        self.forefront_zone["top"] = int(self.game_window["height"] * 0.7)
        self.forefront_zone["width"] = int(self.game_window["width"] * 0.12)
        self.forefront_zone["height"] = int(self.game_window["height"] * 0.29)

    def _update_game_over_zone(self):
        self.game_over_zone = dict()
        self.game_over_zone["left"] = int(self.game_window["width"] * 0.48)
        self.game_over_zone["top"] = int(self.game_window["height"] * 0.57)
        self.game_over_zone["width"] = int(self.game_window["width"] * 0.045)
        self.game_over_zone["height"] = int(self.game_window["height"] * 0.18)

    def _draw_obstacle_zone(self):
        obstacle_zone_absolute = dict()
        obstacle_zone_absolute["left"] = self.game_window["left"] + self.obstacle_zone["left"]
        obstacle_zone_absolute["top"] = self.game_window["top"] + self.obstacle_zone["top"]
        obstacle_zone_absolute["width"] = self.obstacle_zone["width"]
        obstacle_zone_absolute["height"] = self.obstacle_zone["height"]
        return self.overlay.draw_rect_from_dict(obstacle_zone_absolute)

    def _get_game_over_pixels(self):
        bottom_right_x = self.game_over_zone["left"] + self.game_over_zone["width"]
        bottom_right_y = self.game_over_zone["top"] + self.game_over_zone["height"]
        image_game_over = self.image_binary[self.game_over_zone["top"]:bottom_right_y, self.game_over_zone["left"]:bottom_right_x]
        return np.sum(image_game_over)

    def _draw_forefront_zone(self):
        forefront_zone_absolute = dict()
        forefront_zone_absolute["left"] = self.game_window["left"] + self.forefront_zone["left"]
        forefront_zone_absolute["top"] = self.game_window["top"] + self.forefront_zone["top"]
        forefront_zone_absolute["width"] = self.forefront_zone["width"]*1.05
        forefront_zone_absolute["height"] = self.forefront_zone["height"]*1.05
        self.overlay.draw_rect_from_dict(forefront_zone_absolute)

    def _draw_game_over_zone(self):
        game_over_zone_absolute = dict()
        game_over_zone_absolute["left"] = self.game_window["left"] + self.game_over_zone["left"]
        game_over_zone_absolute["top"] = self.game_window["top"] + self.game_over_zone["top"]
        game_over_zone_absolute["width"] = self.game_over_zone["width"]
        game_over_zone_absolute["height"] = self.game_over_zone["height"]
        self.overlay.draw_rect_from_dict(game_over_zone_absolute)

    def _jump(self):
        if not self.obstacle_handled:
            self.obstacle_handled = True
            keyboard.send("up")
            print("jump sent")
            if len(self.obstacle_queue) > 0:
                self.obstacle_queue.pop(0)

    def _duck(self):
        curr_time = time.time()
        if curr_time - self.prev_duck_time > 0.35:
            self.prev_duck_time = curr_time
            keyboard.press("down")
        elif curr_time - self.prev_duck_time > 0.33:
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
                    # bottom_pixel_percent_pos = get_bottom_pixel_percent_pos(image_forefront_inner)
                    # if bottom_pixel_percent_pos <= 0.45:
                    #     print("BIRD TO DUCK")
                    #     self.obstacle_queue += [ObstacleType.BIRD_TO_DUCK]
                    #     self.recognize_forefront = False
                    #     return

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
        amount_pixels_bottom_half = self.obstacle_zone["width"] * (self.obstacle_zone["height"]//2)
        percent_dark_pixels = np.sum(image_obstacle_zone) / amount_pixels
        percent_dark_pixels_bottom_half = np.sum(image_obstacle_zone[self.obstacle_zone["height"]//2:, :]) / amount_pixels_bottom_half
        if percent_dark_pixels > 0.05:
            if percent_dark_pixels_bottom_half < 0.05:
                self._duck()
            else:
                self._jump()
        else:
            self.obstacle_handled = False


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

