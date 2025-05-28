import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Email credentials for mail processing
EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")

# API keys for various services
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Path to Google Vision API service account JSON key file
GOOGLE_VISION_KEY_PATH = os.getenv("GOOGLE_VISION_KEY_PATH")

# API key for Google Knowledge Graph Search API
GOOGLE_KG_SEARCH_API= os.getenv("GOOGLE_KG_SEARCH_API")