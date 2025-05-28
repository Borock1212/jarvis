import os
import pyautogui
import pytesseract
from PIL import Image, ImageOps, ImageFilter

pytesseract.pytesseract.tesseract_cmd = r"C:\\Users\\Boroc\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\\Users\\Boroc\\AppData\\Local\\Programs\\Tesseract-OCR\\tessdata"

def read_screen_text():
    """
    Captures a screenshot of the entire screen, preprocesses it to enhance text recognition,
    and returns the extracted text using Tesseract OCR.

    Returns:
        str: Recognized text from the screen, or error message if failed.
    """
    def preprocess_image(img):
        """
        Preprocesses the image for better OCR results:
        - Converts to grayscale
        - Inverts colors (useful if background is dark)
        - Applies median filter to reduce noise
        - Applies binary thresholding to enhance contrast
        """
        img = img.convert('L')  # convert to grayscale
        img = ImageOps.invert(img)  # invert colors if background is dark
        img = img.filter(ImageFilter.MedianFilter())  # reduce noise
        img = img.point(lambda x: 0 if x < 140 else 255, '1')  # binary thresholding
        return img

    try:
        temp_path = os.path.join(os.getcwd(), "screen_for_read.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(temp_path)

        # Open and preprocess the image before OCR
        img = Image.open(temp_path)
        img = preprocess_image(img)

        # Pass preprocessed image to Tesseract OCR engine
        text = pytesseract.image_to_string(img, lang="rus+eng")
        return text
    except Exception as e:
        return f"Screen reading error: {e}"
