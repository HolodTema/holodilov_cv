import time
import pyautogui
import pyscreenshot
import numpy as np
import keyboard


def check_obstacle():
    BBOX_CHECK_TOP_LEFT_X = 300
    BBOX_CHECK_TOP_LEFT_Y = 370
    BBOX_CHECK_BOTTOM_RIGHT_X = 350
    BBOX_CHECK_BOTTOM_RIGHT_Y = 380

    screenshot = pyscreenshot.grab(bbox=(BBOX_CHECK_TOP_LEFT_X, BBOX_CHECK_TOP_LEFT_Y, BBOX_CHECK_BOTTOM_RIGHT_X, BBOX_CHECK_BOTTOM_RIGHT_Y))
    array_screenshot = np.array(screenshot)
    dark_pixels = np.sum(array_screenshot < 100)
    return dark_pixels > 20



def jump():
    keyboard.send("space")


    
def main():
    print("T-REX autorunner (by python_hackershaa)")
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
            if check_obstacle():
                jump()
                time.sleep(0.05)
            time.sleep(0.02)
        else:
            time.sleep(0.1)       



if __name__ == "__main__":
    main()


