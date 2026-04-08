"""
config.py — Load all secrets and settings from .env file.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


def _require(var_name: str) -> str:
    """Return an env var or exit with a descriptive error."""
    value = os.getenv(var_name)
    if not value:
        print(f"[CONFIG ERROR] Required environment variable '{var_name}' is missing. "
              f"Copy .env.example → .env and fill in all values.")
        sys.exit(1)
    return value


# ── YouTube OAuth ──────────────────────────────────────────────
YOUTUBE_CLIENT_SECRET_FILE: str = os.getenv(
    "YOUTUBE_CLIENT_SECRET_FILE", "client_secret.json"
)

# ── Processing defaults ───────────────────────────────────────
OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
NUM_CLIPS: int = int(os.getenv("NUM_CLIPS", "5"))
MAX_CLIP_DURATION: int = int(os.getenv("MAX_CLIP_DURATION", "59"))

# ── Retry / backoff ──────────────────────────────────────────
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BASE_DELAY: float = float(os.getenv("RETRY_BASE_DELAY", "2.0"))


def validate_youtube_config() -> None:
    """Ensure YouTube-related config is present."""
    if not Path(YOUTUBE_CLIENT_SECRET_FILE).exists():
        print(
            f"[CONFIG ERROR] YouTube client secret file '{YOUTUBE_CLIENT_SECRET_FILE}' "
            f"not found. Download it from Google Cloud Console."
        )
        sys.exit(1)
