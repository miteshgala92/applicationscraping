from pytesseract import Output

try:
    from PIL import Image
except ImportError:
    import Image

import pytesseract
import re

def replace_chars(text):
    """
    Replaces all characters instead of numbers from 'text'.

    :param text: Text string to be filtered
    :return: Resulting number
    """
    list_of_numbers = re.findall(r'\d+', text)
    result_number = ''.join(list_of_numbers)
    return result_number


ocr_result = pytesseract.image_to_string(Image.open('../screenshots/price.png'), lang='eng', output_type=Output.STRING)
print(ocr_result)
print(replace_chars(ocr_result))