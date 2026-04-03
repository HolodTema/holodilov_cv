import numpy as np
import matplotlib.pyplot as plt

# lerp - linear interpolation
# linear interpolation returns value between value1 and value2 due to linear koeff
# 
# for example, if koeff=0, then lerp=v0
# for example, if koeff=1, then lerp=v1
# for example, if koeff=0.5, then lerp = average(v0, v1)
def lin_interpolation(value0, value1, koeff):
    return (1 - koeff) * value0 + koeff * value1 


imageSize = 100
# every pixel of our sizexsize image has 3 0-255 values (like RGB)
image = np.zeros((imageSize, imageSize, 3), dtype="uint8")
# check that image is square (width = height) 
assert image.shape[0] == image.shape[1]

# rgb colors for gradient
# index0 = red
# index1 = green
# index2 = blue
color1 = [255, 128, 0]
color2 = [0, 128, 255]

# now in pixel(0, 0) we have koeff = 0 (top left corner)
# in pixel(size-1, size-1) we have koeff = 1 (bottom right corner)
maxIndexSum = 2 * (imageSize - 1)
for i in range(imageSize):
    for j in range(imageSize):
        # koeff value must be in interval 0-1, that is why we need normalization.
        koeff = (i + j) / maxIndexSum
        red = lin_interpolation(color1[0], color2[0], koeff)
        green = lin_interpolation(color1[1], color2[1], koeff)
        blue = lin_interpolation(color1[2], color2[2], koeff)
        image[i, j, :] = [red, green, blue]

plt.figure(1)
plt.imshow(image)
plt.show()
