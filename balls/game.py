import cv2
import numpy as np
import random
from pathlib import Path
import json


def get_random_ball_succession():
    l = ["orange", "green", "blue"]
    random.shuffle(l)
    return l


def get_x_coord(hsv, lower, upper, window_mask_name):
    inr = cv2.inRange(hsv, lower, upper)
    mask = cv2.morphologyEx(inr, cv2.MORPH_CLOSE, np.ones((5, 5), dtype="u1"))
    cv2.imshow(window_mask_name, mask)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        contour = max(contours, key=cv2.contourArea)
        (x, y), _ = cv2.minEnclosingCircle(contour)
        return x
    else:
        return None
    


def import_calibration(lower_orange, upper_orange, lower_green, upper_green, lower_blue, upper_blue):
    save_path = Path(__file__).parent
    balls_path = save_path / "balls.json"
    if balls_path.exists():
        with balls_path.open("r") as f:
            js = json.load(f)
            if "lower_orange" in js:
                lower_orange = np.array(js["lower_orange"], dtype="u1")
                upper_orange = np.array(js["upper_orange"], dtype="u1")
                lower_green = np.array(js["lower_green"], dtype="u1")
                upper_green = np.array(js["upper_green"], dtype="u1")
                lower_blue = np.array(js["lower_blue"], dtype="u1")
                upper_blue = np.array(js["upper_blue"], dtype="u1")



def export_calibration(lower_orange, upper_orange, lower_green, upper_green, lower_blue, upper_blue):
    save_path = Path(__file__).parent
    balls_path = save_path / "balls.json"
    with balls_path.open("w") as f:
        json.dump(
            {
                "lower_orange": None if lower_orange is None else lower_orange.tolist(),
                "upper_orange": None if upper_orange is None else upper_orange.tolist(),
                "lower_green": None if lower_green is None else lower_green.tolist(),
                "upper_green": None if upper_green is None else upper_green.tolist(),
                "lower_blue": None if lower_blue is None else lower_blue.tolist(),
                "upper_blue": None if upper_blue is None else upper_blue.tolist(),
            },
            f
        )


clicked = False
position = [0, 0]
def on_click(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at {x}, {y}")
        global position
        position = [x, y]
        global clicked
        clicked = True


cv2.namedWindow("Image", cv2.WINDOW_GUI_NORMAL)
cv2.namedWindow("Mask orange", cv2.WINDOW_GUI_NORMAL)
cv2.namedWindow("Mask green", cv2.WINDOW_GUI_NORMAL)
cv2.namedWindow("Mask blue", cv2.WINDOW_GUI_NORMAL)

cv2.setMouseCallback("Image", on_click)

balls = get_random_ball_succession()
text_result = ""
lower_orange = None
upper_orange = None
lower_green = None
upper_green = None
lower_blue = None
upper_blue = None

import_calibration(
    lower_orange,
    upper_orange,
    lower_green,
    upper_green,
    lower_blue,
    upper_blue
)

cam = cv2.VideoCapture(0)

while cam.isOpened():
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    if key == ord('n'):
        balls = get_random_ball_succession()
    ret, frame = cam.read()
    cv2.putText(frame, ", ".join(balls), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0))
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    if clicked:
        clicked = False
        color = hsv[position[1], position[0]]
        if lower_orange is None:
            lower_orange = np.clip(color * 0.9, 0, 255).astype("u1")
            upper_orange = np.clip(color * 1.1, 0, 255).astype("u1")
            print("Orange calibrated")
            continue
        if lower_green is None:
            lower_green = np.clip(color * 0.9, 0, 255).astype("u1")
            upper_green = np.clip(color * 1.1, 0, 255).astype("u1")
            print("Green calibrated")
            continue
        if lower_blue is None:
            lower_blue = np.clip(color * 0.9, 0, 255).astype("u1")
            upper_blue = np.clip(color * 1.1, 0, 255).astype("u1")
            print("Blue calibrated")
            continue
    else:
        if lower_orange is None:
            text_result = "CALIBRATE ORANGE"
            cv2.putText(frame, text_result, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0))
            cv2.imshow("Image", frame)
            continue
        if lower_green is None:
            text_result = "CALIBRATE GREEN"
            cv2.putText(frame, text_result, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0))
            cv2.imshow("Image", frame)
            continue
        if lower_blue is None:
            text_result = "CALIBRATE BLUE"
            cv2.putText(frame, text_result, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0))
            cv2.imshow("Image", frame)
            continue




    x_orange = get_x_coord(hsv, lower_orange, upper_orange, "Mask orange")
    x_green = get_x_coord(hsv, lower_green, upper_green, "Mask green")
    x_blue = get_x_coord(hsv, lower_blue, upper_blue, "Mask blue")

    if x_orange is None or x_green is None or x_blue is None:
        text_result = "NO BALLS"
        cv2.putText(frame, text_result, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0))
        cv2.imshow("Image", frame)
        continue
            
    coords = [("orange", x_orange), ("green", x_green), ("blue", x_blue)]
    coords = sorted(coords, key=lambda x: x[1], reverse=True)
    names = [x[0] for x in coords]
    if (names == balls):
        text_result = "VICTORY"
    else:
        text_result = "GAME OVER"
    cv2.putText(frame, text_result, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0))
    cv2.imshow("Image", frame)


cam.release()
cv2.destroyAllWindows()

with balls_path.open("w") as f:
    json.dump(
        {
            "lower_orange": None if lower_orange is None else lower_orange.tolist(),
            "upper_orange": None if upper_orange is None else upper_orange.tolist(),
            "lower_green": None if lower_green is None else lower_green.tolist(),
            "upper_green": None if upper_green is None else upper_green.tolist(),
            "lower_blue": None if lower_blue is None else lower_blue.tolist(),
            "upper_blue": None if upper_blue is None else upper_blue.tolist(),
        },
        f
    )

export_calibration(
    lower_orange,
    upper_orange,
    lower_green,
    upper_green,
    lower_blue,
    upper_blue
)

