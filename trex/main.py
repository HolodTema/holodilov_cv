import mss
import numpy as np
from pathlib import Path
import json
import keyboard
import time
import matplotlib.pyplot as plt



def import_config_file():
    path = Path(__file__).parent / "config.json"
    if not(path.exists()):
        return None
    with path.open("r") as f:
        return json.load(f)



def check_obstacle(game_window):
    obstacle_zone_left = game_window["left"] + int(game_window["width"]*0.15)
    obstacle_zone_top = game_window["top"] + int(game_window["height"]*0.7)
    obstacle_zone_height = int(game_window["height"]*0.3)
    obstacle_zone_width = int(game_window["width"]*0.1)

    obstacle_zone = {
        "left": obstacle_zone_left,
        "top": obstacle_zone_top,
        "width": obstacle_zone_width,
        "height": obstacle_zone_height
    }

    dark_pixels = 0
    with mss.MSS() as sct:
        screen = sct.grab(obstacle_zone)
        image = np.array(screen)
        gray = np.sum(image, axis=2)
        print(gray.shape)
        dark_pixels = np.sum(gray < 700)
        print(dark_pixels)
    return dark_pixels > 100



def jump():
    print("JUMP!")
    keyboard.send("space")


    
def main():
    print("T-REX autorunner (by python_hackershaa)")
    game_window = import_config_file()
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


