import math
import cv2
import numpy as np
from skimage.measure import label, regionprops
from skimage.io import imread
import matplotlib.pyplot as plt
from skimage.filters import sobel
from skimage.morphology import binary_closing
import time


def define_ball_start_x(image, props):
    x_of_highest_regionprop = 0
    y_of_highest_regionprop = image.shape[0]
    for prop in props:
        centroid = prop.centroid
        if centroid[0] < y_of_highest_regionprop:
            y_of_highest_regionprop = centroid[0]
            x_of_highest_regionprop = int(centroid[1])
    return x_of_highest_regionprop


def get_prop_by_touch_coordinate(binary, props, ball_touch_x, ball_touch_y):
    if not binary[ball_touch_y, ball_touch_x]:
        return None
    for prop in props:
        width = prop.image.shape[1]
        height = prop.image.shape[0]
        x = int(prop.centroid[1])
        y = int(prop.centroid[0])
        if ball_touch_x > x - (width//2) and ball_touch_x < x + (width//2) and ball_touch_y > y - (height//2) and ball_touch_y < y + (height//2):
            return prop
    return None


def get_prop_angle(prop):
    return prop.orientation / 3.1415 * 180


def main():
    BALL_RADIUS = 20
    FPS = 100
    HORIZONTAL_FRICTION = 0.005
    JUMP_INVERSION_KOEFFICIENT = -0.9
    cv2.namedWindow("Game", cv2.WINDOW_GUI_NORMAL)
    cv2.namedWindow("Camera", cv2.WINDOW_GUI_NORMAL)

    is_falling = False
    vspeed = 0
    hspeed = 0
    gravity = 0.2
    ball_x = 0
    ball_y = 0

    camera = cv2.VideoCapture(0)
    while camera.isOpened():

        is_frame_got, image = camera.read()
        if not is_frame_got:
            break
        image = image[::-1]

        key = cv2.waitKey(1000 // FPS)

        if not is_falling and key == ord(' '):
            gray = image.mean(2)
            contours = sobel(gray)
            binary = contours > 20
            binary = binary_closing(binary, footprint=np.ones((10, 10)))
            binary = binary[::-1, :]
            binary_to_show = (binary * 255).astype("uint8")
            labeled = label(binary)
            props = regionprops(labeled)
            props = [prop for prop in props if prop.perimeter > int(image.shape[1]*0.1)]
            orientations = [(prop.orientation / 3.1415 * 180) for prop in props]
            binary_to_show = (binary * 255).astype("uint8")
            vspeed = 0
            hspeed = 0
            ball_x = define_ball_start_x(image, props)
            ball_y = 0
            cv2.circle(binary_to_show, (ball_x, ball_y), 30, 100, -1)
            is_falling = True
            binary_to_show = (np.logical_not(binary) * 255).astype("uint8")
        if is_falling:
            binary_to_show = (np.logical_not(binary) * 255).astype("uint8")
            vspeed += gravity
            if hspeed > HORIZONTAL_FRICTION:
                hspeed -= HORIZONTAL_FRICTION
            elif hspeed < -HORIZONTAL_FRICTION:
                hspeed += HORIZONTAL_FRICTION
            ball_y += int(vspeed)
            ball_x += int(hspeed)
            cv2.circle(binary_to_show, (ball_x, ball_y), BALL_RADIUS, 100, -1)
            ball_touch_y = min(ball_y + BALL_RADIUS, binary.shape[0]-1)
            prop_to_touch = get_prop_by_touch_coordinate(binary, props, ball_x, ball_touch_y)
            if prop_to_touch != None:
                sin = math.sin(prop_to_touch.orientation)
                hspeed += int(sin * 2.5)
                vspeed = vspeed * (JUMP_INVERSION_KOEFFICIENT)


            if ball_y > image.shape[0] + BALL_RADIUS:
                is_falling = False
            cv2.imshow("Game", binary_to_show)
        cv2.imshow("Camera", image[::-1, :])

    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()
