import mss
import numpy as np
from pathlib import Path
import json
import keyboard
import time
from Overlay import Overlay



def import_config_file():
    path = Path(__file__).parent / "config.json"
    if not(path.exists()):
        return None
    with path.open("r") as f:
        return json.load(f)


def draw_game_frame_overlay(overlay, game_window):
    x_top_left = game_window["left"] 
    y_top_left = game_window["top"] 
    x_bottom_right = x_top_left + game_window["width"] 
    y_bottom_right = y_top_left + game_window["height"] 
    overlay.draw_rect(x_top_left, y_top_left, x_bottom_right, y_bottom_right, outline="red", width=2)


def draw_obstacle_check_zone_overlay(overlay, top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    overlay.draw_rect(top_left_x, top_left_y, bottom_right_x, bottom_right_y, outline="green", width=2)



def take_screenshot(game_window):
    with mss.MSS() as sct:
        image = np.array(sct.grab(game_window))[:, :, :-1]
        image_gray = np.sum(image, axis=2)
        return image_gray



def get_background_brightness(image_gray):
    background_zone_width = int(image_gray.shape[0]*0.02)
    background_zone_height = int(image_gray.shape[1]*0.02)
    background_zone = image_gray[:background_zone_width, :background_zone_height]
    return np.median(background_zone)



def check_obstacle(overlay, game_window, image_gray, speed, background_brightness):
    width = image_gray.shape[1]
    height = image_gray.shape[0]
    obstacle_zone_left = int(width*0.11)
    obstacle_zone_top = int(height*0.67)
    obstacle_zone_height = int(height*0.325)
    obstacle_zone_width = int(width*0.17)
    obstacle_zone_bottom = obstacle_zone_top + obstacle_zone_height
    obstacle_zone_right = obstacle_zone_left + obstacle_zone_width

    obstacle_zone = image_gray[obstacle_zone_top:obstacle_zone_bottom, obstacle_zone_left:obstacle_zone_right]
    draw_obstacle_check_zone_overlay(overlay, obstacle_zone_left, obstacle_zone_top, obstacle_zone_right, obstacle_zone_bottom)
    # threshold = background_brightness - 50
    dark_pixels = np.sum(abs(obstacle_zone - background_brightness) > 382)
    amount_all_pixels = obstacle_zone_width * obstacle_zone_height
    percent_dark_pixels = dark_pixels / amount_all_pixels
    if percent_dark_pixels < 0.05:
        return None
    return "jump"
    center_row = obstacle_zone.shape[0] // 2
    gray_top = obstacle_zone[:center_row, :]
    gray_bottom = obstacle_zone[center_row:, :]

    dark_pixels_top = np.sum(abs(gray_top - background_brightness) > 382)
    dark_pixels_bottom = np.sum(abs(gray_bottom - background_brightness) > 382)

    if dark_pixels_top > dark_pixels_bottom * 3:
        return "duck"
    else:
        return "jump"



def jump():
    keyboard.send("up")



def duck():
    keyboard.send("down")
    time.sleep(0.3)
    keyboard.release("down")


    
def main():
    overlay = Overlay()
    overlay.start()

    game_window = import_config_file()
    draw_game_frame_overlay(overlay, game_window)

    print("T-REX autorunner (by python_hackershaa)")
    if game_window is None:
        print("Error: you need to create config.json file with coordinates of game window")
        return
    print("Game window configured from config.json")
    print()
    print("1 - start autorun")
    print("2 - stop autorun")
    print("3 - quit")
    print()

    is_running = False
    speed = 6
    background_brightness = 700

    while True:
        if keyboard.is_pressed('1') and not(is_running):
            is_running = True
            print("autorun started")
            time.sleep(0.2)
        if keyboard.is_pressed('2') and is_running:
            is_running = False
            print("autorun stopped")
            time.sleep(0.2)
        if keyboard.is_pressed('3'):
            print("quit")
            break

        if is_running:
            overlay.clear()
            image_gray = take_screenshot(game_window)
            draw_game_frame_overlay(overlay, game_window)
            if int(time.time()) % 3 == 0:
                background_brightness = get_background_brightness(image_gray)

            action = check_obstacle(overlay, image_gray, speed, background_brightness)
            if action == "jump":
                jump()
            elif action == "duck":
                duck()

            if speed < 15:
                speed += 0.002
            
            time.sleep(0.01)
        else:
            time.sleep(0.16)  
    overlay.stop()



if __name__ == "__main__":
    main()


