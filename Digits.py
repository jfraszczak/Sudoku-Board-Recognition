import Sudoku
import matplotlib.pyplot as plt
import cv2
import numpy as np

def preprocessing(image):
    #processed_img = cv2.GaussianBlur(image.copy(), (9, 9), 0)
    threshold = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
    threshold_inv = cv2.bitwise_not(threshold, threshold)

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(2,2))
    threshold_inv = cv2.erode(threshold_inv, kernel, iterations= 1)
    #threshold_inv = cv2.dilate(threshold_inv, kernel, iterations=1)

    return threshold_inv

def bounding_box(external_contour):
    x1, x2, y1, y2 = 100000, 0, 100000, 0

    for point in external_contour:
        if point[0][0] < x1:
            x1 = point[0][0]
        elif point[0][0] > x2:
            x2 = point[0][0]
        if point[0][1] < y1:
            y1 = point[0][1]
        elif point[0][1] > y2:
            y2 = point[0][1]

    return [(x1, y1), (x2, y2)]

def generate_black_canvas(width, height):
    canvas = np.ones(shape=[28, 28, 3], dtype=np.uint8)
    canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)

    return canvas

def read_grid(digits):
    grid = []
    grid_info = []

    for digit in digits:
        digit_gray = cv2.cvtColor(digit, cv2.COLOR_BGR2GRAY)
        processed = preprocessing(digit_gray)

        contour = Sudoku.find_contours(processed)
        pom = processed.copy()
        pom = cv2.cvtColor(pom, cv2.COLOR_GRAY2RGB)
        if len(contour) > 0:
            x, y, w, h = cv2.boundingRect(contour)
            #cv2.rectangle(pom, (x, y), (x + w, y + h), (0, 255, 0), 1)
            size = w * h / (len(digit) * len(digit[0]))
            #print(size)
            #plt.imshow(pom)
            #plt.show()
            if size > 0.1 and size < 0.9:
                #print(size)
                box = bounding_box(contour)
                #cv2.rectangle(pom, (box[0][0], box[0][1]), (box[1][0], box[1][1]), (0, 255, 0), 1);
                #plt.imshow(pom)
                #plt.show()

                cropped_digit= processed[box[0][1]:box[1][1], box[0][0]:box[1][0]]
                black_canvas = generate_black_canvas(28, 28)
                rows = len(cropped_digit)
                columns = len(cropped_digit[0])

                columns = int(20 / rows * columns)
                rows = 20

                cropped_digit = cv2.resize(cropped_digit, (columns, rows))

                x1 = int((28 - rows) / 2)
                x2 = int((28 - rows) / 2) + rows
                y1 = int((28 - columns) / 2)
                y2 = int((28 - columns) / 2) + columns
                black_canvas[x1:x2, y1:y2] = cropped_digit

                black_canvas = 1. * (np.array(black_canvas) / 255 > 0.1)
                grid_info.append(1)
                grid.append(black_canvas)
                #plt.imshow(black_canvas, cmap='gray')
                #plt.show()
            else:
                grid_info.append(0)
        else:
            grid_info.append(0)


    grid = np.asarray(grid)
    digits = grid.reshape((grid.shape[0], 28, 28, 1)).astype('float32')

    return digits, grid_info


