import cv2
from PIL import Image

from image_preprocessing.remove_noise import process_image_for_ocr
from tesseract_interface import pytesser

THRESHOLD_FOR_INVERTED_IMAGE = 128
import tempfile


def image_process_extract_string(mask, x, y, w, h):
    temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
    temp_filename = temp_file.name
    im = mask[y:y + h, x:x + w]
    cv2.imwrite(temp_filename, im)
    size = 2 * w, 2 * h
    im = Image.open(temp_filename)
    im_resized = im.resize(size, Image.ANTIALIAS)
    im_resized.save(temp_filename, dpi=(300, 300))
    return pytesser.image_to_string(temp_filename, 6)


def extract_image_text(image):
    boxed_image = image.copy()
    img = image.copy()
    img2gray = img
    inv_img = (255 - img2gray)
    contours = contour_plot_on_text(inv_img)
    complete_image_text = read_contours_text(boxed_image, contours, img)
    cv2.imwrite('boxed_image.jpg', boxed_image)
    return complete_image_text


def read_contours_text(boxed_image, contours, img):
    image_text_dict = {}
    """store on the location where it is located in the image. here it will be top-left pixel location as the key"""
    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)

        # draw rectangle around contour on original image
        if w < 20 or h < 20 or (w > 500 and h > 500):
            continue

        cv2.rectangle(boxed_image, (x, y), (x + w + 10, y + h + 10), thickness=2, color=0)

        box_read = image_process_extract_string(img, x, y, w, h)
        box_read = box_read.strip()
        image_text_dict[(x, y)] = box_read

    list_of_text = []
    for key, value in sorted(image_text_dict.items()):
        print('key , value) : ', key, value)
        list_of_text.append(value)
    return '\n'.join(list_of_text).strip()


def contour_plot_on_text(inv_img):
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 2))
    dilated = cv2.dilate(inv_img, kernel, iterations=10)  # dilate
    _, contours, hierarchy = cv2.findContours(
        dilated,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE)  # get contours
    return contours


def main(file_path):
    image = process_image_for_ocr(file_path)
    image_text = extract_image_text(image)
    print('extract_image_text text :\n', image_text)
    return image_text


image_path = '/Users/Amit/Desktop/data_cleaning/51d518c25e2153da53439668dd6b3590.jpg'
main(image_path)