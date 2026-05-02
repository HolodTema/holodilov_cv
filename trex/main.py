import time
import pyautogui
import pyscreenshot
import shlex
import numpy as np
import keyboard
import json
from pathlib import Path
import matplotlib.pyplot as plt
from skimage.io import imread
import subprocess



def import_config_file():
    path = Path(__file__).parent / "config.json"
    if not(path.exists()):
        return None
    with path.open("r") as f:
        return json.load(f)



def save_obstacle_screenshot(game_window):
    width = game_window["x_bottom_right"] - game_window["x_top_left"]
    height = game_window["y_bottom_right"] - game_window["y_top_left"]
    geometry = f"{game_window["x_top_left"]},{game_window["y_top_left"]} {width}x{height}"
    command = f"grim -g {shlex.quote(geometry)} screen.png"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Screenshot creating error:", e)



def check_obstacle():
    image = imread("./screen.png")
    gray = np.sum(image, axis=2)
    dark_pixels = np.sum(gray < 30)
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
            save_obstacle_screenshot(game_window)
            if check_obstacle():
                jump()
                time.sleep(0.05)
            time.sleep(0.02)
        else:
            time.sleep(0.1)       



if __name__ == "__main__":
    main()


