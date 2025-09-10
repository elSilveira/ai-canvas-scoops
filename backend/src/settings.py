import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
SRC_DIR = Path(__file__).resolve().parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_FILE = os.getenv("DB_FILE", SRC_DIR / "database" / "ingredients.db")
