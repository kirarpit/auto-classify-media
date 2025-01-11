import logging
import os
from dotenv import load_dotenv


load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

WATCH_FOLDER = os.getenv("WATCH_FOLDER")
PUID = os.getenv("PUID", "")
PGID = os.getenv("PGID", "")
MOVIES_FOLDER = os.getenv("MOVIES_FOLDER")
SHOWS_FOLDER = os.getenv("SHOWS_FOLDER")
AUDIOBOOKS_FOLDER = os.getenv("AUDIOBOOKS_FOLDER")
EBOOKS_FOLDER = os.getenv("EBOOKS_FOLDER")
KINDLE_EMAIL = os.getenv("KINDLE_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")
FROM_EMAIL_PASSWORD = os.getenv("FROM_EMAIL_PASSWORD")

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    logging.error(
        "API key for Generative AI is not set. Please configure GENAI_API_KEY."
    )
    exit(1)
