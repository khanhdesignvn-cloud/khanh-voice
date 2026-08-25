"""Environment-based configuration for the Khanh Voice key-selling site."""

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = os.environ.get("DATABASE_PATH", str(DATA_DIR / "khanhvoice.db"))

# Public base URL of the deployed site, e.g. https://voice.example.com
# Used to build PayOS return/cancel URLs and to self-register the webhook.
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")

# Secret used to sign admin session cookies. MUST be overridden in production.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# Plaintext admin password (single admin). Override with a strong random value.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
ADMIN_SESSION_HOURS = int(os.environ.get("ADMIN_SESSION_HOURS", "12"))

# PayOS credentials — see https://payos.vn (merchant dashboard).
PAYOS_CLIENT_ID = os.environ.get("PAYOS_CLIENT_ID", "")
PAYOS_API_KEY = os.environ.get("PAYOS_API_KEY", "")
PAYOS_CHECKSUM_KEY = os.environ.get("PAYOS_CHECKSUM_KEY", "")

PAYOS_CONFIGURED = bool(PAYOS_CLIENT_ID and PAYOS_API_KEY and PAYOS_CHECKSUM_KEY)
