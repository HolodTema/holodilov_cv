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
    dark_pixels = 0
    with mss.MSS() as sct:
        screen = sct.grab(game_window)
        image = np.array(screen)
        gray = np.sum(image, axis=2)
        plt.imshow(gray)
        plt.show()
        dark_pixels = np.sum(gray > 80)
        print(dark_pixels)
    return dark_pixels > 10000



def jump():
    print("JUMP!")
    keyboard.send("space")


    
def main():
    print("T-REX autorunner (by python_hackershaa)")
    game_window = import_config_file()
    if game_window is None:
        print("Error: you need to create config.json file with coordinates of game window")
        return
    print("Game window configured from config.json:")
    # print(f"top_left coordinates: {game_window["left"]}, {game_window["top"]}")
    # print(f"width: {game_window["width"]} height: {game_window["height"]}")
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


