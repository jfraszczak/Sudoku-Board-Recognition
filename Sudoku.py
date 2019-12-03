import cv2
import matplotlib.pyplot as plt
import numpy as np
import math
import statistics


def image_preprocessing(image):
    processed_img = cv2.GaussianBlur(image.copy(), (9, 9), 0)
    processed_img = cv2.adaptiveThreshold(processed_img , 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
    processed_img = cv2.bitwise_not(processed_img, processed_img)

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(2,2))
    processed_img = cv2.dilate(processed_img, kernel, iterations= 1)

    return processed_img

def find_contours(image):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    if len(contours) > 0:
        rectangle = contours[0]
    else:
        rectangle = []

    return rectangle

def extract_corners(external_contour):
    top_left = top_right = bottom_left = bottom_right = (external_contour[0][0][0], external_contour[0][0][1])

    for point in external_contour:
        if point[0][0] + point[0][1] < top_left[0] + top_left[1]:
            top_left = (point[0][0], point[0][1])
        elif point[0][0] - point[0][1] > top_right[0] - top_right[1]:
            top_right = (point[0][0], point[0][1])
        elif point[0][0] - point[0][1] < bottom_left[0] - bottom_left[1]:
            bottom_left = (point[0][0], point[0][1])
        elif point[0][0] + point[0][1] > bottom_right[0] + bottom_right[1]:
            bottom_right = (point[0][0], point[0][1])

    return [top_left, top_right, bottom_left, bottom_right]

def distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** (1 / 2)

def perspective_transformation(corners, img):
    rows, cols, _ = img.shape
    top_left, top_right, bottom_left, bottom_right = corners[0], corners[1], corners[2], corners[3]
    length = max([
        distance(top_left, top_right),
        distance(top_left, bottom_left),
        distance(top_right, bottom_right),
        distance(bottom_left, bottom_right)
    ])

    points_before = np.float32([[corners[0][0], corners[0][1]], [corners[1][0], corners[1][1]], [corners[2][0], corners[2][1]], [corners[3][0], corners[3][1]]])
    points_after = np.float32([[0, 0], [length - 1, 0], [0, length - 1], [length - 1, length - 1]])

    matrix = cv2.getPerspectiveTransform(points_before, points_after)
    result = cv2.warpPerspective(img, matrix, (int(length), int(length)))

    return result

def divide_grid(img):
    size = img.shape[:1][0]
    lines = []

    for i in range(9):
        line = i / 9 * size
        lines.append(line)

    return lines

def line_covers(rho, array, line_num, img):
    length = img.shape[:1][0] / 9
    flag = False
    if line_num == 0:
        if rho < 10:
            flag = True
    elif abs(statistics.mean(array[line_num - 1]) + length - rho) < 10:
        flag = True

    return flag

def calculate_edges(new_perspective):
    length = new_perspective.shape[:1][0] / 9

    new_perpsective_gray = cv2.cvtColor(new_perspective, cv2.COLOR_BGR2GRAY)

    lines = cv2.HoughLines(new_perpsective_gray, 1, np.pi / 180, 150, None, 100, 0)

    vertical = []
    chorizontal = []

    if lines is not None:
        for line_num in range(10):
            tmp_ver = []
            tmp_chor = []
            for i in range(0, len(lines)):
                rho = lines[i][0][0]
                theta = lines[i][0][1]

                if theta / math.pi * 180 > -0.01 and theta / math.pi * 180 < 0.01 and line_covers(rho, vertical, line_num, new_perspective):
                    tmp_ver.append(rho)

                if theta / math.pi * 180 > 89 and theta / math.pi * 180 < 91 and line_covers(rho, chorizontal, line_num, new_perspective):
                    tmp_chor.append(rho)

            vertical.append(tmp_ver)
            chorizontal.append(tmp_chor)

    vertical_means = []
    chorizontal_means = []
    for i in range(len(vertical)):
        if len(vertical[i]) > 0:
            vertical_means.append(statistics.mean(vertical[i]))
        else:
            vertical_means.append(length * i)

    for i in range(len(chorizontal)):
        if len(chorizontal[i]) > 0:
            chorizontal_means.append(statistics.mean(chorizontal[i]))
        else:
            chorizontal_means.append(length * i)

    for m in vertical_means:
        pt1 = (int(m), 1000)
        pt2 = (int(m), -1000)
        cv2.line(new_perspective, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)

    for m in chorizontal_means:
        pt1 = (1000, int(m))
        pt2 = (-1000, int(m))
        cv2.line(new_perspective, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)

    return new_perspective, vertical_means, chorizontal_means

def crop_digits(image, vertical, chorizontal):
    digits = []
    size = image.shape[:1][0] / 9
    for i in range(9):
        for j in range(9):
            y1 = int(chorizontal[i] + size / 10)
            y2 = int(chorizontal[i + 1] - size / 10)
            x1 = int(vertical[j] + size / 10)
            x2 = int(vertical[j + 1] - size / 10)

            cropped_img = image[y1:y2, x1:x2]
            digits.append(cropped_img)

    return digits



def main(file, show):

    img = cv2.imread(file)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed = image_preprocessing(img_gray)
    if(show):
        plt.imshow(processed, cmap = 'gray')
        plt.show()

    contour = find_contours(processed)
    processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2RGB)
    pom = processed.copy()
    cv2.drawContours(pom, [contour], 0, (255, 0, 0), 3)
    if(show):
        plt.imshow(pom)
        plt.show()

    points = extract_corners(contour)

    pom = processed.copy()
    for point in points:
        cv2.circle(pom, point, 7, (255, 0, 0), -1)
    if(show):
        plt.imshow(pom)
        plt.show()

    new_perpsective = perspective_transformation(points, processed)
    if(show):
        plt.imshow(new_perpsective)
        plt.show()

    lin = divide_grid(new_perpsective)

    pom = new_perpsective.copy()
    edges, vertical, chorizontal = calculate_edges(pom)
    if(show):
        plt.imshow(edges, cmap = 'gray')
        plt.show()

    img_transformed = perspective_transformation(points, img)



    digits = crop_digits(img_transformed, vertical, chorizontal)
    return digits
