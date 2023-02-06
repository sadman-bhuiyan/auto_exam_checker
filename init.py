import script
import utility
import os
import time

for f in os.listdir('./output'):
    os.remove(os.path.join('./output', f))

list_of_images = utility.get_images()

students_data = []


i = 0
utility.printProgressBar(i, len(list_of_images), suffix='complete')
for image_path in list_of_images:
    i += 1
    student_data = script.start_task(f'input/{image_path}')
    time.sleep(0.1)
    utility.printProgressBar(i, len(list_of_images), suffix='complete')

    students_data.append(student_data)

student_ids = []
names = []
surnames = []
date_births = []
faculties = []
marks = []

for s in students_data:
    student_ids.append(s['student_id'])
    names.append(s['name'])
    surnames.append(s['surname'])
    date_births.append(s['date_of_birth'])
    faculties.append(s['faculty'])
    marks.append(s['mark'])


utility.create_excel(student_ids, names, surnames,
                     date_births, faculties, marks)
print(" ")
print("Thank you! bye")
