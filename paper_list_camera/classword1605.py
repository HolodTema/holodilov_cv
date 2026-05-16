import cv2
import numpy as np
import zmq
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt


def get_paper_list_corner_coords(labeled, prop):
    mask = (labeled == prop.label).astype(np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = contours[0]
    min_rotated_rect = cv2.minAreaRect(contour)
    box_points = cv2.boxPoints(min_rotated_rect).astype(np.float32)
    if (box_points[1, 0] - box_points[0, 0]) < (box_points[2, 0] - box_points[1, 0]) or (box_points[-1, 0] - box_points[0, 0]) > (box_points[1, 0] - box_points[0, 0]):
        box_points = np.array([box_points[-1, :], *box_points[:-1, :]]).astype(np.float32)
    return box_points

def main():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.connect("tcp://84.237.21.36:6002")

    cv2.namedWindow("Stream", cv2.WINDOW_GUI_NORMAL)
    cv2.namedWindow("Result", cv2.WINDOW_GUI_NORMAL)
    count = 0

    while True:
        msg = socket.recv()
        print(len(msg))
        key = cv2.waitKey(100)
        if key == ord("q"):
            break
        count += 1
        frame = cv2.imdecode(np.frombuffer(msg, np.uint8), -1)
        gray = np.sum(frame, axis=2)
        binary = gray > 300
        labeled = label(binary)
        prop = regionprops(labeled)[0]

        corners = get_paper_list_corner_coords(labeled, prop)

        canvas_width = max(prop.image.shape)
        if canvas_width == prop.image.shape[0]:
            canvas_height = prop.image.shape[1]
        else:
            canvas_height = prop.image.shape[0]

        canvas_for_text: np.ndarray = np.zeros((canvas_height, canvas_width, 3)).astype(np.uint8)
        cv2.putText(canvas_for_text, f"Count {count}", (int(canvas_width*0.65), int(canvas_height*0.9)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
        canvas_for_text_corners = np.array([
            [0, 0],
            [canvas_width, 0],
            [canvas_width, canvas_height],
            [0, canvas_height],
        ]).astype(np.float32)

        matrix = cv2.getPerspectiveTransform(canvas_for_text_corners, corners)
        canvas_for_text_transformed = cv2.warpPerspective(canvas_for_text, matrix, (frame.shape[1], frame.shape[0]))

        mask = np.any(canvas_for_text_transformed != 0, axis=2).astype(np.uint8) * 255
        mask_inverted = cv2.bitwise_not(mask)
        background = cv2.bitwise_and(frame, frame, mask=mask_inverted)
        foreground = cv2.bitwise_and(canvas_for_text_transformed, canvas_for_text_transformed, mask=mask)
        image_result = cv2.add(background, foreground)
        cv2.imshow("Stream", frame)
        cv2.imshow("Result", image_result)



if __name__ == "__main__":
    main()

