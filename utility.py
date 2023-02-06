import cv2
import numpy as np
import ocr
import xlsxwriter
import os
import barcode
import sys


def find_areas(contours):

    found_areas = []
    for x in contours:
        area = cv2.contourArea(x)
        if area > 50:
            perimeter = cv2.arcLength(x, True)
            aproximation = cv2.approxPolyDP(x, 0.02*perimeter, True)

            if len(aproximation) == 4:
                found_areas.append(x)
    found_areas = sorted(found_areas, key=cv2.contourArea, reverse=True)
    return found_areas


def find_corner_points(contour):
    perimeter = cv2.arcLength(contour, True)
    aproximation = cv2.approxPolyDP(contour, 0.02*perimeter, True)

    return aproximation


def reorder(points):
    points = points.reshape(4, 2)
    new_points = np.zeros((4, 1, 2), np.int32)
    add = points.sum(1)

    new_points[0] = points[np.argmin(add)]
    new_points[3] = points[np.argmax(add)]
    difference = np.diff(points, axis=1)
    new_points[1] = points[np.argmin(difference)]
    new_points[2] = points[np.argmax(difference)]

    return new_points


def split_rectangles(image):
    rows = np.vsplit(image, 8)
    rectangles = []
    i = 0
    for r in rows:
        cols = np.hsplit(r, 4)
        i += 1
        for rectangle in cols:
            rectangles.append(rectangle)
    return rectangles


def get_written_answers(image):

    rows = np.vsplit(image, 9)
    ans = []

    i = 0
    while i < len(rows):
        cv2.imwrite(f'temp/{i}.jpeg', rows[i])

        ans.append(ocr.image_reader(f'temp/{i}.jpeg').rstrip())

        i += 1

    return ans


def correct_answers(image, mark_indices, grading, answers, questions, choices, im_w, im_h):
    area_width = int(image.shape[1]/choices)
    area_hight = int(image.shape[0]/questions)

    for x in range(0, 8):
        ans = mark_indices[x]
        choice_x = (ans*area_width)+area_width//2
        choice_y = (x*area_hight)+area_hight//2

        if(grading[x] == 1):
            color = (0, 255, 0)
        else:
            color = (0, 0, 255)
            correct_ans = answers[x]

            cv2.circle(image, ((correct_ans*area_width)+area_width//2,
                               (x*area_hight)+area_hight//2), 20, (0, 255, 0), cv2.FILLED)

        cv2.circle(image, (choice_x, choice_y), 20, color, cv2.FILLED)
    image = cv2.resize(image, (im_w, im_h))
    return image


def get_images():
    arr = os.listdir('./input')
    return arr


def create_excel(student_id, name, surname, date_birth, faculty, marks):
    workbook = xlsxwriter.Workbook('./output/report.xlsx')
    worksheet = workbook.add_worksheet()

    row = 0
    col = 0

    worksheet.write(row, col, "Student ID")
    worksheet.write(row, col+1, "Name")
    worksheet.write(row, col+2, "Surname")
    worksheet.write(row, col+3, "Date of Birth")
    worksheet.write(row, col+4, "Faculty")
    worksheet.write(row, col+5, "Mark")

    row = 1

    x = 0
    while(x < len(student_id)):
        worksheet.write(row, col, student_id[x])
        worksheet.write(row, col+1, name[x])
        worksheet.write(row, col+2, surname[x])
        worksheet.write(row, col+3, date_birth[x])
        worksheet.write(row, col+4, faculty[x])
        worksheet.write(row, col+5, round(marks[x], 2))
        row += 1
        x += 1
    workbook.close()


def printProgressBar(count, total, suffix=''):

    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()
