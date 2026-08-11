from pathlib import Path
from dotenv import load_dotenv
from os import getenv
import re

PROJECT_DIRECTORY_PATH = Path(__file__).resolve().parent.parent.parent
DOTENV_STRING_PATH = str(PROJECT_DIRECTORY_PATH / ".env")

def get_data_api_key():
    load_dotenv(DOTENV_STRING_PATH)
    return getenv("DATA_API_KEY")

def sanitize_filename(value):
    value = str(value)
    value = re.sub(r'[<>:"/\\|?*]', "_", value)
    return value