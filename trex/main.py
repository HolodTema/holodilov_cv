import time
import pyautogui
import pyscreenshot
import numpy as np
import keyboard
import json
from pathlib import Path
import matplotlib.pyplot as plt


def import_config_file():
    path = Path(__file__).parent / "config.json"
    if not(path.exists()):
        return None
    with path.open("r") as f:
        return json.load(f)



def check_obstacle(game_window):
    width = game_window["x_bottom_right"] - game_window["x_top_left"]
    height = game_window["y_bottom_right"] - game_window["y_top_left"]
    BBOX_CHECK_TOP_LEFT_X = game_window["x_top_left"] + int(width * 0.15)
    BBOX_CHECK_TOP_LEFT_Y = game_window["y_bottom_right"] - int(height * 0.3)
    BBOX_CHECK_BOTTOM_RIGHT_X = game_window["x_top_left"] + int(width * 0.3)
    BBOX_CHECK_BOTTOM_RIGHT_Y = game_window["y_bottom_right"]

    screenshot = pyscreenshot.grab(bbox=(BBOX_CHECK_TOP_LEFT_X, BBOX_CHECK_TOP_LEFT_Y, BBOX_CHECK_BOTTOM_RIGHT_X, BBOX_CHECK_BOTTOM_RIGHT_Y))
    array_screenshot = np.array(screenshot)
    plt.imshow(array_screenshot)
    plt.show()
    gray = np.sum(array_screenshot, axis=2)
    print(gray.shape)
    dark_pixels = np.sum(gray < 30)
    print(dark_pixels)
    return dark_pixels > 5000



def jump():
    keyboard.send("space")


    
def main():
    print("T-REX autorunner (by python_hackershaa)")
    game_window = import_config_file()
    if game_window is None:
        print("Error: you need to create config.json file with coordinates of game window")
        return
    
    print("Game window configured from config.json:")
    print(f"top_left: ({game_window["x_top_left"]}, {game_window["y_top_left"]})")
    print(f"bottom_right: ({game_window["x_bottom_right"]}, {game_window["y_bottom_right"]})")
    print()
    print("1 - start autorun")
    print("2 - stop autorun")
    print("3 - quit")
    print()

    is_running = False

    while True:
        if keyboard.is_pressed('1'):
            if not is_running:
                is_running = True
                print("autorun started")

        if keyboard.is_pressed('2'):
            if is_running:
                is_running = False
                print("autorun stopped")

        if keyboard.is_pressed('3'):
            print("quit")
            break

        if is_running:
            if check_obstacle(game_window):
                jump()
                time.sleep(0.05)
            time.sleep(0.02)
        else:
            time.sleep(0.1)       



if __name__ == "__main__":
    main()


