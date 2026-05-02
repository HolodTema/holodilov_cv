import cv2
import numpy as np
# чтобы считать расстояние между двумя точками
from math import dist
# чтобы измерять время между кадрами
import time
# чтобы сохранять цвет предыдущего шара 
from pathlib import Path
# и этот цвет мы будем сохранять в config.json
import json


# директория, где лежит текущий tracking.py файл
# нужно, чтобы файл программы работал вне зависимости от своего расположения
save_path = Path(__file__).parent
config_path = save_path / "config.json"


cv2.namedWindow("Image", cv2.WINDOW_GUI_NORMAL)
cv2.namedWindow("Mask", cv2.WINDOW_GUI_NORMAL)


position = [0, 0]
clicked = False


def on_click(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at {x}, {y}")
        global position
        position = [x, y]
        global clicked
        clicked = True


cv2.setMouseCallback("Image", on_click)

cam = cv2.VideoCapture(0)
lower = None
upper = None

if config_path.exists():
    with config_path.open("r") as f:
        js = json.load(f)
        # есть вариант, что мы запускали в прошлый раз прогу. но шар не находили
        # тогда config.json существует, но он пустой. Проверим это
        if "lower" in js:
            lower = np.array(js["lower"], dtype="u1")
            upper = np.array(js["upper"], dtype = "u1")

positions = list()
prev_time = time.time()
curr_time = time.time()
# диаметр шарика 6.36 сантиметра
d = 6.36

while cam.isOpened():
    ret, frame = cam.read()
    # blur the frame from the camera to get better contours
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    # convert frame from the camera to HSV color format
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    if clicked:
        clicked = False
        color = hsv[position[1], position[0]]
        # every number in HSV will be -10% or +10%
        # but color values can go out 255 - use np.clip()
        # and convert it to int with astype()
        lower = np.clip(color * 0.9, 0, 255).astype("u1")
        upper = np.clip(color * 1.1, 0, 255).astype("u1")
    if lower is not None:
        # inr = in range = mask 
        inr = cv2.inRange(hsv, lower, upper)
        mask = cv2.morphologyEx(inr, cv2.MORPH_CLOSE, np.ones((5, 5), dtype="u1"))
        cv2.imshow("Mask", mask)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            # находим максимальный по площади контур из всех обнаруженных контуров
            contour = max(contours, key=cv2.contourArea)
            # подбираем минимального размера круг, в который контур помещается
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if radius > 10:
                x = int(x)
                y = int(y)
                radius = int(radius)
                # если максимальный контур хоть-сколько-то большой (радиус > 10) - это наш круг
                cv2.circle(frame, (x, y), radius, (0, 255, 255), 4)
                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                positions += [(x, y)]
                # to prevent out of memory we keep not more than 20 positions
                if len(positions) > 20:
                    positions.pop(0)
                # рисуем хвост
                for i, position in enumerate(positions[:-1]):
                    # затемнение
                    last_color_value = 100 + 155 / len(positions) * i
                    # размер i*2 чтобы хвост уменьшался постепенно
                    cv2.circle(frame, position, i*2, (0, 0, last_color_value), -1)
        
                curr_time = time.time()
                delta = curr_time - prev_time
                # можем считать только в том случае, если у нас есть хотя бы пара 
                # позиций в истории
                if len(positions) >= 2:
                    curr_pos = positions[-1]
                    prev_pos = positions[-2]
                    dst = dist(prev_pos, curr_pos)
                    # коэффициент, переводящий пиксели в сантиметр объекта
                    # то есть радиус в пикселях
                    pxl_per_cm = d / (2 * radius)
                    pxl_per_m = pxl_per_cm / 100
                    # speed - число, модуль скорости
                    # velocity - скорость как вектор
                    # вычисляем скорость в пикселях, а потом переводим ее в м/c
                    speed = dst / delta * pxl_per_m
                    cv2.putText(frame, f"Speed = {speed:.2f}m/s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0))
                prev_time = curr_time
    cv2.imshow("Image", frame)


cam.release()
cv2.destroyAllWindows()

# сохраняем цвет шарика, с которым работали, в config.json
with config_path.open("w") as f:
    json.dump(
        {
            "lower": None if lower is None else lower.tolist(),
            "upper": None if upper is None else upper.tolist()
        },
        f
    )

