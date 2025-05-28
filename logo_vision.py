import os

from config import GOOGLE_VISION_KEY_PATH

# Before making any calls to Google Vision API,
# set the environment variable with the path to your service account key.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_VISION_KEY_PATH

from google.cloud import vision

def detect_logo(path_to_image):
    """
    Detects the most prominent logo in the given image file using Google Vision API.

    Args:
        path_to_image (str): The file path to the image to analyze.

    Returns:
        tuple: (logo_description (str), confidence_score (float))
               Returns (None, None) if no logo is detected.
    """
    # Initialize the Vision API client
    client = vision.ImageAnnotatorClient()
    # Read the image file
    with open(path_to_image, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # Perform logo detection
    response = client.logo_detection(image=image)
    logos = response.logo_annotations

    if logos:
        best_logo = logos[0]
        # Return logo description and confidence score
        return best_logo.description, best_logo.score
    else:
        # No logos found in the image
        return None, None