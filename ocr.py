from google.cloud import vision
import io
import os


def image_reader(image):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'My First Project-9f751f111f95.json'
    client = vision.ImageAnnotatorClient()

    with io.open(image, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)

    txt = response.full_text_annotation.text

    return txt.replace(" ", "")
