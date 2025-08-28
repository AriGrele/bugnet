import cv2,os
import numpy as np

with open('data/pixels.txt','w') as o:                                          #output file (ssv)
        o.write('path insect x y\n')

src='../data/output/images/good'                                                #just the good images.

files=[file for file in os.listdir(src)]

print(len(files))
for i,image_path in enumerate(files):
        
    image = cv2.imread(f'{src}/{image_path}', cv2.IMREAD_GRAYSCALE)             #read black and white image

    _, thresholded = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU) #threshold to darkest portions of image

    kernel = np.ones((3, 3), np.uint8)
    closing = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #choose insect contours based on above threshold and kernel
    filled = np.zeros_like(closing)
    cv2.drawContours(filled, contours, -1, (255), thickness=cv2.FILLED)         #fill contours

    white_pixel_count = np.sum(filled == 255)                                   #count pixels
    total_pixels = image.size
    white_pixel_percentage = (white_pixel_count / total_pixels) * 100
    x_dim, y_dim = image.shape

    with open('data/pixels.txt','a') as o:
        if i%1000==0:print(i,f'{src}/{image_path} {white_pixel_count} {x_dim} {y_dim}\n')
        o.write(f'{src}/{image_path} {white_pixel_count} {x_dim} {y_dim}\n')