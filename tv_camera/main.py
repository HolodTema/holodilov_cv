import cv2
import matplotlib.pyplot as plt
import numpy as np



def main():
    news = cv2.imread("./news.jpg")

    # corners of screen on news.jpg
    news_corners = np.array([[18, 25], [432, 53], [435, 270], [39, 294]], dtype="f4")

    # for the first frame we need to calculate perspective-matrix, so we use the flag
    is_fist_frame = True
    frame_height = 0
    frame_width = 0
    matrix = 0
    frame_corners = 0

    # starting getting images from PC camera
    camera = cv2.VideoCapture(1)
    while camera.isOpened():
        # get another one frame from the camera
        is_frame_got, frame = camera.read()
        if not is_frame_got:
            break
        
        if is_first_frame:
            frame_height, frame_width, _ = frame.shape
            frame_corners = np.array([[0, 0], [frame_width, 0], [frame_width, frame_height], [0, frame_height]], dtype="f4")
            matrix = cv2.getPerspectiveTransform(frame_corners, news_corners)
            is_first_frame = False

        frame_transformed = cv2.warpPerspective(frame, matrix, (news.shape[1], news.shape[0]))

        # make transformed frame grayscale to make it binary later
        frame_transformed_gray = cv2.cvtColor(frame_transformed, cv2.COLOR_BGR2GRAY)

        # then make frame binary with threshold() function. It is our mask
        mask = cv2.threshold(frame_transformed_gray, 1, 255, cv2.THRESH_BINARY)

        # invert the mask to use it on background
        mask_inverted = cv2.bitwise_not(mask)

        background = cv2.bitwise_and(news, news, mask=mask_inverted)
        foreground = cv2.bitwise_and(frame_transformed, frame_transformed, mask=mask)

        image_result = cv2.add(background, foreground)

        cv2.imshow("TV camera task", image_result)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    # close windows and clear program resources
    camera.release()
    cv2.destroyAllWindows()




if __name__ == "__main__":
    main()


