import cv2
import matplotlib.pyplot as plt
import numpy as np

# open images with news and Cheburashka
tv = cv2.imread("./news.jpg")
chebu = cv2.imread("./cheburashka.jpg", cv2.IMREAD_COLOR_RGB)

chebu_height, chebu_width, _ = chebu.shape

# corners of chebu image: top left, top right, bottom right, bottom left
chebu_corners = np.array([[0, 0], [chebu_width, 0], [chebu_width, chebu_height], [0, chebu_height]], dtype="f4")

# corners of tv-screen on news.jpg image
tv_corners = np.array([[18, 25], [432, 53], [435, 270], [39, 294]], dtype="f4")

# we need to get the matrix of perspective transformation to put Cheburashka into TV screen
matrix = cv2.getPerspectiveTransform(chebu_corners, tv_corners)

# our transformed by perspective image with Cheburashka. Background is black (pixels=0)
image_transformed = cv2.warpPerspective(chebu, matrix, (tv.shape[1], tv.shape[0]))

# make transformed image grayscale
image_transformed_gray = cv2.cvtColor(image_transformed, cv2.COLOR_BGR2GRAY)

# then make binary mask from transformed image
# threshold - дословно переводится как порог
# cv2.threshold() to make image binary with some maxval
# cv2.threshold(src_image, thresh, maxval, type)
# thresh - value from 0 to 255
# maxval - max value, which can be assigned to pixels that overcomed the thresh. Usually maxval=255
_, mask = cv2.threshold(image_transformed_gray, 1, 255, cv2.THRESH_BINARY)
# mask is binary tranformed image

# invert our mask
mask_inverted = cv2.bitwise_not(mask)

# and we use the mask_inverted to get cheburashka-image and news-image together on the single image
background = cv2.bitwise_and(tv, tv, mask=mask_inverted)
foreground = cv2.bitwise_and(image_transformed, image_transformed, mask=mask)

image_result = cv2.add(background, foreground)

# actually opencv is working in BGR (blue, green, red)
# matplotlib is working in RGB (red, green, blue)
#
# that is why now result colors are inversed
# we need to convert image_result to show it via matplotlib
background_rgb = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
image_result_rgb = cv2.add(background_rgb, foreground)

plt.imshow(image_result_rgb)
plt.show()

