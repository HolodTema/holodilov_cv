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

# now image is with zeros
# we need to fill our image with color gradient
for i, koeff in enumerate(np.linspace(0.0, 1, imageSize)):
    red = lin_interpolation(color1[0], color2[0], koeff/2)
    green = lin_interpolation(color1[1], color2[1], koeff/2)
    blue = lin_interpolation(color1[2], color2[2], koeff/2)
    
    # for j in range(i):
        # image[i-j, j, :] = [red, green, blue]
        # image[imageSize-1-i-j, imageSize-1-j, :] = [red, green, blue]

    paddingRow = 0
    paddingColumn = 0
    while (i - paddingRow) >= 0 and (paddingColumn < imageSize):
        image[i - paddingRow, paddingColumn, :] = [red, green, blue]
        paddingRow += 1
        paddingColumn += 1
    

    red = lin_interpolation(color1[0], color2[0], 1-koeff/2)
    green = lin_interpolation(color1[1], color2[1], 1-koeff/2)
    blue = lin_interpolation(color1[2], color2[2], 1-koeff/2)
    

    paddingRow = 0
    paddingColumn = 0
    while (i + paddingRow) < imageSize and (imageSize-1-paddingColumn) >= 0:
        image[i + paddingRow, imageSize - 1 - paddingColumn, :] = [red, green, blue]
        paddingRow += 1
        paddingColumn += 1


plt.figure(1)
plt.imshow(image)
plt.show()
