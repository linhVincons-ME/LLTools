import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = APP_DIR / "data"
STATIC_DIR = APP_DIR / "static"

# Database Configuration
DATABASE_PATH = BASE_DIR / "lltools.db"

# Server Configuration
HOST = os.getenv("LLTOOLS_HOST", "127.0.0.1")
PORT = int(os.getenv("LLTOOLS_PORT", "8000"))
DEBUG = os.getenv("LLTOOLS_DEBUG", "True").lower() in ("true", "1", "yes")

# Spaced Repetition (SM-2) Default Parameters
DEFAULT_EASE_FACTOR = 2.5
MIN_EASE_FACTOR = 1.3
INTERVAL_STEP_1 = 1  # 1 day
INTERVAL_STEP_2 = 6  # 6 days
