"""Application settings and configuration.

Environment variables should be loaded before importing this module.
The .env file is loaded in src/app.py at application startup.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Application directories
SRC_DIR = Path(__file__).resolve().parent

# dotenv directory
DOTENV_PATH = SRC_DIR.parent / ".env"

load_dotenv(DOTENV_PATH)

# API Keys - loaded from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STABILITY_AI_KEY = os.getenv("STABILITY_AI_KEY")

# Server configuration
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = os.getenv("SERVER_PORT", "8000")
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Database configuration
DB_FILE = os.getenv("DB_FILE", SRC_DIR / "database" / "ingredients.db")

# Debug flag for development
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
