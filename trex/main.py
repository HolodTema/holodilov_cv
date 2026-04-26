import time
import pyautogui
from PIL import ImageGrab
import numpy as np
from pynput.keyboard import Key, Listener, Controller


def check_obstacle():
    BBOX_CHECK_TOP_LEFT_X = 300
    BBOX_CHECK_TOP_LEFT_Y = 370
    BBOX_CHECK_BOTTOM_RIGHT_X = 350
    BBOX_CHECK_BOTTOM_RIGHT_Y = 380

    screenshot = ImageGrab.grab(bbox=(BBOX_CHECK_TOP_LEFT_X, BBOX_CHECK_TOP_LEFT_Y, BBOX_CHECK_BOTTOM_RIGHT_X, BBOX_CHECK_BOTTOM_RIGHT_Y))
    array_screenshot = np.array(screenshot)
    dark_pixels = np.sum(array_screenshot < 100)
    return dark_pixels > 20



def jump(keyboard_controller):
    keyboard_controller.press(Key.space)
    time.sleep(0.01)
    keyboard_controller.release(Key.space)


    
def main():
    print("T-REX autorunner (by python_hackershaa)")
    print("F2 - start autorun")
    print("F3 - stop autorun")
    print("F4 - quit")
    print()

    is_running = False

    keyboard_controller = Controller()

    def on_press(key):
        nonlocal is_running
        try:
            if hasattr(key, "char") and key.char:
                if key.char == "2":
                    is_running = True
                    print("Autorun started")
                elif key.char == "3":
                    is_running = False
                    print("Autorun stopped")
                elif key.char == "4":
                    print("Quit")
                    return False
        except Exception as e:
            print("error occured:", e)
        return True


    with Listener(on_press=on_press) as listener:
        while listener.running:
            if is_running:
                if check_obstacle():
                    jump(keyboard_controller)
                    time.sleep(0.05)
                time.sleep(0.02)
            



if __name__ == "__main__":
    main()


