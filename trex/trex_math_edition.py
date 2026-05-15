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
        self.is_running = None
        self.recognize_forefront = None
        self.speed = None
        self.DINO_LEFT = int(self.game_window.width * 0.063)
        self.DINO_RIGHT = int(self.game_window.width * 0.135)
        self.is_jumping = False
        self.jump_end_time = 0
        self.forefront_zone = None
        self.obstacle_queue = None
        self.image_binary = None

    def start_autorun(self):
        self.is_running = True
        self.is_jumping = False
        self.recognize_forefront = True
        self.speed = self.MIN_SPEED
        self.obstacle_queue = list()
        self.forefront_zone = Zone(
            left=int(self.game_window.width * 0.78),
            top=int(self.game_window.height * 0.7),
            width=int(self.game_window.width * 0.17),
            height=int(self.game_window.height * 0.29)
        )

        self.overlay.start()
        self.overlay.draw_rect_from_zone(self.game_window)
        self.overlay.draw_rect_from_zone(self.forefront_zone.get_absolute_zone_from_parent_zone(self.game_window))

        self.overlay.draw_rect(
            top_left_x=self.game_window.left+self.DINO_LEFT,
            top_left_y=int(self.game_window.top+self.game_window.height*0.8),
            width=1,
            height=1
        )

        self.overlay.draw_rect(
            top_left_x=self.game_window.left + self.DINO_RIGHT,
            top_left_y=int(self.game_window.top + self.game_window.height * 0.8),
            width=1,
            height=1
        )

        prev_time = time.time()
        canvas_ids = list()
        while self.is_running:
            for canvas_id in canvas_ids:
                self.overlay.clear_by_canvas_id(canvas_id)
            # now_time = time.time()
            # delta_time = now_time - prev_time
            # if delta_time < 1/60:
            #     time.sleep(1/60 - delta_time)
            # prev_time = time.time()

            self._take_screenshot()
            self._handle_forefront()
            canvas_ids = self._handle_obstacle_queue()
            if self.is_jumping and time.time() >= self.jump_end_time:
                self.is_jumping = False
            if self.speed < self.MAX_SPEED:
                self.speed += self.ACCELERATION
            time.sleep(0.016)

    def stop_autorun(self):
        self.overlay.stop()
        self.is_running = False

    def _take_screenshot(self):
        with mss.MSS() as sct:
            image = np.array(sct.grab(self.game_window.convert_to_dict()))[:, :, :-1]
            image_gray = np.sum(image, axis=2)
            self.image_binary = (image_gray < 600)

    def _jump(self):
        if self.is_jumping:
            return
        keyboard.send("up")
        print("JUMP")
        self.is_jumping = True
        jump_duration = self._get_jump_duration()
        self.jump_end_time = time.time() + jump_duration

    def _duck(self):
        pass

    def _get_jump_duration(self):
        return (20.0 - self.speed / 5.0) / 36.0

    def _handle_forefront(self):
        horizontal_padding = int(self.forefront_zone.width * 0.1)
        zone_forefront_left = Zone(
            left=self.forefront_zone.left,
            top=self.forefront_zone.top,
            width=horizontal_padding,
            height=self.forefront_zone.height
        )
        zone_forefront_right = Zone(
            left=self.forefront_zone.get_bottom_right_x()-horizontal_padding,
            top=self.forefront_zone.top,
            width=horizontal_padding,
            height=self.forefront_zone.height
        )
        image_left = zone_forefront_left.crop_np_image(self.image_binary)
        image_right = zone_forefront_right.crop_np_image(self.image_binary)

        percent_dark_pixels_left = np.sum(image_left) / get_amount_pixels(image_left)
        percent_dark_pixels_right = np.sum(image_right) / get_amount_pixels(image_right)

        if percent_dark_pixels_right < 0.05 and percent_dark_pixels_left < 0.05:
            if self.recognize_forefront:
                zone_inner = Zone(
                    left=self.forefront_zone.left + horizontal_padding,
                    top=self.forefront_zone.top,
                    width=self.forefront_zone.width - horizontal_padding,
                    height=self.forefront_zone.height
                )
                image_inner = zone_inner.crop_np_image(self.image_binary)
                percent_dark_pixels_inner = np.sum(image_inner) / get_amount_pixels(image_inner)
                if percent_dark_pixels_inner > 0.05:
                    obstacle = Obstacle(
                        game_window=self.game_window,
                        zone=zone_inner,
                        image=image_inner
                    )
                    print("Obstacle isTall = ", obstacle.is_tall, "\tisWide = ", obstacle.is_wide)
                    self.obstacle_queue += [obstacle]
                    self.recognize_forefront = False
        else:
            self.recognize_forefront = True

    def _handle_obstacle_queue(self):
        canvas_ids = list()
        for i in range(len(self.obstacle_queue)):
            self.obstacle_queue[i].move_with_speed(self.speed)
            zone_to_draw = Zone(
                left=self.obstacle_queue[i].right_border,
                top=self.game_window.height + 20,
                width=2,
                height=2
            )
            canvas_ids += [self.overlay.draw_rect_from_zone(zone_to_draw.get_absolute_zone_from_parent_zone(self.game_window), outline="green")]

        # self.obstacle_queue = [obstacle for obstacle in self.obstacle_queue if obstacle.right_border < self.DINO_LEFT]

        # if len(self.obstacle_queue) == 0 or self.is_jumping:
        if len(self.obstacle_queue) == 0:
            # print("queue is empty, return")
            return canvas_ids

        first_obstacle: Obstacle = self.obstacle_queue[0]
        if first_obstacle.is_tall:
            coeff = -0.1
        else:
            coeff = -0.07

        if self.speed*((self._get_jump_duration())*60+coeff) >= (first_obstacle.right_border-self.DINO_LEFT):
            self._jump()
            self.obstacle_queue.pop(0)
        else:
            pass
            # print("I see I cannot jump")
        return canvas_ids


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

