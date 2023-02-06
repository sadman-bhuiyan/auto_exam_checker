import cv2
import numpy as np
import utility
import barcode
import ocr


def start_task(image_path):

    answers = [0, 2, 1, 2, 0, 3, 0, 3]
    written_answers = ['TALENTED', 'REPORT', 'FIRE', 'PARADISE',
                       'ROOF', 'TEA', 'SAFARITRUCK', 'NEEDLE', 'ORANGE']

    image = cv2.imread(image_path)
    image_height = image.shape[0]
    image_width = image.shape[1]
    image = cv2.resize(image, (image_width, image_height))
    image_contours = image.copy()
    final_image = image.copy()
    image_part1_area = image.copy()
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_blur = cv2.GaussianBlur(image_gray, (5, 5), 1)
    t = cv2.threshold(image_blur, 200, 255, cv2.THRESH_BINARY_INV)[1]
    image_canny = cv2.Canny(t, 30, 50)

    contours, hierarchy = cv2.findContours(
        image_canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(image_contours, contours, -1, (0, 255, 0), 8)

    found_areas = utility.find_areas(contours)

    part1_area = utility.find_corner_points(found_areas[2])
    qrCode_area = utility.find_corner_points(found_areas[6])
    part2_area = utility.find_corner_points(found_areas[0])

    grade_area = utility.find_corner_points(found_areas[28])

    if part1_area.size != 0:
        cv2.drawContours(image_part1_area, part2_area, -1, (0, 255, 0), 8)
        cv2.drawContours(image_part1_area, part1_area, -1, (255, 0, 0), 8)
        cv2.drawContours(image_part1_area, grade_area, -1, (0, 0, 255), 8)

        part1_area = utility.reorder(part1_area)
        part2_area = utility.reorder(part2_area)
        grade_area = utility.reorder(grade_area)
        qrCode_area = utility.reorder(qrCode_area)

        # QR PART

        pointOne_QRCODE = np.float32(qrCode_area)
        pointTwo_QRCODE = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])

        matrix_QRCODE = cv2.getPerspectiveTransform(
            pointOne_QRCODE, pointTwo_QRCODE)

        image_QRCODE = cv2.warpPerspective(
            final_image, matrix_QRCODE, (300, 300))

        # GRADE PART

        pointOne_grade_area = np.float32(grade_area)
        pointTwo_grade_area = np.float32(
            [[0, 0], [300, 0], [0, 150], [300, 150]])

        matrix_grade_area = cv2.getPerspectiveTransform(
            pointOne_grade_area, pointTwo_grade_area)

        image_grade_area = cv2.warpPerspective(
            image, matrix_grade_area, (300, 150))

        # MCQ PART
        pointOne_part1 = np.float32(part1_area)
        pointTwo_part1 = np.float32(
            [[0, 0], [image_width, 0], [0, image_height], [image_width, image_height]])

        matrix_part1 = cv2.getPerspectiveTransform(
            pointOne_part1, pointTwo_part1)

        image_warp_original_part1 = cv2.warpPerspective(
            image, matrix_part1, (image_width, image_height))

        # LETTER PART
        pointOne_part2 = np.float32(part2_area)
        pointTwo_part2 = np.float32(
            [[0, 0], [image_width, 0], [0, image_height], [image_width, image_height]])

        matrix_part2 = cv2.getPerspectiveTransform(
            pointOne_part2, pointTwo_part2)

        image_warp_original_part2 = cv2.warpPerspective(
            image, matrix_part2, (image_width, image_height))

        image_warp_original_part2 = cv2.resize(
            image_warp_original_part2, (900, 900))

        student_written_answers = utility.get_written_answers(
            image_warp_original_part2)

        image_warp_gray_part1 = cv2.cvtColor(
            image_warp_original_part1, cv2.COLOR_BGR2GRAY)
        image_threshold_part1 = cv2.threshold(
            image_warp_gray_part1, 150, 255, cv2.THRESH_BINARY_INV)[1]
        image_threshold_part1 = cv2.resize(image_threshold_part1, (1000, 1000))

        rectangles = utility.split_rectangles(image_threshold_part1)

        px_values = np.zeros((8, 4))
        count_cols = 0
        count_rows = 0
        for image in rectangles:
            totalpx = cv2.countNonZero(image)
            px_values[count_rows][count_cols] = totalpx
            count_cols += 1
            if(count_cols == 4):
                count_rows += 1
                count_cols = 0

        marked_indices = []

        for m in range(0, 8):
            array = px_values[m]
            maximum = np.where(array == np.amax(array))
            marked_indices.append(maximum[0][0])

        grading = []
        x = 0

        while x < 8:
            if(answers[x] == marked_indices[x]):
                grading.append(1)
            else:
                grading.append(0)
            x += 1

        # SHOW ANSWER
        results_image_part1 = image_warp_original_part1.copy()
        results_image_part1 = utility.correct_answers(
            results_image_part1, marked_indices, grading, answers, 8, 4, image_width, image_height)

        raw_results_image_part1 = np.zeros_like(image_warp_original_part1)
        raw_results_image_part1 = utility.correct_answers(
            raw_results_image_part1, marked_indices, grading, answers, 8, 4, image_width, image_height)

        inverse_matrix_part1 = cv2.getPerspectiveTransform(
            pointTwo_part1, pointOne_part1)
        inverse_results_image_part1 = cv2.warpPerspective(
            raw_results_image_part1, inverse_matrix_part1, (image_width, image_height))
        x = 0
        while x < 9:
            if(student_written_answers[x] == written_answers[x]):
                grading.append(1)
            else:
                grading.append(0)
            x += 1
        mark = (sum(grading)/17)*100

        raw_grade_image = np.zeros_like(image_grade_area)
        if(mark < 60):
            mark_color = (0, 0, 255)
        else:
            mark_color = (0, 255, 0)
        cv2.putText(raw_grade_image, str(int(mark)), (50, 100),
                    cv2.FONT_HERSHEY_COMPLEX, 3, mark_color, 10)
        inverse_matrix_grade = cv2.getPerspectiveTransform(
            pointTwo_grade_area, pointOne_grade_area)
        inverse_results_image_grade = cv2.warpPerspective(
            raw_grade_image, inverse_matrix_grade, (image_width, image_height))

        final_image = cv2.addWeighted(
            final_image, 0.8, inverse_results_image_part1, 1, 0)
        final_image = cv2.addWeighted(
            final_image, 0.8, inverse_results_image_grade, 1, 0)
        student_data = barcode.read_barcode(image_QRCODE, mark)

        file_name = student_data['student_id']

        cv2.imwrite(f'output/{file_name}.jpg', final_image)
        with open("output/student_written_answers.txt", "a") as f:
            f.write(f'{file_name}={student_written_answers}')
            f.write("\n")
            f.close()

        return student_data
