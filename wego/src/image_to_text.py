import cv2
import pytesseract
import easyocr
from PIL import Image
import re

from pytesseract import Output


def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))


#detect_text('test1.png')

reader = easyocr.Reader(['en'])
output = reader.readtext('../screenshots/price 3.png')
print(output[-1][1])
temp = re.findall(r'\d+', output[-1][1])
print(temp)

'''
img = cv2.imread('price.png')
#img = Image.open('test1.png')
pytesseract.pytesseract.tesseract_cmd ='/usr/local/Cellar/tesseract/4.1.1/bin/tesseract'
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


#cv2.imshow('threshold image', threshold_img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
#custom_config = r'--oem 3 --psm 6'
#details = pytesseract.image_to_data(threshold_img,output_type=Output.DICT, config=custom_config, lang='eng')
img = cv2.imread('price.png')
text = pytesseract.image_to_string(img)
print(text)


# print(details)

total_boxes = len(details['text'])
for sequence_number in range(total_boxes):
    if int(details['conf'][sequence_number]) > 30:
        (x, y, w, h) = (
        details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number],
        details['height'][sequence_number])
        threshold_img = cv2.rectangle(threshold_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

text = pytesseract.image_to_data(threshold_img)
print(text)
cv2.imshow('captured text', threshold_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

'''